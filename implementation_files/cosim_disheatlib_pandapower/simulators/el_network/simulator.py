# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by LGPL-2.1.
'''
This is a modified version of the Mosaik Pandapower module.
'''

import json
import os.path

import pandas as pd
import pandapower as pp
from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapower.control import ConstControl
from pandapower.timeseries.run_time_series import run_time_step, init_time_series

class Pandapower(object):

    def __init__(self):
        self.entity_map={}


    def load_case(self,path,grid_idx):
        '''
        Loads a pandapower network, the network should be ready in a separate json or excel file
        TODO: pypower converter and network building with only parameter as input
        '''
        loaders = {
          '.json': 1,
          '.xlsx': 2,
          # '': 3
          }

        try:
           ext = os.path.splitext(path)[-1]
           loader = loaders[ext]
        except KeyError:
            raise ValueError('Don\'t know how to open "{}"'.format(path))

        if loader == 1:
            self.net = pp.from_json(path)
        elif loader == 2:
            self.net = pp.from_excel(path)

        self.bus_id = self.net.bus.name.to_dict()

        # #create virtual loads and gens on each bus ready to be plugged in
        # for i in self.bus_id:
         # if self.net.ext_grid.bus[0] != i:
            # pp.create_load(self.net, i, p_mw=0, name=('ext_load_%s' % i))
            # pp.create_sgen(self.net, i, p_mw=0, name=('ext_gen_%s' % i))

        #create elements indices, to create entities
        self.load_id = self.net.load.name.to_dict()
        self.sgen_id = self.net.sgen.name.to_dict()
        self.line_id = self.net.line.name.to_dict()
        self.trafo_id = self.net.trafo.name.to_dict()
        self.switch_id = self.net.switch.name.to_dict()

        #load the entity map
        self._get_slack(grid_idx)
        self._get_buses(grid_idx)
        self._get_lines(grid_idx)
        self._get_trafos(grid_idx)
        self._get_loads(grid_idx)
        self._get_sgen(grid_idx)

        entity_map = self.entity_map
        ppc = self.net #pandapower case

        if 'profiles' in self.net:
            time_steps = range(0, len(self.net.profiles['load']))
            output_dir = os.path.join(os.getcwd(), 'time_series_example')
            ow = create_output_writer(self.net, time_steps, output_dir)  # just created to update res_bus in each time step
            self.ts_variables = init_time_series(self.net, time_steps)
        else:
            pass

        return  ppc, entity_map


    def _get_slack(self, grid_idx):
        '''Create entity of the slack bus'''

        self.slack_bus_idx = self.net.ext_grid.bus[0]
        bid = self.bus_id[self.slack_bus_idx]
        eid = make_eid(bid, grid_idx)

        self.entity_map[eid] = {
                'etype': 'Ext_grid',
                'idx': self.slack_bus_idx,
                'static': {'vm_pu': self.net.ext_grid['vm_pu'],
                           'va_degree': self.net.ext_grid['va_degree']
                }
        }
        slack = (0, self.slack_bus_idx)

        return slack


    def _get_buses(self,grid_idx):
        '''Create entities of the buses'''
        buses = []

        for idx in self.bus_id:
         if self.slack_bus_idx != idx:
            element = self.net.bus.iloc[idx]
            bid = element['name']
            eid = make_eid(bid, grid_idx)
            buses.append((idx, element['vn_kv']))
            #etype = bid
            self.entity_map[eid] = {
                'etype': 'Bus',
                'idx': idx,
                'static': {
                    'vn_kv':  element['vn_kv']
                },
            }
         else:
             pass

        return buses


    def _get_loads(self, grid_idx):
        '''Create load entities'''
        loads = []

        for idx in self.load_id:
                element = self.net.load.iloc[idx]
                eid = make_eid(element['name'], grid_idx)
                bid = make_eid(self.bus_id[element['bus']], grid_idx)

                element_data = element.to_dict()
                keys_to_del = ['name', 'const_z_percent', 'const_i_percent', 'min_q_mvar', 'min_p_mw', 'max_q_mvar'
                    , 'max_p_mw']
                element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}

                # time series calculation
                if 'profile' in element_data_static:
                    if type (element_data_static ['profile']) != float:
                       profile_name = element_data_static['profile']

                       datasource = pd.DataFrame()
                       datasource[profile_name+'_pload'] = self.net.profiles['load'][profile_name+'_pload']*element['p_mw']
                       datasource[profile_name +'_qload'] = self.net.profiles['load'][profile_name+'_qload']* element['q_mvar']

                       ds = DFData(datasource)

                       ConstControl(self.net, element='load', variable='p_mw', element_index=idx,
                                 data_source=ds, profile_name=profile_name+'_pload')

                       ConstControl(self.net, element='load', variable='q_mvar', element_index=idx,
                                 data_source=ds, profile_name=profile_name+'_qload')
                    else:
                        pass
                else:
                    pass

                self.entity_map[eid] = {'etype': 'Load', 'idx': idx, 'static': element_data_static
                    , 'related': [bid]}

                loads.append((bid, element['p_mw'], element['q_mvar'], element['scaling']
                              , element['in_service']))

        return loads


    def _get_sgen(self, grid_idx):
        '''Create static generator entities'''
        sgens = []

        for idx in self.sgen_id:
             element = self.net.sgen.iloc[idx]
             eid = make_eid(element['name'], grid_idx)
             bid = make_eid(self.bus_id[element['bus']], grid_idx)

             element_data = element.to_dict()
             keys_to_del = ['name', 'min_q_mvar', 'min_p_mw', 'max_q_mvar', 'max_p_mw']
             element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}

             # time series calculation
             if 'profile' in element_data_static:
                 if type(element_data_static['profile']) != float:
                     profile_name = element_data_static['profile']

                     datasource = pd.DataFrame()
                     datasource[profile_name ] = self.net.profiles['renewables'][profile_name ] * element['p_mw']

                     ds = DFData(datasource)

                     ConstControl(self.net, element='sgen', variable='p_mw', element_index=idx
                                  , data_source=ds, profile_name=profile_name )
                 else:
                   pass
             else:
                 pass

             self.entity_map[eid] = {'etype': 'Sgen', 'idx': idx, 'static': element_data_static
                 , 'related': [bid]}

             sgens.append((bid, element['p_mw'], element['q_mvar'], element['scaling']
                           , element['in_service']))

        return sgens


    def _get_lines(self, grid_idx):
        '''create branches entities'''
        lines = []

        for idx in self.line_id:
            element = self.net.line.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            fbus = make_eid(self.bus_id[element['from_bus']], grid_idx)
            tbus = make_eid(self.bus_id[element['to_bus']], grid_idx)

            f_idx = self.entity_map[fbus]['idx']
            t_idx = self.entity_map[tbus]['idx']

            element_data= element.to_dict()
            keys_to_del = ['name', 'from_bus', 'to_bus']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del }
            #del element_data_static

            self.entity_map[eid] = {'etype': 'Line', 'idx': idx, 'static': element_data_static
                , 'related': [fbus, tbus]}

            lines.append((f_idx, t_idx, element['length_km'], element['r_ohm_per_km'], element['x_ohm_per_km'],
                         element['c_nf_per_km'], element['max_i_ka'], element['in_service']))

        return lines


    def _get_trafos(self, grid_idx):
        '''Create tranformer entities'''
        trafos = []

        if 0 == len(self.trafo_id):
            return trafos

        for idx in self.trafo_id:
            element = self.net.trafo.iloc[idx]
            eid = make_eid(element['name'], grid_idx)
            hv_bus = make_eid(self.bus_id[element['hv_bus']], grid_idx)
            lv_bus = make_eid(self.bus_id[element['lv_bus']], grid_idx)


            hv_idx = self.entity_map[hv_bus]['idx']
            lv_idx = self.entity_map[lv_bus]['idx']

            element_data = element.to_dict()
            keys_to_del = ['name', 'hv_bus', 'lv_bus']
            element_data_static = {key: element_data[key] for key in element_data if key not in keys_to_del}
            # del element_data_static

            self.entity_map[eid] = {'etype': 'Transformer', 'idx': idx, 'static': element_data_static
                , 'related': [hv_bus, lv_bus]}

        trafos.append((hv_idx, lv_idx, element['sn_mva'], element['vn_hv_kv'], element['vn_lv_kv']
                       , element['vk_percent'], element['vkr_percent'], element['pfe_kw'], element['i0_percent']
                       , element['shift_degree'], element['tap_side'], element['tap_pos'], element['tap_neutral']
                       , element['tap_min'], element['tap_max'], element['in_service']))

        return trafos


    def set_inputs(self, etype, idx, data, static):
        '''setting the input from other simulators'''

        name = list(data.keys())[0]
        value = list(data.values())[0]

        if etype == 'Load':
           if name == 'p_mw':
              self.net.load.at[idx, 'p_mw'] = value
           elif name == 'q_mvar':
              self.net.load.at[idx, 'q_mvar'] = value
           elif name == 'in_service':
              self.net.load.at[idx, 'in_service'] = value
           else :
              self.net.load.at[idx, 'controllable'] = value

        elif etype == 'Sgen':

            if name == 'p_mw':
                self.net.sgen.at[idx, 'p_mw'] = value
            elif name == 'q_mvar':
                self.net.sgen.at[idx, 'q_mvar'] = value
            elif name == 'in_service':
                self.net.sgen.at[idx, 'in_service'] = value
            elif name == 'va_degree':
                self.net.sgen.at[idx, 'va_degree'] = value
            else:
                self.net.sgen.at[idx, 'controllable'] = value

        elif etype == 'Transformer':
            if 'tap_turn' in data:
                tap = 1 / static['tap_pos'][data['tap_turn']]
                self.net.trafo.at[idx, 'tap_pos'] = tap #TODO: acces number of transformers

        else:
            raise ValueError('etype %s unknown' % etype)


    def powerflow(self):
        '''Conduct power flow'''
        pp.runpp(self.net)


    def powerflow_timeseries(self, time_step):
        '''Conduct power flow series'''

        run_time_step(self.net, time_step, self.ts_variables, _ppc=True, is_elements=True)


    def get_cache_entries(self):
        '''cache the results of the power flow to be communicated to other simulators'''

        cache = {}
        case = self.net

        for eid, attrs in self.entity_map.items():
            etype = attrs['etype']
            idx = attrs['idx']
            data = {}

            if not case.res_bus.empty:

                if etype == 'Bus':
                    bus = case.res_bus.iloc[idx]
                    data['p_mw'] = bus['p_mw']
                    data['q_mvar'] = bus['q_mvar']
                    data['vm_pu'] = bus['vm_pu']
                    data['va_degree'] = bus['va_degree']

                elif etype == 'Load':
                    load = case.res_load.iloc[idx]
                    data['p_mw'] = load['p_mw']
                    data['q_mvar'] = load['q_mvar']

                elif etype == 'Sgen':
                    sgen = case.res_sgen.iloc[idx]
                    data['p_mw'] = sgen['p_mw']
                    data['q_mvar'] = sgen['q_mvar']

                elif etype == 'Transformer':
                    trafo = case.res_trafo.iloc[idx]
                    data['va_lv_degree'] = trafo['va_lv_degree']
                    data['loading_percent'] = trafo['loading_percent']

                elif etype == 'Line':
                    line = case.res_line.iloc[idx]
                    data['i_ka'] = line['i_ka']
                    data['loading_percent'] = line ['loading_percent']

                else:
                    slack = case.res_ext_grid
                    data['p_mw'] = slack['p_mw']
                    data['q_mvar'] = slack['q_mvar']

            else:
                # Failed to converge.
                if etype in 'Bus':
                    data['p_mw'] = float('nan')
                    data['q_mvar'] = float('nan')
                    data['vm_pu'] = float('nan')
                    data['va_degree'] = float('nan')
                elif etype in 'Line':
                    data['i_ka'] = float('nan')
                    data['p_from_mw'] = float('nan')
                    data['q_from_mvar'] = float('nan')
                    data['p_to_mw'] = float('nan')
                    data['q_to_mvar'] = float('nan')
                elif etype in 'Transformer':
                    data['va_lv_degree'] = float('nan')
                    data['loading_percent'] = float('nan')

            cache[eid] = data
        return cache


def make_eid(name, grid_idx):
    return '%s_%s' % (name, grid_idx)


def create_output_writer(net, time_steps, output_dir):
    '''Pandapower output to save results'''
    ow = OutputWriter(net, time_steps, output_path=output_dir, output_file_type='.xls')
    # these variables are saved to the harddisk after / during the time series loop
    ow.log_variable('res_load', 'p_mw')
    ow.log_variable('res_load', 'q_mvar')
    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('res_bus', 'q_mvar')
    ow.log_variable('res_bus', 'va_degree')
    ow.log_variable('res_bus', 'p_mw')
    ow.log_variable('res_line', 'loading_percent')
    ow.log_variable('res_line', 'i_ka')
    ow.log_variable('res_trafo', 'va_lv_degree')
    ow.log_variable('res_trafo', 'loading_percent')
    ow.log_variable('res_sgen', 'p_mw')
    ow.log_variable('res_sgen', 'q_mvar')

    return ow

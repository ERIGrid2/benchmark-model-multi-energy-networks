# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by LGPL-2.1.
'''
This is a modified version of the Mosaik Pandapower module.
'''

import logging
import os
import mosaik_api

from .simulator import Pandapower, make_eid

logger = logging.getLogger('pandapower.mosaik')

META = {
    'models': {
        'Grid': {
            'public': True,
            'params': [
                'gridfile',  # Name of the file containing the grid topology.
                'sheetnames',  # Mapping of Excel sheet names, optional.
            ],
            'attrs': [],
        },
        'Ext_grid': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # load Active power [MW]
                'q_mvar',   # Reactive power [MVAr]
            ],

        },
        'Bus': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # load Active power [MW]
                'q_mvar',   # Reactive power [MVAr]
                'vn_kv',  # Nominal bus voltage [KV]
                'vm_pu',  # Voltage magnitude [p.u]
                'va_degree',  # Voltage angle [deg]
            ],
        },
        'Load': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # load Active power [MW]
                'q_mvar',   # Reactive power [MVAr]
                'in_service',  # specifies if the load is in service.
                'controllable',  # States if load is controllable or not.
            ],
        },
        'Sgen': {
            'public': False,
            'params': [],
            'attrs': [
                'p_mw',   # load Active power [MW]
                'q_mvar',   # Reactive power [MVAr]
                'in_service',  # specifies if the load is in service.
                'controllable',  # States if load is controllable or not.
                'va_degree',  # Voltage angle [deg]
            ],
        },
        'Transformer': {
            'public': False,
            'params': [],
            'attrs': [
                'p_hv_mw',    # Active power at "from" side [MW]
                'q_hv_mvar',    # Reactive power at "from" side [MVAr]
                'p_lv_mw',      # Active power at "to" side [MW]
                'q_lv_mvar',      # Reactive power at "to" side [MVAr]
                'sn_mva',       # Rated apparent power [MVA]
                'max_loading_percent',   # Maximum Loading
                'vn_hv_kv',       # Nominal primary voltage [kV]
                'vn_lv_kv',       # Nominal secondary voltage [kV]
                'pl_mw',       # Active power loss [MW]
                'ql_mvar',       # reactive power consumption of the transformer [Mvar]
                #'pfe_kw',       #  iron losses in kW [kW]
                #'i0_percent',       #  iron losses in kW [kW]
                'loading_percent',       # load utilization relative to rated power [%
                'i_hv_ka',       # current at the high voltage side of the transformer [kA]
                'i_lv_ka',       # current at the low voltage side of the transformer [kA]
                'tap_max',      # maximum possible  tap turns
                'tap_min',      # minimum possible tap turns
                'tap_pos',  # Currently active tap turn
            ],
        },
        'Line': {
            'public': False,
            'params': [],
            'attrs': [
                'p_from_mw',    # Active power at "from" side [MW]
                'q_from_mvar',    # Reactive power at "from" side [MVAr]
                'p_to_mw',      # Active power at "to" side [MW]
                'q_to_mvar',      # Reactive power at "to" side [MVAr]
                'max_i_ka',     # Maximum current [KA]
                'length_km',    # Line length [km]
                'pl_mw',    # active power losses of the line [MW]
                'ql_mvar',    # reactive power consumption of the line [MVar]
                'i_from_ka',    # Current at from bus [kA]
                'i_to_ka',    # Current at to bus [kA]
                'loading_percent',    #line loading [%]
                'r_ohm_per_km',  # Resistance per unit length [Ω/km]
                'x_ohm_per_km',  # Reactance per unit length [Ω/km]
                'c_nf_per_km',   # Capactity per unit length [nF/km]
                'in_service',    # Boolean flag (True|False)
            ],
        },
    },
}


class ElectricNetworkSimulator(mosaik_api.Simulator):
    def __init__(self):
        super(ElectricNetworkSimulator, self).__init__(META)
        self.step_size = None
        self.simulator=Pandapower()
        self.time_step_index=0
        #There are three elements that have power values based on the generator
        #  viewpoint (positive active power means power consumption), which are:
        #gen ,sgen, ext_grid
        #For all other bus elements the signing is based on the consumer viewpoint
        # (positive active power means power consumption):bus, load

        self._entities = {}
        self._relations = []  # List of pair-wise related entities (IDs)
        self._ppcs = []  # The pandapower cases
        self._cache = {}  # Cache for load flow outputs

    def init(self, sid, step_size, mode, pos_loads=True):
        #TODO: check if we need to change signs or we leave it
        logger.debug('Power flow will be computed every %d seconds.' %
                     step_size)
        #signs = ('positive', 'negative')
        #logger.debug('Loads will be %s numbers, feed-in %s numbers.' %
         #            signs if pos_loads else tuple(reversed(signs)))

        self.step_size = step_size
        self.mode = mode

        return self.meta

    def create(self, num, modelname, gridfile, sheetnames=None):
        if modelname != 'Grid':
            raise ValueError('Unknown model: "%s"' % modelname)
        if not sheetnames:
            sheetnames = {}

        grids = []
        for i in range(num):
            grid_idx = len(self._ppcs)
            ppc, entities = self.simulator.load_case(gridfile,grid_idx)
            self._ppcs.append(ppc)

            children = []
            for eid, attrs in sorted(entities.items()):
                assert eid not in self._entities
                self._entities[eid] = attrs

                # We'll only add relations from line to nodes (and not from
                # nodes to lines) because this is sufficient for mosaik to
                # build the entity graph.
                relations = []
                if attrs['etype'] in ['Transformer', 'Line','Load','Sgen']:
                    relations = attrs['related']

                children.append({
                    'eid': eid,
                    'type': attrs['etype'],
                    'rel': relations,
                })

            grids.append({
                'eid': make_eid('grid', grid_idx),
                'type': 'Grid',
                'rel': [],
                'children': children,
            })

        return grids

    def step(self, time, inputs):

        for eid, attrs in inputs.items():
            idx = self._entities[eid]['idx']
            etype = self._entities[eid]['etype']
            static = self._entities[eid]['static']
            for name, values in attrs.items():
                attrs[name] = sum(float(v) for v in values.values())
                if name == 'P':
                    attrs[name] *= self.pos_loads

            self.simulator.set_inputs(etype, idx, attrs, static,)

        if self.mode == 'pf_timeseries' and not bool(inputs):
            self.simulator.powerflow_timeseries(self.time_step_index)
        elif self.mode == 'pf':
            self.simulator.powerflow()

        self._cache = self.simulator.get_cache_entries()

        self.time_step_index +=1
        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            for attr in attrs:
                try:
                    val = self._cache[eid][attr]
                    if attr == 'P':
                        val *= self.pos_loads
                except KeyError:
                    val = self._entities[eid]['static'][attr]
                data.setdefault(eid, {})[attr] = val

        return data

def main():
    mosaik_api.start_simulation(ElectricNetworkSimulator(), 'The mosaik pandapower adapter')

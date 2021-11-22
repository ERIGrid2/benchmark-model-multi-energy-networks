# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import sys
import math
from dataclasses import dataclass, field
from typing import Dict
import pandas as pd
import numpy as np
import pandapipes as pp
import pandapipes.control.run_control as run_control
from .valve_control import CtrlValve
# import matplotlib.pyplot as plt
# import pandapipes.plotting as plot

if not sys.warnoptions:
    import warnings

# Global
# OUTPUT_PLOTTING_PERIOD = 60 * 60 * 4 - 60

@dataclass
class DHNetwork:
    '''
    Pandapipes district heating network model.
    '''

    # Parameters
    T_amb: float = 8  # Ambient ground temperature [degC]
    enable_logging: bool = True  # enable power flow logging
    T_supply_grid: float = 75  # Supply temperature of the external grid [degC]
    P_grid_bar: float = 6  # Pressure of the external grid [bar]
    P_hp_bar: float = 6  # Pressure of the heat pump + storage unit [bar]
    tank_installed: bool = True  # Enable hp + tank connection point
    dynamic_temp_flow_enabled: bool = True  # Enable external temperature flow sim incl. network inertia

    # Magnitudes
    CP_WATER: float = 4186  # Specific heat capacity of water [J/(kgK)]

    # Input
    Qdot_evap: float = 0  # Heat consumption of heat pump evaporator [kW]
    Qdot_cons1: float = 500  # Heat consumption of consumer 1 [kW]
    Qdot_cons2: float = 500  # Heat consumption of consumer 2 [kW]
    T_tank_forward: float = 70  # Supply temp of storage unit [degC]

    mdot_cons1_set: float = 4  # Mass flow at consumer 1 [kg/s]
    mdot_cons2_set: float = 4  # Mass flow at consumer 2 [kg/s]
    mdot_bypass_set: float = 0.5  # Mass flow through bypass (const.) [kg/s]
    mdot_grid_set: float = 7.5  # Mass flow injected by grid [kg/s]
    mdot_tank_in_set: float = 0  # Mass flow injected in the tank [kg/s]
    mdot_tank_out_set: float = - mdot_tank_in_set  # Mass flow supplied by the tank [kg/s]


    # Variables
    T_return_tank: float = 40  # Return temperature of the storage unit [degC]
    T_evap_in: float = 40  # Return temperature towards the heat pump evaporator [degC]
    T_return_grid: float = 40  # Return temperature of the external grid [degC]
    T_supply_cons1: float = 70  # Supply temperature at consumer 1 [degC]
    T_supply_cons2: float = 70  # Supply temperature at consumer 2 [degC]
    T_return_cons1: float = 40  # Return temperature at consumer 1 [degC]
    T_return_cons2: float = 40  # Return temperature at consumer 2 [degC]
    mdot_cons1: float = 4  # Mass flow at consumer 1 [kg/s]
    mdot_cons2: float = 4  # Mass flow at consumer 2 [kg/s]
    mdot_bypass: float = 0.5  # Mass flow through bypass (const.) [kg/s]
    mdot_grid: float = 7.5  # Mass flow injected by grid [kg/s]
    mdot_tank_in: float = 0  # Mass flow injected in the tank [kg/s]
    mdot_tank_out: float = - mdot_tank_in  # Mass flow supplied by the tank [kg/s]
    P_supply_cons1: float = P_grid_bar  # Supply pressure at consumer 1 [degC]
    P_supply_cons2: float = P_grid_bar  # Supply pressure at consumer 2 [degC]
    P_return_cons1: float = P_grid_bar  # Return pressure at consumer 1 [degC]
    P_return_cons2: float = P_grid_bar  # Return pressure at consumer 2 [degC]

    # Internal variables
    # plot_results_enabled: bool = False  # calculates static and dynamic heat flow and compares both results (only when dynamic temp flow enabled!)
    compare_to_static_results: bool = False  # calculates static and dynamic heat flow and compares both results (only when dynamic temp flow enabled
    store: Dict[str, pd.DataFrame] = field(default_factory=dict)
    cur_t: float = 0  # Actual time [s]

    # Network utils
    net: pp.pandapipesNet = None
    junction: list = None
    pipe: list = None
    heat_exchanger: list = None
    valve: list = None
    controller: list = None
    sink: list = None
    source: list = None
    circ_pump: list = None

    def __post_init__(self):
        self._create_network()
        self._init_output_store()
        warnings.filterwarnings('ignore', message='Pipeflow converged, however, the results are phyisically incorrect as pressure is negative at nodes*')

    def _init_output_store(self):
        # Init output storage
        if self.dynamic_temp_flow_enabled:
            self.store['dynamic'] = {}
            if self.compare_to_static_results:
                self.store['static'] = {}

        else:
            self.store['static'] = {}

    def step_single(self, time):
        j = self.junction
        v = self.valve

        # Set actual time
        self.cur_t = time

        # update inputs
        self._update()

        # Run hydraulic flow (steady-state)
        self.run_hydraulic_control()

        if not self.dynamic_temp_flow_enabled:
            self._run_static_pipeflow()
        else:
            self._run_dynamic_pipeflow()

        # Plot results
        # if self.plot_results_enabled:
            # if self.cur_t == OUTPUT_PLOTTING_PERIOD:
                # self._plot_outputs()

        # Set output variables
        self.T_return_tank = round(self.net.res_junction.at[j.index('n3r'), 't_k'] - 273.15, 2)
        self.T_evap_in = round(self.net.res_junction.at[j.index('n3r'), 't_k'] - 273.15, 2)
        self.T_return_grid = round(self.net.res_junction.at[j.index('n1r'), 't_k'] - 273.15, 2)
        self.T_supply_cons1 = round(self.net.res_junction.at[j.index('n5s'), 't_k'] - 273.15, 2)
        self.T_supply_cons2 = round(self.net.res_junction.at[j.index('n7s'), 't_k'] - 273.15, 2)
        self.T_return_cons1 = round(self.net.res_junction.at[j.index('n5r'), 't_k'] - 273.15, 2)
        self.T_return_cons2 = round(self.net.res_junction.at[j.index('n7r'), 't_k'] - 273.15, 2)
        self.P_supply_cons1 = round(self.net.res_junction.at[j.index('n5s'), 'p_bar'], 2)
        self.P_supply_cons2 = round(self.net.res_junction.at[j.index('n7s'), 'p_bar'], 2)
        self.P_return_cons1 = round(self.net.res_junction.at[j.index('n5r'), 'p_bar'], 2)
        self.P_return_cons2 = round(self.net.res_junction.at[j.index('n7r'), 'p_bar'], 2)

        self.mdot_cons1 = round(self.net.res_valve.at[v.index('sub_v1'), 'mdot_from_kg_per_s'], 2)
        self.mdot_cons2 = round(self.net.res_valve.at[v.index('sub_v2'), 'mdot_from_kg_per_s'], 2)
        self.mdot_bypass = round(self.net.res_valve.at[v.index('bypass'), 'mdot_from_kg_per_s'], 2)
        self.mdot_grid = round(self.net.res_valve.at[v.index('grid_v1'), 'mdot_from_kg_per_s'], 2)
        self.mdot_tank_out = round(self.net.res_valve.at[v.index('tank_v1'), 'mdot_from_kg_per_s'], 2)
        self.mdot_tank_in = - self.mdot_tank_out

    def run_hydraulic_control(self):
        # Ignore user warnings of control
        try:
            run_control(self.net, max_iter=100)
        except:
            # Throw UserWarning
            warnings.warn('Controller not converged: maximum number of iterations per controller is reached at time t={}.'.format(self.cur_t), UserWarning, stacklevel=2)

    def _run_static_pipeflow(self):
        pp.pipeflow(self.net, transient=False, mode='all', max_iter=100, run_control=True, heat_transfer=True)

        # Store results
        # self._store_output(label='static')

    def _run_dynamic_pipeflow(self):
        if self.compare_to_static_results:
            # static temperature flow calculation
            self._run_static_pipeflow()

            # Store results
            self._store_output(label='static')

        # Dynamic heat flow distribution
        self._internal_heatflow_calc()

        # Store results
        self._store_output(label='dynamic')

    def _internal_heatflow_calc(self):
        self._calc_forward_pipe_tempflow()
        self._calc_backward_pipe_tempflow()

    def _calc_forward_pipe_tempflow(self):
        for pipe in self.pipe[0:7]:  # TODO: Make this applicable to any network topology
            self._internal_tempflow_calc(pipe)
            self._update_temperature_flow(pipe)

    def _calc_consumer_return_temperature(self, hex):
        h = self.heat_exchanger
        p = self.pipe

        from_j_id = self.net.heat_exchanger.at[h.index(hex), 'from_junction']
        to_j_id = self.net.heat_exchanger.at[h.index(hex), 'to_junction']
        qext_w = self.net.heat_exchanger.at[h.index(hex), 'qext_w']
        forward_temp = self.net.res_junction.at[from_j_id, 't_k']
        mdot = self.net.res_heat_exchanger.at[h.index(hex), 'mdot_from_kg_per_s']
        cp_w = self.CP_WATER

        # Set forward temperature to hex component
        self.net.res_heat_exchanger.at[h.index(hex), 't_from_k'] = forward_temp

        # Calc return temperature at hex component
        return_temp = forward_temp - qext_w / (cp_w * mdot)

        # Set return temperature at hex component and connected junctions and pipes
        self.net.res_heat_exchanger.at[h.index(hex), 't_to_k'] = return_temp
        self.net.res_junction.at[to_j_id, 't_k'] = return_temp

        conn_p_name = self.net.pipe['name'].loc[self.net.pipe['from_junction'] == to_j_id].values.tolist()
        for pipe in conn_p_name:
            self.net.res_pipe.at[p.index(pipe), 't_from_k'] = return_temp

    def _calc_backward_pipe_tempflow(self):  # TODO: Make this applicable to any network topology
        pipe_seq = self.pipe[7:14]
        pipe_seq.reverse()
        for pipe in pipe_seq:
            self._internal_tempflow_calc(pipe)
            self._update_temperature_flow(pipe)

    def _store_output(self, label='static'):  # TODO: Improve due to low performance
        data = {}

        for j in self.junction:
            data.update({'temp_' + j: round(self.net.res_junction.at[self.junction.index(j), 't_k'] - 273.15, 2)})

        for l in self.pipe:
            # Get temperature
            data.update({'temp_' + l: round(self.net.res_pipe.at[self.pipe.index(l), 't_to_k'] - 273.15, 2)})

            # Get mass flow
            data.update({'mdot_' + l: round(self.net.res_pipe.at[self.pipe.index(l), 'mdot_from_kg_per_s'], 2)})

            # Determine thermal inertia
            dx = self.net.pipe.at[self.pipe.index(l), 'length_km'] * 1000
            v_mean = self.net.res_pipe.at[self.pipe.index(l), 'v_mean_m_per_s']
            dt = dx / v_mean
            data.update({'dt_' + l: round(dt, 2)})

        df = pd.DataFrame.from_dict(self.store[label])
        df = df.append((pd.DataFrame(data=data, index=[self.cur_t])))
        self.store[label] = df.to_dict()

    # def _plot_outputs(self):

        # plt_dict = {
            # # 'temp': ['n1s', 'n2s', 'n3s', 'n3s_tank', 'n4s', 'n5s', 'n6s', 'n7s', 'n8s'],
            # 'temp': ['n3s', 'n5s', 'n4s', 'n6s', 'n7s'],
            # #'dt': ['l2s', 'l3s', 'l4s', 'l5s', 'l6s'],
            # 'mdot': ['l2s', 'l3s', 'l4s', 'l5s', 'l6s'],
        # }

        # # define different linestyles for static and dynamic results
        # ls = {'static': '-', 'dynamic': '--'}

        # # Plot data
        # fig, ax = plt.subplots(nrows=len(plt_dict.keys()), ncols=1)
        # for sim in self.store:
            # df = pd.DataFrame.from_dict(self.store[sim])
            # for i, (title, variables) in enumerate(plt_dict.items()):

                # # create subplot figure setup
                # if len(plt_dict.items()) is 1:
                    # axes = ax
                # else:
                    # axes = ax[i]

                # # plot data
                # axes.set_title(title)
                # for v in variables:
                    # axes.plot(df[title + '_' + v], label=v, linestyle=ls[sim])
                # axes.set_prop_cycle(None)  # same colormap for dynamic and static
                # axes.legend(loc='upper right')

    def _internal_tempflow_calc(self, pipe):
        # Set required input data
        p = self.pipe
        j = self.junction
        net = self.net
        mf = net.res_pipe.at[p.index(pipe), 'mdot_from_kg_per_s']
        Cp_w = self.CP_WATER
        dx = net.pipe.at[p.index(pipe), 'length_km'] * 1000
        v_mean = net.res_pipe.at[p.index(pipe), 'v_mean_m_per_s']
        alpha = net.pipe.at[p.index(pipe), 'alpha_w_per_m2k']
        dia = net.pipe.at[p.index(pipe), 'diameter_m']
        loss_coeff = alpha * math.pi * dia  # Heat loss coefficient in [W/mK]
        Ta = net.pipe.at[p.index(pipe), 'text_k']

        # Get junction connected to pipe inlet
        j_in_id = self.net.pipe.at[p.index(pipe), 'from_junction']
        j_in_name = self.net.junction.at[j_in_id, 'name']

        # Get historic inlet temperature
        df = pd.DataFrame.from_dict(self.store['dynamic'])

        # Get historic inlet temperature
        if not df.empty:
            dt = dx / v_mean
            delay_t = self.cur_t - dt
            Tin = np.interp(delay_t, df.index, df['temp_' + j_in_name]) + 273.15  # TODO: Reduce calls due to performance
        else:
            Tin = net.res_junction.at[j_in_id, 't_k']

        # Static temperature drop
        # Tin = net.res_junction.at[j_in_id, 't_k']

        # Set current inlet temperature of pipe
        net.res_pipe.at[p.index(pipe), 't_from_k'] = Tin

        # Dynamic temperature drop along a pipe
        exp = - (loss_coeff * dx) / (Cp_w * mf)
        Tout = Ta + (Tin - Ta) * math.exp(exp)

        # Set pipe outlet temperature
        net.res_pipe.at[p.index(pipe), 't_to_k'] = Tout

    def _update_temperature_flow(self, act_pipe):
        p = self.pipe
        v = self.valve
        j = self.junction

        # Get connected junctions (direct and indirect)
        # Check direct connection via junction
        conn_j_id = []
        conn_j_id.append(self.net.pipe.at[p.index(act_pipe), 'to_junction'])
        # Check connection via valve
        conn_v_name = self.net.valve['name'].loc[self.net.valve['from_junction'].isin(conn_j_id)].values.tolist()
        for valve in conn_v_name:
            opened = self.net.valve.at[v.index(valve), 'opened']
            if opened:
                conn_j_id.append(self.net.valve.at[v.index(valve), 'to_junction'])

        # Set temperature at connected junctions
        conn_j_name = self.net.junction['name'].iloc[conn_j_id].values.tolist()
        for junction in conn_j_name:
            self._set_pipe_inlet_temperature_at_junction(junction)

        # Get connected hex consumer
        hex_name = self.net.heat_exchanger['name'].loc[self.net.heat_exchanger['from_junction'].isin(conn_j_id)].values.tolist()
        for hex in hex_name:
            # Set temperature at the return side of each hex consumer
            self._calc_consumer_return_temperature(hex)

    def _set_pipe_inlet_temperature_at_junction(self, junction):
        j = self.junction
        p = self.pipe
        v = self.valve
        conn_j_id = [j.index(junction)]
        # Get number of incoming pipes
        # Check connection via valve
        conn_v_name = self.net.valve['name'].loc[self.net.valve['to_junction'].isin(conn_j_id)].values.tolist()
        for valve in conn_v_name:
            opened = self.net.valve.at[v.index(valve), 'opened']
            if opened:
                conn_j_id.append(self.net.valve.at[v.index(valve), 'from_junction'])
        pipes_in = self.net.pipe['name'].loc[self.net.pipe['to_junction'].isin(conn_j_id)].values.tolist()

        mfsum = []
        mtsum = []
        if pipes_in:
            for name in pipes_in:
                # Do temperature mix weighted by share of incoming mass flow
                mdot = self.net.res_pipe.at[p.index(name), 'mdot_from_kg_per_s']
                t_in = self.net.res_pipe.at[p.index(name), 't_to_k']
                mfsum.append(mdot)
                mtsum.append(mdot * t_in)
            Tset = (1 / sum(mfsum)) * sum(mtsum)
        else:
            raise AttributeError(f"Junction '{junction}' not connected to a network pipe.")

        self.net.res_junction.at[j.index(junction), 't_k'] = Tset

    def _update(self):
        hex = self.heat_exchanger
        ctrl = self.controller
        sink = self.sink
        source = self.source
        v = self.valve

        self.mdot_tank_out_set = - self.mdot_tank_in_set
        self.mdot_grid_set = self.mdot_cons1_set + self.mdot_cons2_set + self.mdot_bypass_set - self.mdot_tank_out_set

        # Update grid mass flow
        self.net.sink.at[sink.index('sink_grid'), 'mdot_kg_per_s'] = self.mdot_grid_set

        # Update controller(s)
        self.net.controller.at[ctrl.index('bypass_ctrl'), 'object'].set_mdot_setpoint(self.mdot_bypass_set)
        self.net.controller.at[ctrl.index('hex1_ctrl'), 'object'].set_mdot_setpoint(self.mdot_cons1_set)
        self.net.controller.at[ctrl.index('hex2_ctrl'), 'object'].set_mdot_setpoint(self.mdot_cons2_set)
        self.net.controller.at[ctrl.index('grid_ctrl'), 'object'].set_mdot_setpoint(self.mdot_grid_set)

        # Update tank
        if self.tank_installed:
            self.net.sink.at[sink.index('sink_tank'), 'mdot_kg_per_s'] = self.mdot_tank_out_set
            self.net.ext_grid.at[source.index('supply_tank'), 't_k'] = self.T_tank_forward + 273.15
            self.net.controller.at[ctrl.index('tank_ctrl1'), 'object'].set_mdot_setpoint(self.mdot_tank_out_set)

        # Update load
        self.net.heat_exchanger.at[hex.index('hex1'), 'qext_w'] = self.Qdot_cons1 * 1000
        self.net.heat_exchanger.at[hex.index('hex2'), 'qext_w'] = self.Qdot_cons2 * 1000
        self.net.heat_exchanger.at[hex.index('hp_evap'), 'qext_w'] = self.Qdot_evap * 1000

    def _create_network(self):
        # create empty network
        self.net = pp.create_empty_network('net', add_stdtypes=False)

        # create fluid
        pp.create_fluid_from_lib(self.net, 'water', overwrite=True)

        # create utils
        self._create_junctions()
        self._create_external_grid()
        self._create_pipes()
        self._create_substations()
        if self.tank_installed:
            self._create_heatpump()
        self._create_bypass()
        self._create_flow_control()
        # self._plot()

    def _create_junctions(self):
        # create nodes (with initial pressure and temperature)
        net = self.net
        pn_init = self.P_grid_bar
        tfluid_init = 273.15 + self.T_supply_grid
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n1s', geodata=(0, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n1r', geodata=(0, -2.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n2s', geodata=(3, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n2r', geodata=(3, -2.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n3s', geodata=(6, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n3s_tank', geodata=(6, 3))  # create hp+tank injection point
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n3sv', geodata=(6, 1.4))  # create tank valve
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n3r', geodata=(6, -2.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n3r_tank', geodata=(6, -4.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n4s', geodata=(10, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n4r', geodata=(11, -2.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n5sv', geodata=(10, 1.5))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n5s', geodata=(10, 4))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n5r', geodata=(11, 4))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n6s', geodata=(15, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n6r', geodata=(16, -2.1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n7sv', geodata=(15, 1.5))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n7s', geodata=(15, 4))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n7r', geodata=(16, 4))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n8s', geodata=(19, 1))
        pp.create_junction(net, pn_bar=pn_init, tfluid_k=tfluid_init, name='n8r', geodata=(19, -2.1))

        self.junction = net.junction['name'].tolist()

    def _create_external_grid(self):
        net = self.net
        j = self.junction
        t_supply_grid_k = 273.15 + self.T_supply_grid
        mdot_init = self.mdot_grid

        # create external grid
        pp.create_ext_grid(net, junction=j.index('n1s'), p_bar=self.P_grid_bar, t_k=t_supply_grid_k, name='ext_grid', type='pt')

        # create sink and source
        pp.create_sink(net, junction=j.index('n1r'), mdot_kg_per_s=mdot_init, name='sink_grid')
        pp.create_source(net, junction=j.index('n1r'), mdot_kg_per_s=0, name='source_grid')

        self.sink = net.sink['name'].tolist()
        self.source = net.ext_grid['name'].tolist()

    def _create_pipes(self):
        net = self.net
        j = self.junction

        l01 = 0.5

        # supply pipes
        pp.create_pipe_from_parameters(net, from_junction=j.index('n1s'), to_junction=j.index('n2s'), length_km=l01,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15+8, name='l1s')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n3sv'), to_junction=j.index('n3s'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l1s_tank')         # create tank pipe connection
        pp.create_pipe_from_parameters(net, from_junction=j.index('n3s'), to_junction=j.index('n4s'), length_km=0.5,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l2s')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n4s'), to_junction=j.index('n5sv'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l3s')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n4s'), to_junction=j.index('n6s'), length_km=0.5,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l4s')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n6s'), to_junction=j.index('n7sv'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l5s')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n6s'), to_junction=j.index('n8s'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l6s')

        # return pipes
        pp.create_pipe_from_parameters(net, from_junction=j.index('n2r'), to_junction=j.index('n1r'), length_km=l01,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15+8, name='l1r')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n3r'), to_junction=j.index('n3r_tank'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l1r_tank')         # create tank pipe connection
        pp.create_pipe_from_parameters(net, from_junction=j.index('n4r'), to_junction=j.index('n3r'), length_km=0.5,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l2r')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n5r'), to_junction=j.index('n4r'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l3r')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n6r'), to_junction=j.index('n4r'), length_km=0.5,
                                       diameter_m=0.1, k_mm=0.01, sections=5, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l4r')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n7r'), to_junction=j.index('n6r'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l5r')
        pp.create_pipe_from_parameters(net, from_junction=j.index('n8r'), to_junction=j.index('n6r'), length_km=0.01,
                                       diameter_m=0.1, k_mm=0.01, sections=1, alpha_w_per_m2k=1.5,
                                       text_k=273.15 + 8, name='l6r')

        # create grid connector valves
        pp.create_valve(net, j.index('n2s'), j.index('n3s'), diameter_m=0.1, loss_coefficient=1000, opened=True, name='grid_v1')
        if not self.tank_installed:
            pp.create_valve(net, j.index('n3r'), j.index('n2r'), diameter_m=0.1, loss_coefficient=0, opened=True, name='grid_v2')

        self.pipe = net.pipe['name'].tolist()
        self.valve = net.valve['name'].tolist()

    def _create_substations(self):
        net = self.net
        j = self.junction
        q_hex1 = self.Qdot_cons1 * 1000
        q_hex2 = self.Qdot_cons2 * 1000

        # create control valves
        pp.create_valve(net, j.index('n5sv'), j.index('n5s'), diameter_m=0.1, opened=True, loss_coefficient=1000, name='sub_v1')
        pp.create_valve(net, j.index('n7sv'), j.index('n7s'), diameter_m=0.1, opened=True, loss_coefficient=1000, name='sub_v2')

        # create heat exchanger
        pp.create_heat_exchanger(net, from_junction=j.index('n5s'), to_junction=j.index('n5r'), diameter_m=0.1,
                                 qext_w=q_hex1, name='hex1')
        pp.create_heat_exchanger(net, from_junction=j.index('n7s'), to_junction=j.index('n7r'), diameter_m=0.1,
                                 qext_w=q_hex2, name='hex2')

        self.heat_exchanger = net.heat_exchanger['name'].tolist()
        self.valve = net.valve['name'].tolist()

    def _create_heatpump(self):
        net = self.net
        j = self.junction
        mdot_tank_init = self.mdot_tank_out
        t_supply_tank_k = self.T_tank_forward + 273.15
        p_bar_set = self.P_hp_bar
        q_hp_evap = self.Qdot_evap * 1000

        # create hp evaporator
        pp.create_heat_exchanger(net, from_junction=j.index('n3r'), to_junction=j.index('n2r'), diameter_m=0.1,
                                 qext_w=q_hp_evap, name='hp_evap')

        # create tank supply
        pp.create_ext_grid(net, junction=j.index('n3s_tank'), p_bar=p_bar_set, t_k=t_supply_tank_k, name='supply_tank', type='pt')

        # create tank mass flow sink
        pp.create_sink(net, junction=j.index('n3r_tank'), mdot_kg_per_s=mdot_tank_init, name='sink_tank')

        # create valves
        pp.create_valve(net, j.index('n3s_tank'), j.index('n3sv'), diameter_m=0.1, opened=True, loss_coefficient=1000, name='tank_v1')

        self.heat_exchanger = net.heat_exchanger['name'].tolist()
        self.valve = net.valve['name'].tolist()
        self.sink = net.sink['name'].tolist()
        self.source = net.ext_grid['name'].tolist()

    def _create_bypass(self):
        net = self.net
        j = self.junction

        # create bypass valve
        pp.create_valve(net, j.index('n8s'), j.index('n8r'), diameter_m=0.1, opened=True, loss_coefficient=1000, name='bypass')

        self.valve = net.valve['name'].tolist()

    def _create_flow_control(self):
        net = self.net
        v = self.valve
        s = self.sink

        # create supply flow control
        CtrlValve(net=net, gid=v.index('tank_v1'), gain=-3000,
                  # data_source=data_source, profile_name='tank',
                  level=0, order=1, tol=0.25, name='tank_ctrl1')

        CtrlValve(net=net, gid=v.index('grid_v1'), gain=-3000,
                  # data_source=data_source, profile_name='tank',
                  level=0, order=2, tol=0.25, name='grid_ctrl')

        # create load flow control
        CtrlValve(net=net, gid=v.index('bypass'), gain=-2000,
                  # data_source=data_source, profile_name='bypass',
                  level=1, order=1, tol=0.25, name='bypass_ctrl')
        CtrlValve(net=net, gid=v.index('sub_v1'), gain=-100,
                  #data_source=data_source, profile_name='hex1',
                  level=1, order=2, tol=0.1, name='hex1_ctrl')
        CtrlValve(net=net, gid=v.index('sub_v2'), gain=-100,
                  # data_source=data_source, profile_name='hex2',
                  level=1, order=3, tol=0.1, name='hex2_ctrl')

        self.controller = ['tank_ctrl1', 'grid_ctrl', 'bypass_ctrl', 'hex1_ctrl', 'hex2_ctrl']

    # def _plot(self):
        # plot.simple_plot(self.net, plot_sinks=True, plot_sources=True, sink_size=4.0, source_size=4.0)

# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
This MOSAIK co-simulation setup implements the ERIGrid 2.0 multi-energy network benchmark.
'''

# Define default for simulation start time, step size and end (1 MOSAIK time-step = 1 second).
START_TIME = '2019-02-01 00:00:00'
STEP_SIZE = 60 * 1
END = 7 * 24 * 60 * 60

# Specify profiles for generation and demand.
POWER_DEMAND_LOAD_PROFILES = 'resources/power/power_demand_load_profiles.csv'
PV_GENERATION_PROFILES = 'resources/power/pv_generation_profiles.csv'

# MOSAIK simulator configuration.
SIM_CONFIG = {
    'DHNetworkSim': {
        'python': 'simulators:DHNetworkSimulator'
    },
    'ElNetworkSim': {
        'python': 'simulators:ElectricNetworkSimulator'
    },
    'FlexHeatCtrlSim': {
        'python': 'simulators:SimpleFlexHeatControllerSimulator'
    },
    'VoltageCtrlSim': {
        'python': 'simulators:VoltageControlSimulator'
    },
    'TimeSeriesSim': {
        'python': 'simulators:TimeSeriesPlayerSim'
    },
    'CollectorSim': {
        'python': 'simulators:Collector'
    },
}


def loadProfiles():
    '''
    Load profiles for demand (heat, power) and PV generation.
    '''
    import pandas as pd
    import pathlib

    profiles = {}

    here = pathlib.Path(__file__).resolve().parent

    profiles['power_demand'] = pd.read_csv(
        pathlib.Path(here, POWER_DEMAND_LOAD_PROFILES),
        index_col = 0, parse_dates = True
    )

    profiles['pv_generation'] = pd.read_csv(
        pathlib.Path(here, PV_GENERATION_PROFILES),
        index_col = 0, parse_dates = True
    )

    return profiles


def initializeSimulators(world, step_size, outfile_name):
    '''
    Initialize and start all simulators.
    '''
    simulators = {}

    # Electrical network.
    simulators['el_network'] = world.start(
        'ElNetworkSim',
        step_size = step_size,
        mode = 'pf'
    )

    # District heating network.
    simulators['dh_network'] = world.start(
        'DHNetworkSim',
        step_size = step_size,
        additional_output_table = { 
            'PID_controller.u_s': 'Real',
            'PID_controller.u_m': 'Real',
            'PID_controller.y': 'Real',
            'thermalNetwork.powerToHeat.T_tank_mean_degC': 'Real',
        },
        additional_param_table = {
        },
        logging_on = False
    )

    # Time series player for electrical load profiles and PV generation profiles.
    simulators['load_gen_profiles'] = world.start(
        'TimeSeriesSim',
        eid_prefix = 'power_demand',
        step_size = step_size
    )

    # Flex heat controller.
    simulators['flex_heat_ctrl'] = world.start(
        'FlexHeatCtrlSim',
        step_size = step_size
    )

    # Voltage controller.
    simulators['voltage_ctrl'] = world.start(
        'VoltageCtrlSim',
        step_size = step_size
    )

    # Data collector.
    simulators['collector'] = world.start(
        'CollectorSim',
        step_size = step_size,
        print_results = False,
        save_h5 = True,
        h5_store_name = outfile_name,
        h5_frame_name = 'results'
    )

    return simulators


def instantiateEntities(simulators, profiles, voltage_control_enabled = True):
    '''
    Create instances of simulators.
    '''
    entities = {}

    # Electrical network.
    entities['el_network'] = simulators['el_network'].Grid(
        gridfile = 'resources/power/power_grid_model.json',
    )

    # Add electrical network components to collection of entities.
    grid = entities['el_network'].children
    entities.update( {element.eid: element for element in grid if element.type in 'Load'} )
    entities.update( {element.eid: element for element in grid if element.type in 'Sgen'} )
    entities.update( {element.eid: element for element in grid if element.type in 'Bus'} )
    entities.update( {element.eid: element for element in grid if element.type in 'Line'} )

    # Time series player for the power consumption profile of load 1.
    entities['consumer_load1'] = simulators['load_gen_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['power_demand'].copy(),
        fieldname = 'Load_1',
        interp_method = 'pchip',
    )

    # Time series player for the power consumption profile of load 2.
    entities['consumer_load2'] = simulators['load_gen_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['power_demand'].copy(),
        fieldname = 'Load_2',
        interp_method = 'pchip',
    )

    # Time series player for generation profile of PV 1.
    entities['gen_pv1'] = simulators['load_gen_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['pv_generation'].copy(),
        fieldname = 'PV_1',
        interp_method = 'pchip',
    )

    # Time series player for generation profile of PV 2.
    entities['gen_pv2'] = simulators['load_gen_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['pv_generation'].copy(),
        fieldname = 'PV_2',
        interp_method = 'pchip',
    )

    # Flex heat controller.
    entities['flex_heat_ctrl'] = simulators['flex_heat_ctrl'].SimpleFlexHeatController(
        voltage_control_enabled = voltage_control_enabled
    )

    # District heating network.
    entities['dh_network'] = simulators['dh_network'].DHNetwork()

    # Voltage controller.
    entities['voltage_ctrl'] = simulators['voltage_ctrl'].VoltageController(
        delta_vm_upper_pu = 0.1,
        delta_vm_lower_pu_hp_on = -0.1,
        delta_vm_lower_pu_hp_off = -0.08,
        delta_vm_deadband = 0.03,
        hp_p_el_mw_rated = 0.1,
        hp_p_el_mw_min = 0.4 * 0.1,
        hp_operation_steps_min = 30 * 60 / STEP_SIZE,
        k_p = 0.15
    )

    # Data collector.
    entities['sc_monitor'] = simulators['collector'].Collector()

    return entities


def connectEntities(world, entities):
    '''
    Add connections between the simulator entities.
    '''
    from simulators.el_network.simulator import make_eid as el_grid_id

    # Connect electrical consumption profiles to electrical loads.
    world.connect(entities['consumer_load1'], entities[el_grid_id('Load_1',0)], ('out', 'p_mw'))
    world.connect(entities['consumer_load2'], entities[el_grid_id('Load_2',0)], ('out', 'p_mw'))

    # Connect PV profiles to static generators.
    world.connect(entities['gen_pv1'], entities[el_grid_id('PV_1',0)], ('out', 'p_mw'))
    world.connect(entities['gen_pv2'], entities[el_grid_id('PV_2',0)], ('out', 'p_mw'))

    # Connect heat pump to electrical grid.
    world.connect(entities['dh_network'], entities[el_grid_id('Heat Pump',0)], ('P_el_heatpump_MW', 'p_mw'),
        time_shifted=True, initial_data={'P_el_heatpump_MW': 0.})

    # Voltage controller.
    world.connect(entities[el_grid_id('Bus_1',0)], entities['voltage_ctrl'], ('vm_pu', 'vmeas_pu'))
    world.connect(entities['voltage_ctrl'], entities['flex_heat_ctrl'], ('hp_p_el_kw_setpoint', 'P_hp_el_setpoint'))

    # Flex heat control.
    world.connect(entities['flex_heat_ctrl'], entities['dh_network'], ('P_hp_el', 'P_el_heatpump_setpoint_kW'))
    world.connect(entities['flex_heat_ctrl'], entities['dh_network'], ('mdot_tank_out', 'mdot_tank_out'))
    world.connect(entities['dh_network'], entities['flex_heat_ctrl'], ('T_tank_high_degC', 'T_tank_hot'),
        time_shifted=True, initial_data={'T_tank_high_degC': 70.})


def connectDataCollector(world, entities):
    '''
    Configure and connect the data collector.
    '''
    from simulators.dh_network.mosaik_wrapper import translate_var_name as dh_var

    collector_connections = {}

    collector_connections['dh_network'] = [
        'T_tank_high_degC', 'T_tank_low_degC',
        dh_var('PID_controller.u_s'), 
        dh_var('PID_controller.u_m'), 
        dh_var('PID_controller.y'),
        dh_var('thermalNetwork.powerToHeat.T_tank_mean_degC'),
        ]

    collector_connections['voltage_ctrl'] = [
        'hp_p_el_kw_setpoint'
        ]

    collector_connections['flex_heat_ctrl'] = [
        'mdot_tank_out', 'P_hp_el', 
        'hp_on_request', 'hp_off_request', 'state'
        ]

    collector_connections.update({element.eid: ['p_mw'] for element in entities.values() if element.type in 'Load'})
    collector_connections.update({element.eid: ['p_mw'] for element in entities.values() if element.type in 'Sgen'})
    collector_connections.update({element.eid: ['vm_pu'] for element in entities.values() if element.type in 'Bus'})
    collector_connections.update({element.eid: ['loading_percent'] for element in entities.values() if element.type in 'Line'})

    for ent, outputnames in collector_connections.items():
        for outputname in outputnames:
            world.connect(entities[ent], entities['sc_monitor'], outputname)


if __name__ == '__main__':
    import argparse
    import mosaik
    from time import time, ctime
    from datetime import timedelta

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', default = 'benchmark_results.h5', help = 'results file name')
    parser.add_argument('--voltage-control-disabled', action = 'store_true', help = 'disable voltage control')
    parser.add_argument('--step-size', type = int, default = STEP_SIZE, help = 'simulation step size in seconds')
    parser.add_argument('--end', type = int, default = END, help = 'simulation period in seconds')
    args = parser.parse_args()

    voltage_control_enabled = not args.voltage_control_disabled
    outfile_name = args.outfile
    step_size = args.step_size
    end = args.end

    sim_start_time = time()
    print("CO-SIMULATION STARTED AT:", ctime(sim_start_time))

    # Start MOSAIK orchestrator.
    world = mosaik.World(SIM_CONFIG)

    # Initialize and start all simulators.
    simulators = initializeSimulators(world, step_size, outfile_name)

    # Load profiles for demand (heat, power) and PV generation.
    profiles = loadProfiles()

    # Create instances of simulators.
    entities = instantiateEntities(simulators, profiles, voltage_control_enabled)

    # Add connections between the simulator entities.
    connectEntities(world, entities)

    # Configure and connect the data collector.
    connectDataCollector(world, entities)

    # Run the simulation.
    world.run(until = end)

    sim_elapsed_time = str(timedelta(seconds = time() - sim_start_time))
    print('TOTAL ELAPSED CO-SIMULATION TIME:', sim_elapsed_time)

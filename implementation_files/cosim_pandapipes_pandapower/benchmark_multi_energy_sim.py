# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
This MOSAIK co-simulation setup implements the ERIGrid 2.0 multi-energy benchmark.
'''

# Define default for simulation start time, step size and end (1 MOSAIK time-step = 1 second).
START_TIME = '2019-02-01 00:00:00'
STEP_SIZE = 60 * 1
END = 7 * 24 * 60 * 60

# Specify profiles for generation and demand.
HEAT_DEMAND_LOAD_PROFILES = 'resources/heat/heat_demand_load_profiles.csv'
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
    'StorageTankSim': {
        'python': 'simulators:StratifiedWaterStorageTankSimulator'
    },
    'HeatPumpSim': {
        'python': 'simulators:ConstantTcondHPSimulator'
    },
    'HeatExchangerSim': {
        'python': 'simulators:HEXConsumerSimulator'
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

# Simulation parameters.
HP_TEMP_COND_OUT_TARGET = 75
EXT_SOURCE_SUPPLY_TEMP = 75  # Supply temperature of external DH network.

INIT_HEX_SUPPLY_TEMP = 75  # Return temperature of heat exchanger.
INIT_HEX_RETURN_TEMP = 45  # Return temperature of heat exchanger.
INIT_STORAGE_TANK_TEMP = 70  # Storage tank initial temperature.


def loadProfiles():
    '''
    Load profiles for demand (heat, power) and PV generation.
    '''
    import pandas as pd
    import pathlib

    profiles = {}
    
    here = pathlib.Path(__file__).resolve().parent
    
    profiles['heat_demand'] = pd.read_csv(
        pathlib.Path(here, HEAT_DEMAND_LOAD_PROFILES),
        index_col = 0, parse_dates = True
    )

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
        step_size = step_size
    )

    # Heat consumer (heat exchanger).
    simulators['hex_consumer'] = world.start(
        'HeatExchangerSim',
        step_size = step_size
    )

    # Time series player for electrical load profiles and PV generation profiles.
    simulators['load_gen_profiles'] = world.start(
        'TimeSeriesSim',
        eid_prefix = 'power_demand',
        step_size = step_size
    )

    # Time series player for the consumer heat demand.
    simulators['heat_profiles'] = world.start(
        'TimeSeriesSim',
        eid_prefix = 'heat_demand',
        step_size = step_size
    )

    # Stratified water storage tank.
    simulators['storage_tank'] = world.start(
        'StorageTankSim',
        step_size = step_size
    )

    # Heat pump.
    simulators['heat_pump'] = world.start(
        'HeatPumpSim',
        eid_prefix = 'heatpump',
        step_size = step_size,
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

    # District heating network.
    entities['dh_network'] = simulators['dh_network'].DHNetwork(
        T_supply_grid = 75,
        P_grid_bar = 6,
        T_amb = 8,
        dynamic_temp_flow_enabled = False,
    )

    # Heat exchanger 1.
    entities['hex_consumer1'] = simulators['hex_consumer'].HEXConsumer(
        T_return_target = 40,
        P_heat = 500,
        mdot_hex_in = 3.5,
        mdot_hex_out = -3.5,
    )

    # Heat exchanger 2.
    entities['hex_consumer2'] = simulators['hex_consumer'].HEXConsumer(
        T_return_target = 40,
        P_heat = 500,
        mdot_hex_in = 3.5,
        mdot_hex_out = -3.5,
    )

    # Time series player for heat demand of consumer 1.
    entities['heat_profiles1'] = simulators['heat_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['heat_demand'].copy(),
        fieldname = 'consumer1',
    )


    # Time series player for heat demand of consumer 2.
    entities['heat_profiles2'] = simulators['heat_profiles'].TimeSeriesPlayer(
        t_start = START_TIME,
        series = profiles['heat_demand'].copy(),
        fieldname = 'consumer2',
    )

    # Stratified water storage tank.
    entities['storage_tank'] = simulators['storage_tank'].WaterStorageTank(
        INNER_HEIGHT = 9.2-0.5-0.4-0.4,  # Full tank height, minus valve height, minus half rounded end height
        INNER_DIAMETER = 3.72,
        INSULATION_THICKNESS = 0.1,
        STEEL_THICKNESS = 0.02,
        NB_LAYERS = 10,
        T_volume_initial = INIT_STORAGE_TANK_TEMP,
        dt = STEP_SIZE
    )

    # Heat pump.
    entities['heat_pump'] = simulators['heat_pump'].ConstantTcondHP(
        P_rated = 100.0,
        lambda_comp = 0.2,
        P_0 = 0.3,
        eta_sys = 0.5,
        eta_comp = 0.7,
        T_evap_out_min = 20,
        dt = STEP_SIZE,
        T_cond_out_target = HP_TEMP_COND_OUT_TARGET,  # degC
    )

    # Flex heat controller.
    entities['flex_heat_ctrl'] = simulators['flex_heat_ctrl'].SimpleFlexHeatController(
        voltage_control_enabled = voltage_control_enabled
    )

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
    from simulators.el_network.simulator import make_eid as grid_id
    
    # Connect electrical consumption profiles to electrical loads.
    world.connect(entities['consumer_load1'], entities[grid_id('Load_1',0)], ('out', 'p_mw'))
    world.connect(entities['consumer_load2'], entities[grid_id('Load_2',0)], ('out', 'p_mw'))

    # Connect PV profiles to static generators.
    world.connect(entities['gen_pv1'], entities[grid_id('PV_1',0)], ('out', 'p_mw'))
    world.connect(entities['gen_pv2'], entities[grid_id('PV_2',0)], ('out', 'p_mw'))

    # Voltage controller.
    world.connect(entities[grid_id('Bus_1',0)], entities['voltage_ctrl'], ('vm_pu', 'vmeas_pu'))
    world.connect(entities['voltage_ctrl'], entities['flex_heat_ctrl'], ('hp_p_el_kw_setpoint', 'P_hp_el_setpoint'))
    world.connect(entities['heat_pump'], entities['flex_heat_ctrl'], ('P_effective', 'P_hp_effective'),
        time_shifted=True, initial_data={'P_effective': 0})

    # District heating network.
    world.connect(entities['flex_heat_ctrl'], entities['dh_network'], ('mdot_1_supply', 'mdot_grid_set'))
    world.connect(entities['flex_heat_ctrl'], entities['dh_network'], ('mdot_3_supply', 'mdot_tank_in_set'))
    world.connect(entities['hex_consumer1'], entities['dh_network'], ('mdot_hex_out', 'mdot_cons1_set'))
    world.connect(entities['hex_consumer2'], entities['dh_network'], ('mdot_hex_out', 'mdot_cons2_set'))

    # Heat demand consumer 1.
    world.connect(entities['heat_profiles1'], entities['dh_network'], ('out', 'Qdot_cons1'))
    world.connect(entities['heat_profiles1'], entities['hex_consumer1'], ('out', 'P_heat'))
    world.connect(entities['hex_consumer1'], entities['flex_heat_ctrl'], ('mdot_hex_out', 'mdot_HEX1'))
    world.connect(entities['dh_network'], entities['hex_consumer1'], ('T_supply_cons1', 'T_supply'),
        time_shifted=True, initial_data={'T_supply_cons1': 70})

    # Heat demand consumer 1.
    world.connect(entities['heat_profiles2'], entities['dh_network'], ('out', 'Qdot_cons2'))
    world.connect(entities['heat_profiles2'], entities['hex_consumer2'], ('out', 'P_heat'))
    world.connect(entities['hex_consumer2'], entities['flex_heat_ctrl'], ('mdot_hex_out', 'mdot_HEX2'))
    world.connect(entities['dh_network'], entities['hex_consumer2'], ('T_supply_cons2', 'T_supply'),
        time_shifted=True, initial_data={'T_supply_cons2': 70})

    # Heat pump.
    world.connect(entities['flex_heat_ctrl'], entities['heat_pump'], ('mdot_2_return', 'mdot_evap_in'))
    world.connect(entities['dh_network'], entities['heat_pump'], ('T_evap_in', 'T_evap_in'),
        time_shifted=True, initial_data={'T_evap_in': 40})
    world.connect(entities['heat_pump'], entities['dh_network'], ('Qdot_evap', 'Qdot_evap'))
    world.connect(entities['storage_tank'], entities['heat_pump'], ('T_cold', 'T_cond_in'),
        time_shifted=True, initial_data={'T_cold': INIT_STORAGE_TANK_TEMP})
    world.connect(entities['heat_pump'], entities[grid_id('Heat Pump',0)], ('P_effective_mw', 'p_mw'),
        time_shifted=True, initial_data={'P_effective_mw': 0.})

    # Flex heat control.
    world.connect(entities['flex_heat_ctrl'], entities['heat_pump'], ('mdot_HP_out', 'mdot_cond_in'))
    world.connect(entities['heat_pump'], entities['flex_heat_ctrl'], ('T_cond_out_target', 'T_hp_cond_out'),
        time_shifted=True, initial_data={'T_cond_out_target': HP_TEMP_COND_OUT_TARGET})
    world.connect(entities['heat_pump'], entities['flex_heat_ctrl'], ('T_cond_in', 'T_hp_cond_in'),
        time_shifted=True, initial_data={'T_cond_in': INIT_STORAGE_TANK_TEMP})
    world.connect(entities['heat_pump'], entities['flex_heat_ctrl'], ('T_evap_in', 'T_hp_evap_in'),
        time_shifted=True, initial_data={'T_evap_in': INIT_HEX_RETURN_TEMP})

    # Storage tank inlet.
    world.connect(entities['heat_pump'], entities['storage_tank'], ('mdot_cond_out', 'mdot_ch_in'))
    world.connect(entities['heat_pump'], entities['storage_tank'], ('T_cond_out', 'T_ch_in'))
    world.connect(entities['flex_heat_ctrl'], entities['storage_tank'], ('mdot_3_supply', 'mdot_dis_out'),
        time_shifted=True, initial_data={'mdot_3_supply': 0})
    world.connect(entities['dh_network'], entities['storage_tank'], ('T_return_tank', 'T_dis_in'))

    # Storage tank outlet.
    world.connect(entities['storage_tank'], entities['dh_network'], ('T_hot', 'T_tank_forward'),
        time_shifted=True, initial_data={'T_hot': INIT_STORAGE_TANK_TEMP})
    world.connect(entities['storage_tank'], entities['flex_heat_ctrl'], ('T_hot', 'T_tank_hot'),
        time_shifted=True, initial_data={'T_hot': INIT_STORAGE_TANK_TEMP})


def connectDataCollector(world, entities):
    '''
    Configure and connect the data collector.
    '''
    collector_connections = {}

    collector_connections['storage_tank'] = [
            'T_cold', 'T_hot', 'T_avg',
            'mdot_ch_in', 'mdot_dis_in', 'mdot_ch_out', 'mdot_dis_out',
            'T_ch_in', 'T_dis_in'
            ]

    collector_connections['hex_consumer1'] = [
            'P_heat', 'mdot_hex_in', 'mdot_hex_out',
            'T_supply', 'T_return']

    collector_connections['hex_consumer2'] = [
            'P_heat', 'mdot_hex_in', 'mdot_hex_out',
            'T_supply', 'T_return']

    collector_connections['heat_pump'] = [
            'T_cond_out', 'T_cond_in',
            'T_evap_in', 'T_evap_out',
            'mdot_cond_in', 'mdot_cond_out',
            'mdot_evap_in', 'mdot_evap_out',
            'Qdot_cond', 'Qdot_evap',
            'W_effective', 'W_requested',
            'W_max', 'W_evap_max', 'W_cond_max', 'W_rated',
            'P_effective', 'P_requested',
            'P_rated', 'eta_hp'
            ]

    collector_connections['dh_network'] = [
            'T_tank_forward', 'T_supply_cons1', 'T_supply_cons2', 'T_return_cons1', 'T_return_cons2','T_return_tank','T_return_grid',
            'mdot_cons1_set', 'mdot_cons2_set', 'mdot_grid_set', 'mdot_tank_in_set',
            'mdot_cons1', 'mdot_cons2', 'mdot_grid', 'mdot_tank_in',
            'Qdot_cons1', 'Qdot_cons2', 'Qdot_evap'
            ]

    collector_connections['voltage_ctrl'] = [
            'hp_p_el_kw_setpoint'
            ]

    collector_connections['flex_heat_ctrl'] = [
            'hp_on_request', 'hp_off_request',
            'mdot_HP_out', 'state'
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

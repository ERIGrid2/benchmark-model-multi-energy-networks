'''
Analysis script for the benchmark results, comparing
results with voltage control enabled and disabled.
'''

import matplotlib.pyplot as plt
import pandas as pd

START_TIME = '2019-02-01 00:00:00'

DROP_FIRST_DAY_DATA = True

DATA_DICT = {
    'tank': [
        [
            'DHNetwork_0.T_tank_low_degC',
            'DHNetwork_0.thermalNetwork_powerToHeat_T_tank_mean_degC',
            'DHNetwork_0.T_tank_high_degC',
        ]
    ],
    'heat_pump': [
        [
            'DHNetwork_0.PID_controller_u_m',
        ]
    ],
    'flex_heat_ctrl': [
        [
            'FHctrl_0.state',
        ]
    ],
    'voltage_ctrl': [
        [
            'VoltageController_0.hp_p_el_kw_setpoint',
        ]
    ],
    'busses': [
        [
            'Bus_1_0.vm_pu',
            'Bus_2_0.vm_pu',
        ]
    ],
    'lines': [
        [
            'LV_Line_0-1_0.loading_percent',
            'LV_Line_1-2_0.loading_percent',
        ]
    ],
}

VAR_DICT = {
    # tank temperatures
    'DHNetwork_0.T_tank_low_degC': 'T_tank_low_degC',
    'DHNetwork_0.thermalNetwork_powerToHeat_T_tank_mean_degC': 'T_tank_mean_degC',
    'DHNetwork_0.T_tank_high_degC': 'T_tank_high_degC',
    # heatpump pid
    'DHNetwork_0.PID_controller_u_m': 'P_effective_W',
    # flex heat controller state
    'FHctrl_0.state': 'state',
    # voltage controller
    'VoltageController_0.hp_p_el_kw_setpoint': 'setpoint_hp_p_el_kW',
    # voltage levels
    'Bus_1_0.vm_pu': 'bus_1_voltage_pu',
    'Bus_2_0.vm_pu': 'bus_2_voltage_pu',
    # line loadings
    'LV_Line_0-1_0.loading_percent': 'line_1_loading',
    'LV_Line_1-2_0.loading_percent': 'line_2_loading',
}


def get_sim_node_name(
    full_name
):
    (sim_name, sim_node) = full_name.split('.')
    return sim_node


def retrieve_results(
    store_name,
    start_time,
    drop_first_day_data = True
):
    results_dict = {}
    results_store = pd.HDFStore(store_name)

    for collector in results_store:
        for (simulator, attribute), data in results_store[collector].items():
            # Retrieve short name of data.
            sim_node_name = get_sim_node_name(simulator)
            res_name = '.'.join([sim_node_name, attribute])

            # Convert index to time format.
            data.index = pd.to_datetime(data.index, unit = 's', origin = start_time)

            if drop_first_day_data:
                first_day_data = data.first('2D')
                results_dict[res_name] = data.drop(first_day_data.index)
            else:
                results_dict[res_name] = data

    results_store.close()
    return results_dict


def extract_results_single_run(
    results_dict, data_dict, var_dict, csv_id
):
    for i, (title, [variables]) in enumerate(data_dict.items()):
        df = pd.DataFrame()
        for v in variables:
            print(v)
            df[var_dict[v]] = results_dict[v]
        df.index.name = 'time'
        file_name = '{}_{}.csv'.format(csv_id, title.replace(' ', '_'))
        df.to_csv(file_name, float_format='%.3f')


if __name__ == '__main__':
    # Retrieve results for simulation with voltage control enabled.
    dict_results_ctrl_enabled = retrieve_results(
        'benchmark_results_ctrl_enabled.h5',
        START_TIME, DROP_FIRST_DAY_DATA
        )

    # Retrieve results for simulation with voltage control disabled.
    dict_results_ctrl_disabled = retrieve_results(
        'benchmark_results_ctrl_disabled.h5',
        START_TIME, DROP_FIRST_DAY_DATA
        )

    # Write results for simulation with voltage control enabled.
    extract_results_single_run(
        dict_results_ctrl_enabled, DATA_DICT, VAR_DICT, 'ctrl_enabled'
        )

    # Write results for simulation with voltage control disabled.
    extract_results_single_run(
        dict_results_ctrl_disabled, DATA_DICT, VAR_DICT, 'ctrl_disabled'
        )

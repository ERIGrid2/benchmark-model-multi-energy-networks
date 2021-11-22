'''
Analysis script for the benchmark results, comparing
results with voltage control enabled and disabled.
'''

import matplotlib.pyplot as plt
import pandas as pd

START_TIME = '2019-02-01 00:00:00'

DROP_FIRST_DAYS_DATA = True

PLOT_DICT = {
    'tank temperatures': [
        'temperature in °C',
        [
            'DHNetwork_0.T_tank_low_degC',
            'DHNetwork_0.T_tank_high_degC',
            'DHNetwork_0.thermalNetwork_powerToHeat_T_tank_mean_degC',
        ]
    ],
    'tank mass flow': [
        'mass flow in kg/s',
        [
            'FHctrl_0.mdot_tank_out',
        ]
    ],
    'heatpump pid': [
        'power in W',
        [
            'DHNetwork_0.PID_controller_u_s',
            'DHNetwork_0.PID_controller_u_m',
        ]
    ],
    'heatpump ctrl': [
        'power in kW',
        [
            'FHctrl_0.P_hp_el'
        ]
    ],
    'flex heat controller state': [
        'state',
        [
            'FHctrl_0.state',
        ]
    ],
    'voltage controller': [
        'setpoint in kW',
        [
            'VoltageController_0.hp_p_el_kw_setpoint',
        ]
    ],
    'electrical consumption': [
        'electrical consumption in MW',
        [
            'Load_1_0.p_mw',
            'Load_2_0.p_mw',
        ]
    ],
    'PV generation': [
        'PV generation in MW',
        [
            'PV_1_0.p_mw',
            'PV_2_0.p_mw',
        ]
    ],
    'voltage levels': [
        'voltage levels in p.u.',
        [
            'Bus_1_0.vm_pu',
            'Bus_2_0.vm_pu',
        ]
    ],
    'line loadings': [
        'line loading in %',
        [
            'LV_Line_0-1_0.loading_percent',
            'LV_Line_1-2_0.loading_percent',
        ]
    ],
}

BINS_BUS_VOLTAGE = [
    round(0.75 + i*.01, 2) for i in range(46)
]

BINS_LINE_LOADING = [
    round(i*5, 2) for i in range(30)
]

BINS_TANK_TEMPERATURE_AVG = [
    round(50 + i*.25, 2) for i in range(40)
]

BINS_TANK_TEMPERATURE_MAX = [
    round(64 + i*.25, 2) for i in range(40)
]

BINS_HP_POWER_CONSUMPTION = [
    round(i*5000, 2) for i in range(22)
]

SHOW_PLOTS = False

FIG_TYPE = 'png' # 'pdf'

FIG_SIZE = [10, 4]


def get_sim_node_name(
    full_name
):
    (sim_name, sim_node) = full_name.split('.')
    return sim_node


def retrieve_results(
    store_name,
    start_time,
    drop_first_days_data = True
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

            if drop_first_days_data:
                first_days_data = data.first('2D')
                results_dict[res_name] = data.drop(first_days_data.index)
            else:
                results_dict[res_name] = data

    results_store.close()
    return results_dict


def plot_results_single_run(
    results_dict, plot_dict,
    fig_id, show = False, fig_type = 'png'
):
    for i, (title, (ylabel, variables)) in enumerate(plot_dict.items()):
        fig, axes = plt.subplots(figsize = FIG_SIZE)
        # fig.tight_layout()
        fmt = '.-' if 'controller' in title else '-'
        for v in variables:
            axes.plot(results_dict[v], fmt, label=v)
            axes.legend(loc = 'upper right')
            axes.set_title(title)
            axes.set_xlabel('date')
            axes.set_ylabel(ylabel)

        plt.savefig('fig_{}_{}.{}'.format(fig_id, title.replace(' ', '_'), fig_type))
        if show == True:
            plt.show()
        plt.close()


def plot_results_compare(
    entity, attr, label,
    label_type1, dict_results_type1,
    label_type2, dict_results_type2,
    fig_id, bins, show = False, fig_type = 'png'
):
    attr_type1 = dict_results_type1['{}.{}'.format(entity, attr)]
    attr_type2 = dict_results_type2['{}.{}'.format(entity, attr)]
    sorted_attr_type1 = attr_type1.sort_values(ascending = False, ignore_index = True)
    sorted_attr_type2 = attr_type2.sort_values(ascending = False, ignore_index = True)

    fig, axes_attr_compare = plt.subplots(figsize = FIG_SIZE)
    # axes_attr_compare.plot(attr_type1, label = '{} {}'.format(entity, label_type1))
    # axes_attr_compare.plot(attr_type2, label = '{} {}'.format(entity, label_type2))
    axes_attr_compare.plot(attr_type1, label = label_type1)
    axes_attr_compare.plot(attr_type2, label = label_type2)
    axes_attr_compare.legend(loc = 'upper right')
    axes_attr_compare.set_xlabel('date')
    axes_attr_compare.set_ylabel(label)

    plt.savefig('fig_{}.{}'.format(fig_id,fig_type))
    if show == True:
        plt.show()
    plt.close()

    fig, axes_sorted_attr_compare = plt.subplots(figsize = FIG_SIZE)
    # axes_sorted_attr_compare.plot(sorted_attr_type1, label = '{} {}'.format(entity, label_type1))
    # axes_sorted_attr_compare.plot(sorted_attr_type2, label = '{} {}'.format(entity, label_type2))
    axes_sorted_attr_compare.plot(sorted_attr_type1, label = label_type1)
    axes_sorted_attr_compare.plot(sorted_attr_type2, label = label_type2)
    axes_sorted_attr_compare.legend(loc = 'upper right')
    axes_sorted_attr_compare.set_ylabel(label)
    axes_sorted_attr_compare.set_title('duration plot of {}'.format(attr))
    plt.savefig('fig_sorted_{}.{}'.format(fig_id,fig_type))
    if show == True:
        plt.show()
    plt.close()

    df_sorted_attr_compare = pd.DataFrame()
    # df_sorted_attr_compare['{} {}'.format(entity, label_type1)] = sorted_attr_type1
    # df_sorted_attr_compare['{} {}'.format(entity, label_type2)] = sorted_attr_type2
    df_sorted_attr_compare[label_type1] = sorted_attr_type1
    df_sorted_attr_compare[label_type2] = sorted_attr_type2
    axes_sorted_attr_compare_hist = df_sorted_attr_compare.plot.hist(bins=bins, alpha=0.5, figsize = FIG_SIZE)
    axes_sorted_attr_compare_hist.set_xlabel(label)
    plt.savefig('fig_hist_{}.{}'.format(fig_id,fig_type))
    if show == True:
        plt.show()
    plt.close()

    return (attr_type1.sum(), attr_type2.sum())


if __name__ == '__main__':
    # Retrieve results for simulation with voltage control enabled.
    dict_results_ctrl_enabled = retrieve_results(
        'benchmark_results_ctrl_enabled.h5',
        START_TIME, DROP_FIRST_DAYS_DATA
        )

    # Retrieve results for simulation with voltage control disabled.
    dict_results_ctrl_disabled = retrieve_results(
        'benchmark_results_ctrl_disabled.h5',
        START_TIME, DROP_FIRST_DAYS_DATA
        )

    # Plot results for simulation with voltage control enabled.
    plot_results_single_run(
        dict_results_ctrl_enabled, PLOT_DICT,
        'ts_ctrl_enabled', SHOW_PLOTS, FIG_TYPE
        )

    # Plot results for simulation with voltage control disabled.
    plot_results_single_run(
        dict_results_ctrl_disabled, PLOT_DICT,
        'ts_ctrl_disabled', SHOW_PLOTS, FIG_TYPE
        )

    # Compare voltage levels for bus 1.
    plot_results_compare(
        'Bus_1_0', 'vm_pu', 'voltage in p.u.',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'voltage_levels_bus1', BINS_BUS_VOLTAGE, SHOW_PLOTS, FIG_TYPE
        )

    # Compare voltage levels for bus 2.
    plot_results_compare(
        'Bus_2_0', 'vm_pu', 'voltage in p.u.',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'voltage_levels_bus2', BINS_BUS_VOLTAGE, SHOW_PLOTS, FIG_TYPE
        )

    # Compare line loadings for line 1.
    plot_results_compare(
        'LV_Line_0-1_0', 'loading_percent', 'line loading in %',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'loadings_line1', BINS_LINE_LOADING, SHOW_PLOTS, FIG_TYPE
        )

    # Compare line loadings for line 2.
    plot_results_compare(
        'LV_Line_1-2_0', 'loading_percent', 'line loading in %',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'loadings_line2', BINS_LINE_LOADING, SHOW_PLOTS, FIG_TYPE
        )

    # Average tank temperature.
    plot_results_compare(
        'DHNetwork_0', 'thermalNetwork_powerToHeat_T_tank_mean_degC', 'average temperature in °C',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'tank_temperature_avg', BINS_TANK_TEMPERATURE_AVG, SHOW_PLOTS, FIG_TYPE
        )

    # Maximum tank temperature.
    plot_results_compare(
        'DHNetwork_0', 'T_tank_high_degC', 'maximum temperature in °C',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'tank_temperature_max', BINS_TANK_TEMPERATURE_MAX, SHOW_PLOTS, FIG_TYPE
        )

    # Compare power consumption of heat pump.
    plot_results_compare(
        'DHNetwork_0', 'PID_controller_u_m', 'heat generation in W',
        'ctrl enabled', dict_results_ctrl_enabled,
        'ctrl disabled', dict_results_ctrl_disabled,
        'heat_pump_power', BINS_HP_POWER_CONSUMPTION, SHOW_PLOTS, FIG_TYPE
        )

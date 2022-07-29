'''
Analysis script for the benchmark results, comparing
results with voltage control enabled and disabled.
'''

import matplotlib.pyplot as plt
import pandas as pd

START_TIME = '2019-02-01 00:00:00'

DROP_FIRST_DAY_DATA = True

FIG_SIZE = [10, 4]

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
#    'electrical consumption': [
#        'electrical consumption in MW',
#        [
#            'Load_1_0.p_mw',
#            'Load_2_0.p_mw',
#        ]
#    ],
#    'PV generation': [
#        'PV generation in MW',
#        [
#            'PV_1_0.p_mw',
#            'PV_2_0.p_mw',
#        ]
#    ],
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


def get_sim_node_name(
    full_name
):
    (sim_name, sim_node) = full_name.split('.')
    return sim_node


def retrieve_results(
    store_name,
    start_time = START_TIME,
    drop_first_day_data = DROP_FIRST_DAY_DATA
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
                first_day_data = data.first('1D')
                results_dict[res_name] = data.drop(first_day_data.index)
            else:
                results_dict[res_name] = data

    results_store.close()
    return results_dict


def plot_results_single_run(
    results_dict, 
    plot_dict = PLOT_DICT
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

        plt.show()
        plt.close()


def plot_results_compare(
    entity, attr, label, bins,
    label_type1, dict_results_type1,
    label_type2, dict_results_type2
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
    plt.show()
    plt.close()

    df_sorted_attr_compare = pd.DataFrame()
    # df_sorted_attr_compare['{} {}'.format(entity, label_type1)] = sorted_attr_type1
    # df_sorted_attr_compare['{} {}'.format(entity, label_type2)] = sorted_attr_type2
    df_sorted_attr_compare[label_type1] = sorted_attr_type1
    df_sorted_attr_compare[label_type2] = sorted_attr_type2
    axes_sorted_attr_compare_hist = df_sorted_attr_compare.plot.hist(bins=bins, alpha=0.5, figsize = FIG_SIZE)
    axes_sorted_attr_compare_hist.set_xlabel(label)
    plt.show()
    plt.close()

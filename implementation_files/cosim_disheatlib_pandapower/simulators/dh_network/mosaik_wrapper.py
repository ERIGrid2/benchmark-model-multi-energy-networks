from .mosaik_fmi import FmuAdapter
import pathlib
import sys

def translate_var_name(var_name):
    alt_name = var_name
    translate_map = {'.': '_', '[': '_', ']': ''}
    for _from, _to in translate_map.items():
        alt_name = alt_name.replace(_from, _to)
    return alt_name

class DHNetworkSimulator(FmuAdapter):

    DEFAULT_VAR_TABLE = {
        'input': {
            'mdot_tank_out': 'Real',
            'P_el_heatpump_setpoint_kW': 'Real',
        },
        'output': {
            'T_tank_high_degC': 'Real',
            'T_tank_low_degC': 'Real',
            'P_el_heatpump_MW': 'Real',
        },
        'parameter': {
        }
    }

    def init(self, sid, step_size = 60, additional_output_table = None, additional_param_table = None, logging_on = False):

        work_dir = pathlib.Path(__file__).resolve().parent

        # Use different FMUs for different platforms.
        if 'win' in sys.platform:
            fmu_name = 'DHNetworkMassFlowControlled_win64'
            model_name = 'DHNetworkMassFlowControlled_win64'
        elif 'linux' in sys.platform:
            fmu_name = 'DHNetworkMassFlowControlled_linux64'
            model_name = 'DHNetworkMassFlowControlled_linux64'
        else:
            raise Exception('platform not supported')

        instance_name = 'DHNetwork'
        fmi_type = 'CoSimulation'
        fmi_version = '2'

        var_table = self.DEFAULT_VAR_TABLE.copy()
        if not additional_output_table is None:
            var_table['output'] = {**var_table['output'], **additional_output_table}
        if not additional_param_table is None:
            var_table['parameter'] = {**var_table['parameter'], **additional_param_table}

        translation_table = {}
        for causality in ['input', 'output', 'parameter']:
            translation_table[causality] = {}
            for var_name, var_type in var_table[causality].items():
                if '.' in var_name:
                    alt_name = translate_var_name(var_name)
                else:
                    alt_name = var_name
                translation_table[causality][alt_name] = var_name

        meta = FmuAdapter.init(self, sid, work_dir = work_dir, fmu_name = fmu_name, model_name = model_name,
            instance_name = instance_name, fmi_type = fmi_type, step_size = step_size, logging_on = logging_on,
            fmi_version = fmi_version, var_table = var_table, translation_table = translation_table)


        if 'linux' in sys.platform:
            self.copy_data_files_to_current_work_dir()
            raise Exception('breakpoint')

        return meta


    def copy_data_files_to_current_work_dir(self):
    '''
    The FMU for platform 'linux64' has been generated with Dymola version 2019 FD01.
    The generated FMUs fail to load data files from the resources folder.
    As a workaround, the data files have to copied to the current working directory by hand.
    '''
        import os, shutil, glob
        data_files_wildcard = pathlib.Path(self.work_dir, self.fmu_name, 'resources', '*')
        for file in glob.glob(str(data_files_wildcard)):
            shutil.copy(file, os.getcwd())

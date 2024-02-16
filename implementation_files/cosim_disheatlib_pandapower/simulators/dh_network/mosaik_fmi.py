import itertools
import os
import mosaik_api
import fmipp
from .parse_xml import get_var_table, get_fmi_version

meta = {
    'models': {},
    'extra_methods': ['fmi_set', 'fmi_get']
}

'''
var_table = {
    'parameter': {
        'a': 'Real',
        'b': 'Integer',
        'c': 'Boolean',
        'd': 'String'
    },
    'input': {
        'x': 'Real',
        ...
    },
    'output': {
        ...
    }
}
'''


class FmuAdapter(mosaik_api.Simulator):
    '''Mosaik adapter for simulators following the FMI for Co-Simulation / ModelExchange standard.'''

    def __init__(self):
        super(FmuAdapter, self).__init__(meta)
        self.sid = None

        self._entities = {}
        self.eid_counters = {}

        # TODO Is it really bad style not to initialize the instance variables here?
        # self.work_dir = None
        # self.model_name = None
        # self.instance_name = None
        # self.var_table = None
        # self.translation_table = None
        # self.step_size = None
        # self.logging_on = False
        # self.time_diff_resolution = 1e-9
        # self.interactive = False
        # self.visible = False
        # self.start_time = 0
        # self.stop_time = 10000
        # self.stop_time_defined = False
        # self.uri_to_extracted_fmu = None
        # self.setp_factor = None
        # self.fmi_version = 1  #default

    def init(self, sid, work_dir=None, fmu_name=None, model_name=None, instance_name=None, fmi_type=None, step_size=1, logging_on=False,
             step_factor=1.0, fmi_version=None, var_table=None, translation_table=None,
             time_diff_resolution=1e-9, interactive=False, visible=False, stop_time_defined=False, stop_time=10000,
             integrator='integratorCK', stop_before_event=False, event_search_precision=1e-10):

        if work_dir is None or model_name is None or fmu_name is None or instance_name is None or fmi_type is None:
            raise RuntimeError("FMI Adapter has to be initialized with work_dir, fmu_name, model_name, instance_name, and fmi_type!")
        self.sid = sid

        self.work_dir = work_dir  # path to directory of the FMU
        self.fmu_name = fmu_name
        self.model_name = model_name
        self.instance_name = instance_name
        self.step_size = step_size
        self.step_factor = step_factor  # Factor to translate mosaik integer time into FMI float time
        self.logging_on = logging_on
        #self.fmi_version = fmi_version

        # Co-simulation-specific variables:
        self.start_time = 0
        self.time_diff_resolution = time_diff_resolution
        self.interactive = interactive
        self.visible = visible
        self.stop_time_defined = stop_time_defined
        self.stop_time = stop_time

        # ModelExchange-specific variables:
        self.stop_before_event = stop_before_event
        self.integrator = getattr(fmipp, integrator)  # FMU for ME require integrators, fmipp provides a selection
        self.event_search_precision = event_search_precision

        # Extracting files from the .fmu (only needed at first use, but will not cause error later)
        path_to_fmu = os.path.join(self.work_dir, self.fmu_name + '.fmu')
        self.uri_to_extracted_fmu = fmipp.extractFMU(path_to_fmu, self.work_dir)
        if not self.uri_to_extracted_fmu:
            self.uri_to_extracted_fmu = os.path.join(self.work_dir, self.fmu_name)

        # FMU variables may be either given by the user or are read automatically from FMU description file:
        xmlfile = os.path.join(self.work_dir, self.fmu_name, 'modelDescription.xml')
        if var_table is None:
            self.var_table, self.translation_table = get_var_table(xmlfile)
        else:
            self.var_table = var_table
            self.translation_table = translation_table  # If variables are specified by hand, a translation table  #
            # also has to be given (in case some FMI variable names are not python-conform)

        if fmi_type in ["cs", "CoSimulation"]:
            self.fmi_type = "CoSimulation"
        elif fmi_type in ["me", "ModelExchange"]:
            self.fmi_type = "ModelExchange"
        else:
            raise RuntimeError("FMI adapter has to be initialized with fmi_type "
                               "(\"cs\", \"CoSimulation\", \"me\", \"ModelExchange\")!")

        self.fmi_version = get_fmi_version(xmlfile)
        if fmi_version and fmi_version != self.fmi_version:
            raise RuntimeError("User-given FMI version (v{}) does not agree with that from the "
                                   "modelDescriptionn.xml (v{})!".format(fmi_version, self.fmi_version))

        self.adjust_var_table()  # Completing var_table and translation_table structure
        self.adjust_meta()  # Writing variable information into mosaik's meta

        return self.meta

    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, itertools.count())

        entities = []

        for i in range(num):
            eid = '%s_%s' % (model, next(counter))

            f_open_fmu = getattr(fmipp, "FMU"+self.fmi_type+"V" + str(self.fmi_version))

            if self.fmi_type=="CoSimulation":
                attrs_open = [self.time_diff_resolution]
                attrs_inst = [self.start_time, self.visible, self.interactive]
                attrs_init = [self.start_time, self.stop_time_defined, self.stop_time]
            elif self.fmi_type=="ModelExchange":
                attrs_open = [self.stop_before_event, self.event_search_precision, self.integrator]
                attrs_inst = []
                attrs_init = []

            fmu = f_open_fmu(self.uri_to_extracted_fmu, self.model_name, self.logging_on, *attrs_open)
            self._entities[eid] = fmu
            inst_stat = self._entities[eid].instantiate(self.instance_name, *attrs_inst)
            assert inst_stat == fmipp.statusOK
            self.set_values(eid, model_params, 'parameter')
            init_stat = self._entities[eid].initialize(*attrs_init)
            assert init_stat == fmipp.statusOK

            entities.append({'eid': eid, 'type': model, 'rel': []})

        return entities

    def step(self, t, inputs=None):
        if self.fmi_type=="CoSimulation":
            # If no input data is provided, all entities are stepped:
            if inputs is None or inputs == {}:
                for fmu in self._entities.values():
                    step_stat = fmu.doStep(t * self.step_factor, self.step_size * self.step_factor, True)
                    assert step_stat == fmipp.statusOK

            else:
                for eid, attrs in inputs.items():
                    for attr, vals in attrs.items():
                        for val in vals.values():
                            self.set_values(eid, {attr: val}, 'input')

                    step_stat = self._entities[eid].doStep(t * self.step_factor, self.step_size * self.step_factor, True)
                    assert step_stat == fmipp.statusOK

            return t + self.step_size

        elif self.fmi_type=="ModelExchange":
            # If no input data is provided, all entities are stepped:
            if inputs is None or inputs == {}:
                for fmu in self._entities.values():
                    stepped_time = fmu.integrate((t + self.step_size) * self.step_factor)

            else:
                for eid, attrs in inputs.items():
                    for attr, vals in attrs.items():
                        for val in vals.values():
                            self.set_values(eid, {attr: val}, 'input')

                    stepped_time = self._entities[eid].integrate((t + self.step_size) * self.step_factor)

            return stepped_time

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                data[eid][attr] = self.get_value(eid, attr)

        return data

    # doesn't work:
    # def finalize(self):
    #     for entity in self._entities.values():
    #         entity.terminate()

    def adjust_var_table(self):
        '''Help function that completes the structure of var_table and translation_tabel. Both require listing of
        the three variable types, parameter, input and output.'''
        self.var_table.setdefault('parameter', {})
        self.var_table.setdefault('input', {})
        self.var_table.setdefault('output', {})

        # A translation table is needed since sometimes FMU variable names are not accepted by mosaik
        # (e.g. containing a period)
        self.translation_table.setdefault('parameter', {})
        self.translation_table.setdefault('input', {})
        self.translation_table.setdefault('output', {})

    def adjust_meta(self):
        '''Help function that writes FMU variable names into the mosaik meta structure.'''
        # FMU inputs and outputs are translated to attributes in mosaik
        attr_list = list(self.translation_table['input'].keys())
        out_list = list(self.translation_table['output'].keys())
        attr_list.extend(out_list)

        self.meta['models'][self.instance_name] = {
            'public': True,
            'params': list(self.translation_table['parameter'].keys()),
            'attrs': attr_list
        }

    def set_values(self, eid, val_dict, var_type):
        '''Help function to set values to a given variable of an FMU. This is done via a "var_table" and a
        "translation_table" to avoid problems due to missmatching naming conventions in mosaik and FMI.'''
        for alt_name, val in val_dict.items():
            name = self.translation_table[var_type][alt_name]
            set_func = getattr(self._entities[eid], 'set' + self.var_table[var_type][name] + 'Value')
            set_stat = set_func(name, val)
            assert set_stat == fmipp.statusOK

    def get_value(self, eid, alt_attr):
        '''Help function to get values from given variables of an FMU.'''
        attr = self.translation_table['output'][alt_attr]
        get_func = getattr(self._entities[eid], 'get' + self.var_table['output'][attr] + 'Value')
        val = get_func(attr)
        return val

    def fmi_set(self, entity, var_name, value, var_type='input'):
        '''Extra function to allow explicit setting by user in scenario file.'''
        var_dict = {var_name: value}
        self.set_values(entity.eid, var_dict, var_type)

    def fmi_get(self, entity, var_name):
        '''Extra function to allow explicit getting by user in scenario file.'''
        val = self.get_value(entity.eid, var_name)
        return val

# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
Model of the voltage controller.
'''

from itertools import count
from .simulator import VoltageController
from mosaik_api import Simulator
from typing import Dict

META = {
    'models': {
        'VoltageController': {
            'public': True,
            'params': [
                'delta_vm_upper_pu',
                'delta_vm_lower_pu_hp_on',
                'delta_vm_lower_pu_hp_off',
                'delta_vm_deadband',
                'hp_p_el_mw_rated',
                'hp_p_el_mw_min',
                'hp_p_el_mw_step',
                'hp_operation_steps_min',
                'k_p',
            ],
            'attrs': [
                # Inputs
                'vmeas_pu',
                # Output
                'hp_p_el_kw_setpoint',
                'hp_p_el_mw_setpoint'
            ],
        },
    },
}


class VoltageControlSimulator(Simulator):

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[VoltageController] = {}
        self.entityparams = {}
        self.output_vars = {'hp_p_el_kw_setpoint','hp_p_el_mw_setpoint'}
        self.input_vars = {'vmeas_pu'}

    def init(self, sid, step_size=10, eid_prefix="VoltageController"):

        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta

    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):

            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = VoltageController(**model_params)

            self.simulators[eid] = esim

            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs):
        for eid, esim in self.simulators.items():
            data = inputs.get(eid, {})

            for attr, incoming in data.items():
                if attr in self.input_vars:

                    if 1 != len(incoming):
                        raise RuntimeError('VoltageControlSimulator does not support multiple inputs')

                    newval = list(incoming.values())[0]
                    setattr(esim, attr, newval)

                else:
                    raise AttributeError(f"VoltageControlSimulator {eid} has no input attribute {attr}.")

            esim.step_single(time)

        self.last_time = time

        return time + self.step_size

    def get_data(self, outputs):
        data = {}

        for eid, esim in self.simulators.items():
            requests = outputs.get(eid, [])
            mydata = {}

            for attr in requests:
                if attr in self.input_vars or attr in self.output_vars:
                    mydata[attr] = getattr(esim, attr)
                else:
                    raise AttributeError(f"VoltageControlSimulator {eid} has no attribute {attr}.")
            data[eid] = mydata
        return data


if __name__ == '__main__':
    test = VoltageControlSimulator()

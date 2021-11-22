# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
Model of the power-to-heat facility controller.
'''

from itertools import count
from .simulator import SimpleFlexHeatController
from mosaik_api import Simulator
from typing import Dict

META = {
    'models': {
        'SimpleFlexHeatController': {
            'public': True,
            'params': ['voltage_control_enabled'],
            'attrs': [
                # Input
                'mdot_HEX1', 'mdot_HEX2', 'T_tank_hot', 'T_hp_cond_in', 'T_hp_cond_out', 'T_hp_evap_in', 'T_hp_evap_out',
                'P_hp_el_setpoint', 'P_hp_effective',
                # Output
                'mdot_1_supply', 'mdot_2_supply', 'mdot_3_supply',
                'mdot_1_return', 'mdot_2_return', 'mdot_3_return',
                'mdot_HP_out', 'mdot_tank_in',
                'hp_on_request', 'hp_off_request', 'state'
                ],
            },
        },
    }


class SimpleFlexHeatControllerSimulator(Simulator):

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[SimpleFlexHeatController] = {}
        self.entityparams = {}
        self.output_vars = {'mdot_1_supply', 'mdot_2_supply', 'mdot_3_supply', 'mdot_1_return', 'mdot_2_return', 'mdot_3_return', 'Q_HP_set', 'mdot_HP_out', 'mdot_tank_in', 'hp_on_request', 'hp_off_request', 'state'}
        self.input_vars = {'mdot_HEX1', 'mdot_HEX2', 'T_tank_hot', 'T_hp_cond_in', 'T_hp_cond_out', 'T_hp_evap_in', 'T_hp_evap_out', 'P_hp_el_setpoint', 'P_hp_effective'}

    def init(self, sid, step_size=10, eid_prefix="FHctrl"):
        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta


    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):
            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = SimpleFlexHeatController(**model_params)

            self.simulators[eid] = esim

            entities.append({'eid': eid, 'type': model})

        return entities


    def step(self, time, inputs):

        for eid, esim in self.simulators.items():

            data = inputs.get(eid, {})

            for attr, incoming in data.items():
                if attr in self.input_vars:
                    if 1 != len(incoming):
                        raise RuntimeError('SimpleFlexHeatControllerSimulator does not support multiple inputs')

                    if 'mdot' in attr:
                        newval = -list(incoming.values())[0] # Reverse the sign of incoming mass flow values
                    else:
                        newval = list(incoming.values())[0]

                    setattr(esim, attr, newval)
                else:
                    raise AttributeError(f"SimpleFlexHeatControllerSimulator {eid} has no input attribute {attr}.")

            esim.step_single()

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
                    raise AttributeError(f"SimpleFlexHeatControllerSimulator {eid} has no attribute {attr}.")

            data[eid] = mydata

        return data


if __name__ == '__main__':

    test = SimpleFlexHeatControllerSimulator()

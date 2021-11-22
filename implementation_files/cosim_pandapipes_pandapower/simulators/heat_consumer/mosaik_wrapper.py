# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
Model of the heat exchanger substation at the consumer side.
'''

from itertools import count
from .simulator import HEXConsumer
from mosaik_api import Simulator
from typing import Dict

META = {
    'models': {
        'HEXConsumer': {
            'public': True,
            'params': [
                'T_return_target', 'P_heat', 'mdot_hex_in', 'mdot_hex_out',
            ],
            'attrs': [
                # Input
                'P_heat', 'T_supply',
                # Output
                'mdot_hex_out', 'mdot_hex_in', 'T_return'
            ],
        },
    },
}


class HEXConsumerSimulator(Simulator):

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[HEXConsumer] = {}
        self.entityparams = {}
        self.output_vars = {'mdot_hex_out', 'mdot_hex_in', 'T_return'}
        self.input_vars = {'P_heat', 'T_supply'}

    def init(self, sid, step_size=10, eid_prefix="HEXConsumer"):

        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta

    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):

            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = HEXConsumer(**model_params)

            self.simulators[eid] = esim

            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs):
        for eid, esim in self.simulators.items():
            data = inputs.get(eid, {})

            for attr, incoming in data.items():
                if attr in self.input_vars:
                    if 1 != len(incoming):
                        raise RuntimeError('HEXConsumerSimulator does not support multiple inputs')

                    newval = list(incoming.values())[0]
                    setattr(esim, attr, newval)

                else:
                    raise AttributeError(f"HEXConsumerSimulator {eid} has no input attribute {attr}.")

            for _ in range(time - self.last_time):
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
                    raise AttributeError(f"HEXConsumerSimulator {eid} has no attribute {attr}.")
            data[eid] = mydata
        return data


if __name__ == '__main__':
    test = HEXConsumerSimulator()

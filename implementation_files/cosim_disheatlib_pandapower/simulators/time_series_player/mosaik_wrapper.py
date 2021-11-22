# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from itertools import count
from .simulator import TimeSeriesPlayer
from mosaik_api import Simulator
from typing import Dict

META = {
    'models': {
        'TimeSeriesPlayer': {
            'public': True,
            'params': [
                't_start', 'series', 'fieldname', 'interp_method', 'scale'
            ],
            'attrs': [
                # Output
                'out',
            ],
        },
    },
}


class TimeSeriesPlayerSim(Simulator):

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[str, TimeSeriesPlayer] = {}
        self.entityparams = {}
        self.output_vars = {'out'}
        self.input_vars = {}

    def init(self, sid, step_size = 10, eid_prefix = 'TimeSeriesPlayer'):

        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta

    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):
            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = TimeSeriesPlayer(step_size = self.step_size,**model_params)

            self.simulators[eid] = esim

            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs):
        for eid, esim in self.simulators.items():
            data = inputs.get(eid, {})
            if not 0 == len(data):
                RuntimeError('TimeSeriesPlayerSimulator has no input attributes.')

            esim.step_single(t=time)

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
                    raise AttributeError(f"TimeSeriesPlayerSimulator {eid} has no attribute {attr}.")
            data[eid] = mydata

        return data


if __name__ == '__main__':

    test = TimeSeriesPlayerSimulator()

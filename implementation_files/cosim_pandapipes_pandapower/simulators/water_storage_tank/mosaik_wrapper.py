# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from itertools import count
from .simulator import WaterStorageTank
from mosaik_api import Simulator
from typing import Dict
from statistics import mean

META = {
    'models': {
        'WaterStorageTank': {
            'public': True,
            'params': [
                'INNER_HEIGHT', 'INNER_DIAMETER', 'INSULATION_THICKNESS', 'STEEL_THICKNESS', 'NB_LAYERS',
                'T_volume_initial','dt'
                ],
            'attrs': [
                # Input
                'mdot_ch_in', 'mdot_dis_out', 'T_ch_in', 'T_dis_in',
                # Output
                'T_hot', 'T_cold', 'T_avg', 'mdot_ch_out', 'mdot_dis_in'
                ],
            },
        },
    }


class StratifiedWaterStorageTankSimulator(Simulator):
    '''
    Models a stratified water storage tank.
    '''

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[WaterStorageTank] = {}
        self.entityparams = {}
        self.output_vars = {'T_hot', 'T_cold', 'T_avg', 'mdot_ch_out', 'mdot_dis_in'}
        self.input_vars = {'mdot_ch_in', 'mdot_dis_out', 'T_ch_in', 'T_dis_in'}


    def init(self, sid, step_size=10, eid_prefix="StratifiedWaterStorageTank"):

        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta


    def create(self, num, model, **model_params):

        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):

            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = WaterStorageTank(**model_params)

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
                    raise AttributeError(f"StratifiedWaterStorageTankSimulator {eid} has no input attribute {attr}.")

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
                    if attr == 'T_avg':
                        mydata[attr] = mean(esim.Layers_temperature_dict.values())
                    elif 'T' in attr:
                        mydata[attr] = getattr(esim, attr)  # Convert local degK to degC for sending into the co-simulation flow
                    else:
                        mydata[attr] = getattr(esim, attr)
                else:
                    raise AttributeError(f"StratifiedWaterStorageTankSimulator {eid} has no attribute {attr}.")
            data[eid] = mydata

        return data


if __name__ == '__main__':

    test = StratifiedWaterStorageTankSimulator()

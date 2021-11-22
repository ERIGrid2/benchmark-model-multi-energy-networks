# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from itertools import count
from .simulator import DHNetwork
from mosaik_api import Simulator
from typing import Dict

META = {
    'models': {
        'DHNetwork': {
            'public': True,
            'params': [
                'T_amb',  # Ambient ground temperature
                'enable_logging',
                'T_supply_grid',
                'P_grid_bar',
                'dynamic_temp_flow_enabled',
                ],
            'attrs': [
                # Input
                'T_tank_forward',  # Supply temp of storage unit
                'mdot_tank_in_set',  # Mass flow injected by tank
                'mdot_grid_set',  # Mass flow injected by the grid
                'mdot_cons1_set',  # Mass flow at consumer 1
                'mdot_cons2_set',  # Mass flow at consumer 2
                'Qdot_evap',  # Heat consumption of heat pump evaporator
                'Qdot_cons1',  # Heat consumption of consumer 1
                'Qdot_cons2',  # Heat consumption of consumer 2
                # Output
                'T_supply_grid',  # Supply temperature of the external grid
                'T_return_grid',  # Return temperature of the external grid
                'T_return_tank',  # Return temperature of the storage unit
                'T_evap_in',  # Return temperature towards the heat pump evaporator
                'T_supply_cons1',  # Supply temperature at consumer 1
                'T_supply_cons2',  # Supply temperature at consumer 2
                'T_return_cons1',  # Return temperature at consumer 1
                'T_return_cons2',  # Return temperature at consumer 2
                'mdot_tank_in',  # Mass flow injected by tank
                'mdot_grid',  # Mass flow injected by the grid
                'mdot_cons1',  # Mass flow at consumer 1
                'mdot_cons2',  # Mass flow at consumer 2
                'mdot_bypass',  # Mass flow at consumer 2
                'P_supply_cons1',  # Supply pressure at consumer 1
                'P_supply_cons2',  # Supply pressure at consumer 2
                'P_return_cons1',  # Return pressure at consumer 1
                'P_return_cons2',  # Return pressure at consumer 2
                ],
            },
        },
    }


class DHNetworkSimulator(Simulator):

    step_size = 10
    eid_prefix = ''
    last_time = 0

    def __init__(self, META=META):
        super().__init__(META)

        # Per-entity dicts
        self.eid_counters = {}
        self.simulators: Dict[DHNetwork] = {}
        self.entityparams = {}
        self.output_vars = {'T_return_tank', 'T_evap_in', 'T_return_grid', 'T_supply_cons1', 'T_supply_cons2', 'T_return_cons1', 'T_return_cons2',
                            'P_supply_cons1', 'P_supply_cons2', 'P_return_cons1', 'P_return_cons2',
                            'mdot_tank_in', 'mdot_grid', 'mdot_cons1', 'mdot_cons2', 'mdot_bypass'}
        self.input_vars = {'mdot_grid_set', 'T_tank_forward', 'mdot_tank_in_set', 'mdot_cons1_set', 'mdot_cons2_set', 'Qdot_evap', 'Qdot_cons1', 'Qdot_cons2'}

    def init(self, sid, step_size=10, eid_prefix="DHNetwork"):
        self.step_size = step_size
        self.eid_prefix = eid_prefix

        return self.meta


    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, count())
        entities = []

        for _ in range(num):

            eid = '%s_%s' % (self.eid_prefix, next(counter))

            self.entityparams[eid] = model_params
            esim = DHNetwork(**model_params)

            self.simulators[eid] = esim

            entities.append({'eid': eid, 'type': model})

        return entities


    def step(self, time, inputs):

        for eid, esim in self.simulators.items():
            data = inputs.get(eid, {})

            for attr, incoming in data.items():
                if attr in self.input_vars:

                    if 1 != len(incoming):
                        raise RuntimeError('DHNetworkSimulator does not support multiple inputs')
                    
                    if 'mdot' in attr:
                        newval = -list(incoming.values())[0]  # Reverse the sign of incoming mass flow values
                    else:
                        newval = list(incoming.values())[0]

                    setattr(esim, attr, newval)

                else:
                    raise AttributeError(f"DHNetworkSimulator {eid} has no input attribute {attr}.")

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
                    raise AttributeError(f"DHNetworkSimulator {eid} has no attribute {attr}.")

            data[eid] = mydata

        return data


if __name__ == '__main__':

    test = DHNetworkSimulator()

# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
'''
A simple data collector that prints all data when the simulator ends.
'''

import collections
import mosaik_api
import pandas as pd

META = {
        'models': {
                'Collector': {
                    'public': True,
                    'any_inputs': True,
                    'params': [],
                    'attrs': [],
                    },
            },
    }


def _format_func(x):
    try:
        return '{0:.02f}'.format(x)
    except TypeError:
        return str(x)


class Collector(mosaik_api.Simulator):

    print_results = True
    save_h5 = True
    h5_store_name = ''
    h5_frame_name = ''

    def __init__(self):
        super().__init__(META)
        self.eid = None
        self.data = collections.defaultdict(
                lambda: collections.defaultdict(list))
        self.time_list=[]

        self.step_size = None

    def init(
            self, sid, step_size=10, print_results=True, save_h5=True,
            h5_store_name='collector_store', h5_frame_name='default_frame'):
        self.step_size = step_size
        self.print_results = print_results
        self.save_h5 = save_h5
        self.h5_store_name = h5_store_name
        self.h5_frame_name = h5_frame_name
        return self.meta

    def create(self, num, model, **entity_params):
        if num > 1 or self.eid is not None:
            raise RuntimeError("Can only create one instance of Collector per simulator.")

        self.eid = 'Collector'
        if self.h5_frame_name is None: self.h5_frame_name = self.eid
        return [{'eid': self.eid, 'type': model}]

    def step(self, time, inputs):
        data = inputs.get(self.eid,{})
        for attr, values in data.items():
            for src, value in values.items():
                self.data[src][attr].append(value)
        self.time_list.append(time)

        return time + self.step_size

    def get_data(self, outputs):
        raise NotImplementedError('Collector does not allow data to be pulled from it')

    def finalize(self):
        if self.print_results:
            print('Collected data:')
            for sim, sim_data in self.data.items():
                print('- {0}'.format(sim))
                for attr, values in sorted(sim_data.items()):
                    print('  - {0}: {1}'.format(attr, list(map(_format_func, values))))
        if self.save_h5:
            store = pd.HDFStore(self.h5_store_name)
            panel = pd.DataFrame({(unit,attribute): pd.Series(data, index=self.time_list) for unit, datadict in self.data.items() for attribute, data in datadict.items()})
            #print(panel)
            print('Saved to store: {0}, dataframe: {1}'.format(self.h5_store_name, self.h5_frame_name))
            store[self.h5_frame_name] = panel
            store.close()


if __name__ == '__main__':
    mosaik_api.start_simulation(Collector())

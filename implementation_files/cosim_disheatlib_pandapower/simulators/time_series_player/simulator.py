# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import pandas as pd
from pandas.tseries.offsets import DateOffset
from dataclasses import dataclass
import datetime

@dataclass
class TimeSeriesPlayer:
    '''
    Time series simulator that plays a given time series at the given date.
    '''

    # Parameters
    t_start: datetime.datetime = None
    fieldname: str = 'in'  # Name of the field in the dataframe to use.
    step_size: int = None
    interp_method: str = 'linear'
    scale: float = 1.

    # Variables
    ## Internal
    cur_t: datetime.datetime = None

    ## Input
    series: pd.DataFrame() = None

    ## Output
    out: float = None


    def __post_init__(self):
        self.sim_check()
        self.step_single(0)


    def sim_check(self):
        self.t_start = pd.to_datetime(self.t_start)
        self.cur_t = self.t_start

        # Retrieve original index from time series.
        index = self.series[self.fieldname].index
        
        # Calculate index required for given step size.
        step_size_index = pd.date_range(index[0], index.values[-1], freq=DateOffset(seconds=self.step_size))

        # Check if original index and index required for step size are the same.
        if not index.equals(step_size_index):
            # Re-index and interpolate the time series.
            new_index = index.union(step_size_index)
            self.series = self.series.reindex(new_index).interpolate(method=self.interp_method)

        assert self.t_start in self.series.index, "Simulation starting date: \"{0}\", is not in time series input.".format(self.t_start)


    def step_single(self, t):
            '''
            Method to update the time series simulator output
            input: simulation time
            output: time series value
            '''
            self.cur_t = self.t_start + pd.Timedelta(seconds=t)

            if self.cur_t in self.series.index:
                self.out = self.scale * self.series[self.fieldname][self.cur_t]

            else:
                raise RuntimeError('timestamp not available')


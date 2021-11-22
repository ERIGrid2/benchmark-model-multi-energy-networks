# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import numpy as np
import pandapower.control as control
from simple_pid import PID
# import matplotlib.pyplot as plt
# import time


class CtrlValve(control.basic_controller.Controller):
    """
    Example class of a Valve-Controller. Models an abstract control valve.
    """

    def __init__(self, net, gid, data_source=None, profile_name=None, in_service=True, enable_plotting=False,
                 mdot_set_kg_per_s=0, gain=-1000,
                 recycle=True, order=0, level=0, tol=0, **kwargs):
        super().__init__(net, in_service=in_service, recycle=recycle, order=order, level=level,
                         initial_powerflow=True, **kwargs)

        # read generator attributes from net
        self.gid = gid  # index of the controlled storage
        self.from_junction = net.valve.at[gid, "from_junction"]
        self.to_junction = net.valve.at[gid, "to_junction"]
        self.diameter = net.valve.at[gid, "diameter_m"]
        self.loss_coeff = net.valve.at[gid, "loss_coefficient"]
        self.opened = net.valve.at[gid, "opened"]
        self.name = net.valve.at[gid, "name"]
        self.gen_type = net.valve.at[gid, "type"]
        # self.mdot_from_kg_per_s = net.res_valve.at[gid, "mdot_from_kg_per_s"]
        # self.in_service = net.valve.at[gid, "in_service"]
        self.applied = False

        # specific attributes
        self.mdot_set_kg_per_s = mdot_set_kg_per_s
        self.method = 'euler'
        self.tolerance = tol  # absolute tolerance
        self.i = 0

        # profile attributes
        self.data_source = data_source
        self.profile_name = profile_name
        self.last_time_step = None

        # init pid control
        self.pid = PID(gain, 0, 0)
        self.pid.output_limits = (None, None)  # Output will always be above 0, but with no upper bound
        self.loss_coeff_min = 0
        self.loss_coeff_max = 1e6

        # # init plot
        # self.enable_plotting = enable_plotting

    def initialize_control(self, net):
        """
        At the beginning of each run_control call reset applied-flag
        """
        self.pid.setpoint = self.mdot_set_kg_per_s
        self.i = 0

        # # clear plot
        # if self.enable_plotting == True:
            # self.axes = plt.gca()
            # self.axes.set_xlim(0, 100)
            # self.axes.set_ylim(0, 1)
            # self.xdata = []
            # self.ydata = []
            # self.line, = self.axes.plot([], [], 'b')

    # Also remember that 'is_converged()' returns the boolean value of convergence:
    def is_converged(self, net):
        mdot = np.nan_to_num(net.res_valve.at[self.gid, 'mdot_from_kg_per_s'])
        mdot_set = self.mdot_set_kg_per_s
        name = self.name

        # Set absolute tolerance
        loTol = mdot_set - self.tolerance
        upTol = mdot_set + self.tolerance

        if loTol <= mdot <= upTol:
            # plt.show()
            self.applied = True
            # print(f'Valve {self.name} successfully adjusted.')
        else:
            self.applied = False
        # check if controller already was applied
        return self.applied

    # Also a first step we want our controller to be able to write its P and Q and state of charge values back to the
    # data structure net.
    def write_to_net(self, net):
        # write p, q and soc_percent to bus within the net
        net.valve.at[self.gid, "loss_coefficient"] = self.loss_coeff
        net.valve.at[self.gid, "opened"] = self.opened

    # In case the controller is not yet converged, the control step is executed. In the example it simply
    # adopts a new value according to the previously calculated target and writes back to the net.
    def control_step(self, net):
        name = net.valve.at[self.gid, 'name']
        mdot = np.nan_to_num(net.res_valve.at[self.gid, 'mdot_from_kg_per_s'])
        mdot_set = self.mdot_set_kg_per_s

        # Set valve status and position
        self._set_valve_status()
        if self.opened:
            self._set_valve_position(net)

        # # Update plot
        # if self.enable_plotting == True:
            # self.update_plot(net)

        # Call write_to_net and set the applied variable True
        self.write_to_net(net)
        self.applied = True

    def _set_valve_status(self):
        # Get flow results
        mdot_set = self.mdot_set_kg_per_s

        # set valve status
        if mdot_set < 1e-6:  # To avoid float issues
            self.opened = False

    def _set_valve_position(self, net):
        # Get method
        method = self.method

        # Get flow results
        mdot = np.nan_to_num(net.res_valve.at[self.gid, 'mdot_from_kg_per_s'])
        mdot_set = self.mdot_set_kg_per_s

        # set valve position
        # PID control
        output = self.pid(mdot)
        self.loss_coeff += output

        # Validate limits of loss_coeff
        min = self.loss_coeff_min
        max = self.loss_coeff_max
        if min <= self.loss_coeff <= max:
            pass
        elif self.loss_coeff < min:
            self.loss_coeff = min
        else:
            self.loss_coeff = max

        # Print new loss_coeff
        self.i += 1
        # print(f'Next loss coeff of {self.name} is y{self.i} = {self.loss_coeff}')

    # In a time-series simulation the battery should read new power values from a profile and keep track
    # of its state of charge as depicted below.
    def time_step(self, net, time):
        # read new values from a profile
        if self.data_source:
            if self.profile_name is not None:
                self.mdot_set_kg_per_s = self.data_source.get_time_step_value(
                                                                    time_step=time,
                                                                    profile_name=self.profile_name)

        self.applied = False  # reset applied variable

    def set_mdot_setpoint(self, setpoint):
        if self.profile_name is None:
            self.mdot_set_kg_per_s = setpoint

    # def update_plot(self, net):
        # loss_coeff = self.loss_coeff

        # mdot = net.res_valve.at[self.gid, 'mdot_from_kg_per_s']
        # mdot_set = self.mdot_set_kg_per_s

        # error = (mdot_set - mdot) / mdot_set
        # error_abs = np.sqrt(np.power(error, 2))

        # # self.xdata.append(loss_coeff)
        # self.xdata.append(self.i)
        # self.ydata.append(error_abs)

        # self.line.set_xdata(self.xdata)
        # self.line.set_ydata(self.ydata)
        # plt.draw()
        # plt.pause(1e-17)
        # # time.sleep(0.1)
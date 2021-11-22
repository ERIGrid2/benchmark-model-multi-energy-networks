# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dataclasses import dataclass
import numpy as np
from simple_pid import PID

@dataclass
class SimpleFlexHeatController:
    '''
    Simple controller for the power-to-heat facility (heat pump & storage tank).
    '''
    # Parameters
    T_tank_max: float = 72  # Maximum tank temperature - [degC]
    T_tank_min: float = 65  # Minimum tank temperature - [degC]
    mdot_tank_out_setpoint: float = 2 # Setpoint for tank discharge mass flow rate - [kg/s]

    # Variables
    ## Input measures
    T_tank_hot: float = 50  # Average tank temperature - [degC]

    # Control inputs
    voltage_control_enabled: bool = False  # Centralised voltage controller connected
    P_hp_rated: float = 100  # Rated heat pump el. consumption [kWe]
    P_hp_el_setpoint: float = 0  # Heat pump setpoint - [kWe]

    # Control outputs
    hp_on_request: bool = False  # Voltage control request for under voltage (toggle) and time period - [sec]
    hp_off_request: bool = False  # Voltage control request for over voltage (toggle) and time period - [sec]

    ## Internal Vars
    hp_operating_threshold: float = 0.35 * P_hp_rated  # HP operating threshold (minimum on-time el. consumption) - [kWe]

    ## Output
    mdot_tank_out: float = 0 # Tank discharge mass flow - [kg/s]
    P_hp_el: float = 0 # Setpoint for heat pump power consumption - [kWe]

    state: int = 1  # state variable 1..6

    def __post_init__(self):
        self.step_single()

    def step_single(self):
        self._update_state()  # Check if state is changed
        self._do_state_based_control()  # Do control based on new step

    def _do_state_based_control(self):

        if self.state == 1:  # Mode 1: External grid supplies heat, hp and tank inactive
            self.mdot_tank_out = 0.
            self.P_hp_el = 0.

        elif self.state == 2:  # Mode 2: External grid supplies heat, HP charges tank
            self.mdot_tank_out = 0.
            self.set_P_hp_el()

        elif self.state == 3:  # Mode 3: Discharge the tank, hp off
            raise Exception('Mode 3 not supported')

        elif self.state == 4:  # Mode 4: Discharge the tank, hp on
            self.mdot_tank_out = self.mdot_tank_out_setpoint
            self.set_P_hp_el()

        elif self.state == 5:  # Mode 5: Tank supports (with fixed mass flow) the grid, hp off
            self.mdot_tank_out = self.mdot_tank_out_setpoint
            self.P_hp_el = 0.

        elif self.state == 6:  # Mode 6: Tank supports (with fixed mass flow) the grid, hp on
            self.mdot_tank_out = self.mdot_tank_out_setpoint
            self.set_P_hp_el()
            
        # print('T_tank_hot: ', self.T_tank_hot, ' - mdot_tank_out: ', self.mdot_tank_out, ' - P_hp_el: ', self.P_hp_el)

    def _update_state(self):
        if self.voltage_control_enabled:
            self.set_hp_request()

        if self.state is 1:  # Mode 1: External grid supplies, tank inactive
            if not self.hp_off_request:
                self.set_state(new_state=2)  # Mode 2: Charge the tank, external supply

        elif self.state is 2:  # Mode 2: Grid supplies, tank inactive, hp on
            if self.T_tank_hot > self.T_tank_max:  # or self.hp_off_request:
                if self.hp_on_request:
                    self.set_state(new_state=6)
                else:
                    self.set_state(new_state=5)
            if self.hp_off_request:
                self.set_state(new_state=5)

        elif self.state is 6:  # Mode 6: Grid supplies, tank supports (and holding the temperature)
            if not self.hp_on_request:
                self.set_state(new_state=5)

        elif self.state is 5:  # Mode 5: Tank support, hp off
            if self.T_tank_hot < self.T_tank_min:  # or self.hp_on_request:
                if self.hp_off_request:
                    self.set_state(new_state=1)
                else:
                    self.set_state(new_state=2)
            if self.hp_on_request:
                self.set_state(new_state=2)

    def set_hp_request(self):
        # Set heat_pump request
        if self.P_hp_el_setpoint > self.hp_operating_threshold:
            self.hp_off_request = False
            self.hp_on_request = True
        else:
            self.hp_off_request = True
            self.hp_on_request = False
            
    def set_P_hp_el(self):
        if self.voltage_control_enabled:
            self.P_hp_el = self.P_hp_el_setpoint
        else:
            self.P_hp_el = self.P_hp_rated

    def set_state(self, new_state):
        old_state = self.state
        self.state = new_state
        if self.state != old_state:
            print(f'Controller state changed from {old_state} to {self.state}')


if __name__ == '__main__':

    test = SimpleFlexHeatController()


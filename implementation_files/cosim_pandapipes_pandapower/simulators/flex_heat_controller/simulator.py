# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dataclasses import dataclass
import numpy as np

@dataclass
class SimpleFlexHeatController:
    '''
    Simple controller for the power-to-heat facility (heat pump & storage tank).
    '''
    # Parameters
    T_tank_max: float = 72  # Maximum tank temperature - [degC]
    T_tank_min: float = 65  # Minimum tank temperature - [degC]

    # Variables
    ## Input measures
    mdot_HEX1: float = 0.0  # Mass flow requested by the consumer 1 HEX - [kg/s]
    mdot_HEX2: float = 0.0  # Mass flow requested by the consumer 1 HEX - [kg/s]
    mdot_bypass: float = 0.5  # Mass flow through network bypass - [kg/s]
    T_tank_hot: float = 50  # Average tank temperature - [degC]
    T_hp_cond_in: float = 50  # Heat pump condenser inlet temperature - [degC]
    T_hp_cond_out: float = 70  # Heat pump output temperature - [degC]
    T_hp_evap_in: float = 40  # Heat pump evaporator inlet temperature - [degC]
    T_hp_evap_out_min: float = 15  # Heat pump minimum evaporator outlet temperature - [degC]
    # Control inputs
    voltage_control_enabled: bool = False  # Centralised voltage controller connected
    P_hp_rated: float = 100  # Rated heat pump el. consumption [kWe]
    P_hp_el_setpoint: float = 0  # Heat pump setpoint - [kWe]
    P_hp_effective: float = 0  # Effective heat pump electricity consumption - [kWe]

    # Control outputs
    hp_on_request: bool = False  # Voltage control request for under voltage (toggle) and time period - [sec]
    hp_off_request: bool = False  # Voltage control request for over voltage (toggle) and time period - [sec]

    ## Internal Vars
    MDOT_FORWARD_MIN: float = 0.11  # Minimum forward mass flow - [kg/s]
    MDOT_HP_MAX: float = 10  # Maximum heat pump output mass flow - [kg/s]
    hp_operating_threshold: float = 0.35 * P_hp_rated  # HP operating threshold (minimum on-time el. consumption) - [kWe]

    ## Output
    mdot_1_supply: float = 0.0  # Supply 3 way valve mass flow at port 1 - [kg/s]
    mdot_2_supply: float = 0.0  # Supply 3 way valve mass flow at port 2 - [kg/s]
    mdot_3_supply: float = 0.0  # Supply 3 way valve mass flow at port 3 - [kg/s]

    mdot_1_return: float = 0.0  # Return 3 way valve mass flow at port 1 - [kg/s]
    mdot_2_return: float = 0.0  # Return 3 way valve mass flow at port 2 - [kg/s]
    mdot_3_return: float = 0.0  # Return 3 way valve mass flow at port 3 - [kg/s]

    mdot_HP_out: float = 0  # HP forward mass flow [kg/s]

    state: int = 1  # state variable 1..6

    # Constants
    Cp_water = 4.180  # [kJ/(kg.degK)]

    def __post_init__(self):
        self.step_single()

    def step_single(self):
        self._update_state()  # Check if state is changed
        self._do_state_based_control()  # Do control based on new step

    def _do_state_based_control(self):
        self.mdot_2_supply = -(self.mdot_HEX1 + self.mdot_HEX2 + self.mdot_bypass)
        self.mdot_1_return = self.mdot_HEX1 + self.mdot_HEX2 + self.mdot_bypass

        if self.state == 1:  # Mode 1: External grid supplies heat, hp and tank inactive
            self.mdot_1_supply = - self.mdot_2_supply - self.MDOT_FORWARD_MIN
            self.mdot_HP_out = 0

        elif self.state == 2:  # Mode 2: External grid supplies heat, HP charges tank
            self.mdot_1_supply = - self.mdot_2_supply - self.MDOT_FORWARD_MIN
            self.set_hp_mdot_out()

        elif self.state == 3:  # Mode 3: Discharge the tank, hp off
            self.mdot_1_supply = self.MDOT_FORWARD_MIN
            self.mdot_HP_out = 0

        elif self.state == 4:  # Mode 4: Discharge the tank, hp on
            self.mdot_1_supply = self.MDOT_FORWARD_MIN
            self.set_hp_mdot_out()

        elif self.state == 5:  # Mode 5: Tank supports (with fixed mass flow) the grid, hp off
            self.mdot_1_supply = - self.mdot_2_supply - 2.0
            self.mdot_HP_out = 0

        elif self.state == 6:  # Mode 6: Tank supports (with fixed mass flow) the grid, hp on
            self.mdot_1_supply = - self.mdot_2_supply - 2.0
            self.set_hp_mdot_out()

        self.mdot_3_supply = -(self.mdot_1_supply + self.mdot_2_supply)

        self.mdot_3_return = -self.mdot_3_supply

        self.mdot_2_return = -self.mdot_1_supply

    def _update_state(self):
        if self.voltage_control_enabled:
            self.set_hp_request()

        if self.state == 1:  # Mode 1: External grid supplies, tank inactive
            if not self.hp_off_request:
                self.set_state(new_state=2)  # Mode 2: Charge the tank, external supply

        elif self.state == 2:  # Mode 2: Grid supplies, tank inactive, hp on
            if self.T_tank_hot > self.T_tank_max:  # or self.hp_off_request:
                if self.hp_on_request:
                    self.set_state(new_state=6)
                else:
                    self.set_state(new_state=5)
            if self.hp_off_request:
                self.set_state(new_state=5)

        elif self.state == 6:  # Mode 6: Grid supplies, tank supports (and holding the temperature)
            if not self.hp_on_request:
                self.set_state(new_state=5)

        elif self.state == 5:  # Mode 5: Tank support, hp off
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

    def set_state(self, new_state):
        old_state = self.state
        self.state = new_state
        if self.state != old_state:
            print(f'Controller state changed from {old_state} to {self.state}')

    def set_hp_mdot_out(self):
        if self.voltage_control_enabled:
            if self.hp_off_request:
                self.mdot_HP_out = 0
            else:
                # PID control
                error_abs = self.P_hp_el_setpoint - self.P_hp_effective
                error_pu = (error_abs / self.P_hp_el_setpoint)
                mdot = self.mdot_HP_out
                mdot += error_pu * -0.5

                self.mdot_HP_out = np.clip(mdot, -self.MDOT_HP_MAX, 0)

        else:
            self.mdot_HP_out = -3.5
            pass

    def get_hp_cop(self):
        eta_hp_sys = 0.5  # Estimated hp efficiency
        T_hot_in = self.T_hp_cond_in
        T_hot_out = self.T_hp_cond_out
        T_cold_in = self.T_hp_evap_in
        T_cold_out = self.T_hp_evap_out_min

        # Calculate COP
        T_hot_m = (T_hot_in - T_hot_out) / np.log(T_hot_out/T_hot_in)
        T_cold_m = (T_cold_in - T_cold_out) / np.log(T_cold_out/T_cold_in)
        cop_hp = (eta_hp_sys * T_hot_m) / (T_hot_m - T_cold_m)

        return cop_hp

if __name__ == '__main__':

    test = SimpleFlexHeatController()


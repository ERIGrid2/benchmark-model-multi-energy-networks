# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dataclasses import dataclass
from ..util import clamp, safediv

@dataclass
class HEXConsumer:
    '''
    Simple heat consumer model based on a simplified heat exchanger model.
    '''

    # Parameters
    T_return_target: float = 40.0  # Return temperature set-point - [degC]
    T_return_min: float = 15.0  # Return temperature set-point - [degC]
    mdot_min: float = 0.01  # Minimum mass flow - [kg/s]
    mdot_max: float = 15  # Maximum mass flow - [kg/s]
    rel_adjust: float = 10  # How quickly the valve adjusts to new settings [s]
    max_change_rate: float = 1  # Valve cannot adjust faster than this rate [kg/s/s]

    # Variables
    ## Input
    P_heat: float = 500  # Heat demand - [kW]
    T_supply: float = 70.0  # Supply temperature - [degC]

    ## Output
    mdot_hex_in: float = 0.5  # Inlet mass flow - [kg/s]
    mdot_hex_out: float = -0.5  # Outlet mass flow - [kg/s]
    T_return: float = T_return_target  # Effective return temperature - [degC]

    # Constants
    Cp_water = 4.180  # [kJ/(kg.degK)]

    def __post_init__(self):
        self.step_single()

    def step_single(self):
        # Positive mass flow entering the HEX
        # Action of return-side valve is:
        # Increase outgoing mass flow if return temperature is lower than the target
        # Decrease outgoing mass flow if return temperature is higher than the target
        target_mdot_for_fixed_temperature = safediv(self.P_heat, self.Cp_water * (self.T_supply - self.T_return_target))
        self.mdot_hex_in = self.mdot_hex_in + 1/self.rel_adjust * \
            clamp(
                -self.max_change_rate,
                (target_mdot_for_fixed_temperature - self.mdot_hex_in),
                self.max_change_rate)

        if self.mdot_hex_in < self.mdot_min:
            print(f"calculated mass flow lower than minimum (reset to min: mdot_hex_in {self.mdot_hex_in:.03f}, mdot_hex_min: {self.mdot_min:.03f} ")
        self.mdot_hex_in = clamp(self.mdot_min, self.mdot_hex_in, self.mdot_max)

        # Negative mass flow leaving the HEX
        self.mdot_hex_out = -self.mdot_hex_in

        # Todo: issue warning if heat demand not met. T_return_min is sign of problems.
        self.T_return = clamp(
            self.T_return_min,
            self.T_supply - (self.P_heat / (self.Cp_water * self.mdot_hex_in)),
            self.T_supply)

if __name__ == '__main__':

    test = HEXConsumer()
    setattr(test, 'P_heat', 800)
    setattr(test, 'T_supply', 70)
    test.step_single()


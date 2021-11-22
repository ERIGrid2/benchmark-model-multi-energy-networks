# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dataclasses import dataclass, field
from math import exp
from ..util import clamp, log_mean, KBASE

@dataclass
class ConstantTcondHP:
    '''
    Heat pump model with constant output temperature at the condenser.
    '''

    # Unit parameters
    eta_sys: float = 0.80  # [n.u.] Relation between work provided by the pump and available thermodynamic work
    eta_comp: float = 0.70  # [n.u.]
    lambda_comp: float = 0.03  # [1/s]  -- was 0.5 , but that seemed rather fast for size of system.
    W_rated: float = field(init=False)  # [kW] - mechanical
    P_rated: float = 100.0   # [kW] - electrical
    P_0: float = 0.3  # [kW] - electrical
    W_0: float = P_0 * eta_comp  # [kW] - mechanical
    T_evap_out_min: float = 15  # [degC]
    T_cond_out_max: float = 85  # [degC]
    T_cond_out_target: float = 80

    # Simulation parameters
    dt: float = 1.0  # [s] Time per step

    # Input variables
    T_evap_in: float = 40  # [degC]
    T_cond_in: float = 40  # [degC]
    mdot_evap_in: float = 2  # [kg/s]
    mdot_cond_in: float = 0.0  # [kg/s]


    # Internal variables
    Q_for_constant_T: float = 0 # [kW] - thermal (Request derived from Mass flow)
    T_evap_L: float = T_evap_in  # [degC]
    T_cond_L: float = T_cond_in  # [degC]


    W_requested: float = 0.0  # [kW] - mechanical
    W_evap_max: float = 0.0  # [kW] - mechanical
    W_cond_max: float = 0.0  # [kW] - mechanical
    W_max: float = 0.0  # [kW] - mechanical
    W_effective: float = 0.0  # [kW] - mechanical

    eta_L: float = 2.0  # [n.u]
    eta_hp_work: float = field(init=False)  # [n.u.] Ratio of work supplied by pump to delivered heat
    eta_hp: float = field(init=False)  # [n.u] Ratio of electrical energy consumed to delivered heat

    # Output variables
    Qdot_cond: float = 0.0  # [kW] - thermal
    Qdot_evap: float = 0.0  # [kW] - thermal

    P_requested: float = 0.0  # [kW] - electrical
    P_cond_max: float = 0.0  # [kW] - electrical
    P_evap_max: float = 0.0  # [kW] - electrical
    P_max: float = 0.0  # [kW] - electrical
    P_effective: float = 0.0  # [kW] - electrical
    P_effective_mw: float = 0.0  # [MW] - electrical

    T_evap_out: float = 30  # [degC]
    T_cond_out: float = 75  # [degC]

    mdot_cond_out: float = -mdot_cond_in  # [kg/s]
    mdot_evap_out: float = -mdot_evap_in  # [kg/s]

    # Constants
    Cp_water: float = 4.180  # [kJ/(kg.K)]


    def __post_init__(self):
        self.W_rated = self.P_rated * self.eta_comp
        self.step_single()


    def step_single(self):
        # Logarithmic mean temperatures
        self.T_cond_L = log_mean(self.T_cond_in + KBASE, self.T_cond_out + KBASE)
        self.T_evap_L = log_mean(self.T_evap_in + KBASE, self.T_evap_out + KBASE)

        # Efficiencies
        self.eta_L = 1/(1 - self.T_evap_L / self.T_cond_L)
        self.eta_hp_work = self.eta_sys * self.eta_L

        # Mechanical work constraints
        self.W_cond_max = \
            (self.T_cond_out_max - self.T_cond_in) * \
            (self.Cp_water * self.mdot_cond_in) / \
            self.eta_hp_work

        self.W_evap_max = \
            (self.T_evap_in - self.T_evap_out_min) * \
            (self.Cp_water * self.mdot_evap_in) / (self.eta_hp_work - 1)

        self.W_max = max(0.0, min(self.W_evap_max, self.W_cond_max, self.W_rated))

        # Mechanical work request/effective calculation
        self.Q_for_constant_T = (self.T_cond_out_target - self.T_cond_in) * self.Cp_water * self.mdot_cond_in
        self.W_requested = clamp(0, self.Q_for_constant_T / self.eta_hp_work, self.W_max)

        expldt = exp(- self.lambda_comp * self.dt)
        # Pump responds within ~ 1/self.lambda_comp seconds
        self.W_effective = (1 - expldt) * self.W_requested + expldt * self.W_effective

        # Heat flows
        self.Qdot_cond = self.eta_hp_work * self.W_effective
        self.Qdot_evap = self.Qdot_cond - self.W_effective

        # Output temperatures
        if self.mdot_cond_in == 0:
            self.T_cond_out = self.T_cond_out_target
        else:
            self.T_cond_out = self.T_cond_in + self.Qdot_cond / (self.Cp_water * self.mdot_cond_in)

        self.T_evap_out = self.T_evap_in - self.Qdot_evap / (self.mdot_evap_in * self.Cp_water)

        # Electrical equivalents
        self.P_cond_max = self.W_cond_max / self.eta_comp
        self.P_evap_max = self.W_evap_max / self.eta_comp
        self.P_max = self.W_max / self.eta_comp

        self.P_requested = self.W_requested / self.eta_comp
        self.P_effective = self.P_0 + self.W_effective / self.eta_comp
        self.P_effective_mw = 1e-3*self.P_effective
        self.eta_hp = self.Qdot_cond / self.P_effective

        self.mdot_cond_out = -self.mdot_cond_in
        self.mdot_evap_out = -self.mdot_evap_in


if __name__ == '__main__':
    test = ConstantTcondHP()

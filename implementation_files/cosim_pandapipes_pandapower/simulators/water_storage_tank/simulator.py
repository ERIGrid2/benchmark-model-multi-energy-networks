# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dataclasses import dataclass, field
import numpy as np
from ..util import KBASE


@dataclass
class WaterStorageTank:
    '''
    Stratified water storage tank model.
    '''

    # Constants
    Cp_water: float = 4180  # Heat capacity - [J/(kg*degK)]
    rho_water: float = 1000  # Density - [kg/m³]

    # Simulation parameters
    dt: float = 1.0  # Time per step, integration resolution - [s]

    # Unit parameters
    # # Geometry
    INNER_HEIGHT: float = 2.0  # [m]
    INNER_DIAMETER: float = 1  # [m]

    INSULATION_THICKNESS: float = 0.1  # Insulation layer thickness - [m]
    STEEL_THICKNESS: float = 0.01  # Structural layer thickness - [m]

    # # Properties
    LAMBDA_INSULATION: float = 0.03  # Thermal conductivity - [W/(m*degK)]
    LAMBDA_STEEL: float = 60  # Thermal conductivity - [W/(m*degK)]
    NB_LAYERS: float = 10  # Number of layers/control volumes dividing the tank volume - [-]


    # Variables
    # # State
    T_volume_initial: int = 50  # Control volume temperature - [degK]
    # # Input
    T_environment: float = 15  # Surrounding temperature to the tank - [degK]

    # Internal parameters
    # # Geometry
    INNER_RADIUS: float = field(init=False)  # [m]
    TOTAL_WALL_AREA: float = field(init=False)  # [m²]
    WATER_VOLUME: float = field(init=False)  # [m³]

    CROSS_SECTIONAL_WATER_AREA: float = field(init=False)  # [m²]
    CROSS_SECTIONAL_INSULATION_AREA: float = field(init=False)  # [m²]
    CROSS_SECTIONAL_STEEL_AREA: float = field(init=False)  # [m²]

    # # Properties
    U_INSULATION: float = field(init=False)  # Thermal transmittance - [W/(m²*degK)]
    U_STEEL: float = field(init=False)  # Thermal transmittance - [W/(m²*degK)]

    R_INSULATION: float = field(init=False)  # Thermal resistance - [(m²*degK)/W]
    R_STEEL: float = field(init=False)  # Thermal resistance - [(m²*degK)/W]

    R_WALL: float = field(init=False)  # Overall thermal resistance - [(m²*degK)/W]
    U_WALL: float = field(init=False)  # Overall thermal transmittance - [W/(m²*degK)]
    LAMBDA_WALL: float = field(init=False)  # Overall thermal conductivity - [W/m*degK]

    DELTA_LAMBDA: float = field(init=False)

    WATER_MASS: float = field(init=False)

    LAYER_LENGTH: float = field(init=False)  # Height of a control volume - [m]
    LAYER_WALL_AREA: float = field(init=False)  # [m²]

    # Internal variables
    # # State
    Layers_temperature_dict: dict = field(default_factory=dict)
    Layers_list: list = field(default_factory=list)

    # # Input
    T_ch_in: float = T_volume_initial  # Inlet temperature to the water tank (while charged) - [degC]
    T_dis_in: float = T_volume_initial
    mdot_ch_in: float = 0.0  # Charging mass flow rate inlet (>0)- [kg/s]
    mdot_dis_out: float = 0.0  # Discharging mass flow rate outlet (<0)- [kg/s]

    # # Output
    T_hot: float = T_volume_initial  # Temperature at the top of the tank - [degC]
    T_cold: float = T_volume_initial  # Temperature at the bottom of the tank - [degC]
    T_out: float = T_volume_initial  # Outlet temperature from the water tank (while charged) - [degC]
    mdot_ch_out: float = 0.0  # Charging mass flow rate outlet (<0) - [kg/s]
    mdot_dis_in: float = 0.0  # Discharging mass flow rate inlet (>0) - [kg/s]


    def __post_init__(self):
        self.initialize_internal_variables()
        self.initialize_stratification()
        self.step_single()

    def initialize_internal_variables(self):
        # Internal parameters
        # # Geometry
        self.INNER_RADIUS = self.INNER_DIAMETER / 2  # [m]
        self.TOTAL_WALL_AREA = 2 * np.pi * self.INNER_RADIUS ** 2 + 2 * np.pi * self.INNER_RADIUS * self.INNER_HEIGHT  # [m²]
        self.WATER_VOLUME = np.pi * self.INNER_RADIUS ** 2 * self.INNER_HEIGHT  # [m³]

        self.CROSS_SECTIONAL_WATER_AREA = 2 * np.pi * self.INNER_RADIUS ** 2  # [m²]
        self.CROSS_SECTIONAL_INSULATION_AREA = 4 * np.pi ** 2 * (self.INNER_RADIUS + self.INSULATION_THICKNESS / 2) * (
                    self.INSULATION_THICKNESS / 2)  # [m²]
        self.CROSS_SECTIONAL_STEEL_AREA = 4 * np.pi ** 2 * (self.INNER_RADIUS + self.STEEL_THICKNESS / 2) * (
                    self.STEEL_THICKNESS / 2)  # [m²]

        # # Properties
        self.U_INSULATION = self.LAMBDA_INSULATION / self.INSULATION_THICKNESS  # Thermal transmittance - [W/(m²*degK)]
        self.U_STEEL = self.LAMBDA_STEEL / self.STEEL_THICKNESS  # Thermal transmittance - [W/(m²*degK)]

        self.R_INSULATION = 1 / self.U_INSULATION  # Thermal resistance - [(m²*degK)/W]
        self.R_STEEL = 1 / self.U_STEEL  # Thermal resistance - [(m²*degK)/W]

        self.R_WALL = self.R_INSULATION + self.R_STEEL  # Overall thermal resistance - [(m²*degK)/W]
        self.U_WALL = 1 / self.R_WALL  # Overall thermal transmittance - [W/(m²*degK)]
        self.LAMBDA_WALL = self.U_WALL * (
            self.INSULATION_THICKNESS + self.STEEL_THICKNESS)  # Overall thermal conductivity - [W/m*degK]

        self.DELTA_LAMBDA = self.LAMBDA_WALL * (
                    (self.CROSS_SECTIONAL_STEEL_AREA + self.CROSS_SECTIONAL_INSULATION_AREA) / self.CROSS_SECTIONAL_WATER_AREA)

        self.WATER_MASS = self.rho_water * self.WATER_VOLUME

        self.LAYER_LENGTH = self.INNER_HEIGHT  # Height of a control volume - [m]
        self.LAYER_WALL_AREA = 2 * np.pi * self.INNER_RADIUS ** 2 + 2 * np.pi * self.INNER_RADIUS * self.INNER_HEIGHT  # [m²]

        ## Input
        self.T_ch_in = self.T_volume_initial  # Inlet temperature to the water tank - [degK]
        self.T_dis_in = self.T_volume_initial  # Inlet temperature to the water tank - [degK]

        ## Output
        self.T_hot = self.T_volume_initial  # Temperature at the top of the tank - [degK]
        self.T_cold = self.T_volume_initial  # Temperature at the bottom of the tank - [degK]
        self.T_out = self.T_volume_initial  # Outlet temperature from the water tank - [degK]


    def initialize_stratification(self):
        self.Layers_list = list(np.arange(self.NB_LAYERS))
        self.LAYER_LENGTH = self.INNER_HEIGHT / self.NB_LAYERS
        self.LAYER_WATER_MASS = self.WATER_MASS / self.NB_LAYERS
        self.LAYER_WALL_AREA = 2 * np.pi * self.INNER_RADIUS**2 + 2 * np.pi * self.INNER_RADIUS * self.LAYER_LENGTH

        for layer in self.Layers_list:
            self.Layers_temperature_dict[layer] = self.T_volume_initial


    def step_single(self):
        # Charging mode
        if self.mdot_ch_in > 0:

            self.mdot_ch_out = - self.mdot_ch_in
            self.mdot_down = self.mdot_ch_in
            self.mdot_up = 0.0

            for layer in self.Layers_list:
                # Top of the tank boundary layer
                if layer == 0:
                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            - self.mdot_down * self.Cp_water * self.Layers_temperature_dict[layer]
                            + self.mdot_ch_in * self.Cp_water * self.T_ch_in
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]


                    # Intermediate layers
                elif (layer != 0 and layer != self.Layers_list[-1:][0]):

                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            +(self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            + self.mdot_down * self.Cp_water * self.Layers_temperature_dict[layer-1]
                            - self.mdot_down * self.Cp_water * self.Layers_temperature_dict[layer]
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]


                # Bottom of the tank boundary layer
                elif layer == self.Layers_list[-1:][0]:

                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            + self.mdot_down * self.Cp_water * self.Layers_temperature_dict[layer-1]
                            + self.mdot_ch_out * self.Cp_water * self.Layers_temperature_dict[layer]
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]

                else:
                    raise ValueError("Layer {0} is unknown".format(layer))

                self.T_out = self.Layers_temperature_dict[self.Layers_list[-1:][0]]


        # Discharging mode (can be at the same time)
        if self.mdot_dis_out < 0:
            self.mdot_dis_in = - self.mdot_dis_out
            self.mdot_up = - self.mdot_dis_out
            self.mdot_down = 0.0

            reverse_layers_list = reversed(self.Layers_list)

            for layer in reverse_layers_list:
                # Bottom of the tank boundary layer
                if layer == self.Layers_list[-1:][0]:

                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            - self.mdot_up * self.Cp_water * self.Layers_temperature_dict[layer]
                            - self.mdot_dis_out * self.Cp_water * self.T_dis_in
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]

                # Intermediate layers
                elif (layer != 0 and layer != self.Layers_list[-1:][0]):
                    self.Layers_temperature_dict[layer] =  (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            +(self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            + self.mdot_up * self.Cp_water * self.Layers_temperature_dict[layer+1]
                            - self.mdot_up * self.Cp_water * self.Layers_temperature_dict[layer]
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]

                # Top of the tank boundary layer
                elif layer == 0:
                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            + self.mdot_up * self.Cp_water * self.Layers_temperature_dict[layer+1]
                            - self.mdot_dis_in * self.Cp_water * self.Layers_temperature_dict[layer]
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]
                else:
                    raise ValueError("Layer {0} is unknown".format(layer))

                self.T_out = self.Layers_temperature_dict[self.Layers_list[-1:][0]]


        # Stand-by mode
        elif self.mdot_ch_in == 0 and self.mdot_dis_out == 0:

            for layer in self.Layers_list:
                if layer == 0:
                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer])
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]

                elif (layer != 0 and layer != self.Layers_list[-1:][0]):
                    self.Layers_temperature_dict[layer] =  (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer+1] - self.Layers_temperature_dict[layer]) \
                            +(self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer]) \
                            ) / (self.LAYER_WATER_MASS * self.Cp_water)
                        ) * self.dt + self.Layers_temperature_dict[layer]

                elif layer == self.Layers_list[-1:][0]:
                    self.Layers_temperature_dict[layer] = (
                        (
                            (self.LAMBDA_WALL + self.DELTA_LAMBDA) * self.CROSS_SECTIONAL_WATER_AREA / self.LAYER_LENGTH * (self.Layers_temperature_dict[layer-1] - self.Layers_temperature_dict[layer]) \
                            + self.U_WALL * self.LAYER_WALL_AREA * (self.T_environment - self.Layers_temperature_dict[layer]) \
                            ) / (self.LAYER_WATER_MASS * self.Cp_water) \
                        ) * self.dt + self.Layers_temperature_dict[layer]
                else:
                    raise ValueError("Layer {0} is unknown".format(layer))

            self.T_out = self.Layers_temperature_dict[self.Layers_list[-1:][0]]

        if self.mdot_ch_in < 0 or self.mdot_dis_out > 0:
            raise ValueError('Unknown value for incoming mass flow mdot_ch_in: {0} and outgoing mass flow mdot_dis_out: {1}'.format(self.mdot_ch_in, self.mdot_dis_out))

        self.T_hot = self.Layers_temperature_dict[0]
        self.T_cold = self.Layers_temperature_dict[self.Layers_list[-1:][0]]


if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import pandas as pd

    Test = WaterStorageTank()

    sim_time = 60 * 60 * 4

    layers_temperature_df = pd.DataFrame(index=np.arange(sim_time), columns=[Test.Layers_list])
    outlet_temp_df = pd.DataFrame(index=np.arange(sim_time), columns=["T_out"])

    for time_step in range(sim_time):
        if time_step < 60*60*1:
            setattr(Test, "T_in", 80)
            setattr(Test, "mdot_in", 0.5)

            Test.step_single()

            for layer, temperature in Test.Layers_temperature_dict.items():
                layers_temperature_df.iloc[time_step][layer] = temperature

            outlet_temp_df.iloc[time_step]["T_out"] = Test.T_out

        elif 60*60*1 <= time_step < 60*60*2: 
            setattr(Test, "T_in", 35)
            setattr(Test, "mdot_in", -0.4)

            Test.step_single()

            for layer, temperature in Test.Layers_temperature_dict.items():
                layers_temperature_df.iloc[time_step][layer] = temperature

            outlet_temp_df.iloc[time_step]["T_out"] = Test.T_out

        elif 60*60*2 <= time_step < 60*60*3: 
            setattr(Test, "T_in", 90)
            setattr(Test, "mdot_in", 0.7)

            Test.step_single()

            for layer, temperature in Test.Layers_temperature_dict.items():
                layers_temperature_df.iloc[time_step][layer] = temperature

            outlet_temp_df.iloc[time_step]["T_out"] = Test.T_out

        else:
            setattr(Test, "mdot_in", 0.0)

            Test.step_single()

            for layer, temperature in Test.Layers_temperature_dict.items():
                layers_temperature_df.iloc[time_step][layer] = temperature

            outlet_temp_df.iloc[time_step]["T_out"] = Test.T_out

    # Layers temperatures plot
    plt.figure()

    for layer in range(len(Test.Layers_list)):
        plt.plot(layers_temperature_df[layer], label='Layer {0}'.format(layer))

    plt.legend()
    plt.xlabel('Time - [seconds]')
    plt.ylabel('Temperature - [$^\circ$C]')

    plt.tight_layout()
    plt.grid()

    # Outlet temperature from the water tank
    plt.figure()
    plt.plot(outlet_temp_df, label='Tank outlet temperature')
    plt.legend()
    plt.xlabel('Time - [seconds]')
    plt.ylabel('Temperature - [$^\circ$C]')

    plt.axvline(x=60*60*4, linestyle='--', linewidth=0.5, color='black')
    plt.grid()
    plt.tight_layout()

    plt.ion()
    plt.show()


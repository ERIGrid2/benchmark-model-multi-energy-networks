# Implementation of thermal system based on DisHeatLib

This folder contains the Modelica model of the thermal system of the multi-energy network benchmark.

## Requirements

The model requires [Dymola](https://www.3ds.com/products-services/catia/products/dymola/) to run.
For viewing the model you may also use [OpenModelica](https://openmodelica.org/).

The following Modelica libraries are requried:

 * [Modelica IBPSA library](https://github.com/ibpsa/modelica-ibpsa/): use commit [a4d922c](https://github.com/ibpsa/modelica-ibpsa/tree/a4d922c9b082eb739d7b1c34959d21a48072592f)
   ```
   git clone https://github.com/ibpsa/modelica-ibpsa.git
   cd modelica-ibpsa
   git checkout a4d922c9b082eb739d7b1c34959d21a48072592f
   ```
 * [DisHeatLib](https://github.com/AIT-IES/DisHeatLib) use commit [b11f533](https://github.com/AIT-IES/DisHeatLib/tree/b11f53379c122870a52f2da9b1705d2c911cd21d)
   ```
   git clone https://github.com/AIT-IES/DisHeatLib.git
   cd DisHeatLib
   git checkout b11f53379c122870a52f2da9b1705d2c911cd21d
   ```
 * To automatically load package IBPSA and DisHeatLib each time you start Dymola, open `\insert\dymola.mos` and add the following lines:
   ```
   openModel("[library path]/IBPSA/package.mo");
   openModel("[library path]/DisHeatLib/package.mo");
   ```

## Overview of Modelica model

File `ERIGridMultiEnergyBenchmark.mo` contains a Modelica package that implements the model of the thermal system of the multi-energy network benchmark.
It contains the following:

 * Class `DHNetworkMassFlowControlled`: This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by directly controlling the mass flow, always providing enough to satisfy the demand of the consumers.
 * Class `DHNetworkPressureControlled`: This model implements the thermal system of the multi-energy network benchmark. The heating network is operated by controlling the pressure, keeping the pressure drop at the consumers above a certain threshold.
 * Sub-package `Components`: This sub-package contains components used for modelling the thermal system of the multi-energy network benchmark
 * Sub-package `FMI`: Specifies models of the thermal system of the multi-energy network benchmark intended for export as FMU. The operation of the power-to-heat facility (heat pump and tank) is controlled via the external inputs (heat pump power consumption, tank dischargche mass flow). 

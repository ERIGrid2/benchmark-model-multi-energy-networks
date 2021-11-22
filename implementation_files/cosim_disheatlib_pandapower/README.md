# Co-simulation model of the multi-energy network benchmark using DisHeatLib and pandapower

This implementation of the multi-energy newtork benchmark uses [mosaik](https://mosaik.offis.de/) for a co-simulation of a [DisHeatLib](https://github.com/AIT-IES/DisHeatLib) model, [pandapower](https://pandapower.readthedocs.io/) and the controllers.

## Requirements

* A working installation of [Python](https://www.python.org/) is required to run this simulation. The recommended version is **Python 3.6**.
* This benchmark implementation has been tested on **Ubuntu 18.04** and **Windows 10**.

## Installation 

### Windows 10

Install all required Python packages with the following command:
```
> python -m pip install -r requirements-win64.txt
```

### Ubuntu 18.04

Prerequisites for installing the [FMI++ Python Interface](https://pypi.org/project/fmipp/):
```
> sudo apt-get install python-setuptools build-essential swig libsundials-dev libboost-all-dev
```

Install all required Python packages with the following command:
```
> python -m pip install -r requirements-linux64.txt
```


## Running the benchmark simulations

Run a benchmark simulation with **voltage control enabled** with the following command:
```
> python benchmark_multi_energy_sim.py --outfile benchmark_results_ctrl_enabled.h5
```

Run a benchmark simulation with **voltage control disabled** with the following command:
```
> python benchmark_multi_energy_sim.py --outfile benchmark_results_ctrl_disabled.h5 --voltage-control-disabled
```

A few comments about running the simulations:

* On a tpyical laptop each simulation takes several minutes to complete.
* You can speed-up the simulation by using a bigger simulation step size or shorter simulation period.
  For more details refer to the usage instructions:
  ```
  > python benchmark_multi_energy_sim.py --help
  ```
* For the simulation of the thermal network, the corresponding model has been exported as a *Functional Mock-up Unit* (FMU) 
  This FMU has been generated with the help of [Dymola](https://www.3ds.com/products-services/catia/products/dymola/) and can be executed without a license.
  However, the generated FMU is plattform-specific and only runs on Windows.

## Analyzing the benchmark results

After running the simulations, you can produce plots that analyze the benchmark results with the following command:
```
> python benchmark_multi_energy_analysis.py
```

**NOTE**: To exclude simulation data affected by initialization artifacts, data from the first simulated day is by default not included into the analysis.

## Source code and data

* File [```benchmark_multi_energy_sim.py```](./benchmark_multi_energy_sim.py) contains the implementation of the mosaik co-simulation setup.
* Folder [```simulators```](./simulators) contains the Python implementation of all simulators used by mosaik in individual subfolders. This includes the network simulators for the thermal system (using an FMU generated with Dymola) and the electrical system (using pandapower).
* Folder [```resources```](./resources) contains data related to this simulation setup (e.g., consumption profiles).
* Folder [```resources/heat```](./resources/heat) also contains the complete Modelica model of the thermal system (modelled with the help of the DisHeatLib library).
  For using this model in the co-simulation, it has to be exported as an FMU.

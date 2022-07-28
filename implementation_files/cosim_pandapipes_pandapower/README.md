# Co-simulation model of the multi-energy network benchmark using pandapipes and pandapower

This implementation of the multi-energy newtork benchmark uses [mosaik](https://mosaik.offis.de/) for a co-simulation of [pandapipes](https://pandapipes.readthedocs.io/), [pandapower](https://pandapower.readthedocs.io/), several stand-alone models and the controllers.

## Requirements

* Only a working installation of [Python](https://www.python.org/) is required to run this simulation. The recommended version is **Python 3.8**.
* This benchmark implementation has been tested on **Ubuntu 20.04** and **Windows 10**.

## Installation

Install all required Python packages with the following command:
```
> python -m pip install -r requirements.txt
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
* During the initial phase the simulation is still affected by artifacts resulting from the initial conditions.
  In rare cases this causes unrealistic conditions, which results in warnings like the following:
  ```
  UserWarning: Controller not converged: maximum number of iterations per controller is reached at time t=21660.
  ```
  This is to be expected during the first few simulated hours and can be safely ignored.
  (For this reason, the first simulated day is not taken into account in the analysis.)

## Analyzing the benchmark results

After running the simulations, you can produce plots that analyze the benchmark results with the following command:
```
> python benchmark_multi_energy_analysis.py
```

**NOTE**: To exclude simulation data affected by initialization artifacts, data from the first simulated day is by default not included into the analysis.

## Source code and data

* File [```benchmark_multi_energy_sim.py```](./benchmark_multi_energy_sim.py) contains the implementation of the mosaik co-simulation setup.
* Folder [```simulators```](./simulators) contains the Python implementation of all simulators used by mosaik in individual subfolders. This includes the network simulators for the thermal system (using pandapipes) and the electrical system (using pandapower).
* Folder [```resources```](./resources) contains data related to this simulation setup (e.g., consumption profiles).

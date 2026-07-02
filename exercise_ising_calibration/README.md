# T1 Calibration with CUDA-Q Dynamics

In this exercise, you will simulate a T1 experiment for a single qubit. T1 is
the characteristic time for an excited qubit to lose energy and relax toward
its ground state.

## Run the experiment

From this folder, run:

```bash
python3 t1_experiment.py
```

The script prints the expected result, runs the CUDA-Q Dynamics simulation,
shows a labeled plot, and saves the plot as `t1_experiment.png`.

The excited-state probability should begin near 1, decay exponentially, reach
about 0.37 after one T1, and approach 0 at long times.

## Interpret the calibration

1. Open the
   [Ising Calibration playground](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b/playground).
2. Upload `t1_experiment.png`.
3. Ask: **Interpret the result of this T1 calibration experiment. What does
   the curve show, and does the calibration appear healthy?**

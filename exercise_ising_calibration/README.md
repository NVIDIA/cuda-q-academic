# T1 Calibration with CUDA-Q Dynamics

In this exercise, you will simulate a T1 experiment for a single qubit. T1 is
the characteristic time for an excited qubit to lose energy and relax toward
its ground state.

## Run the experiment

From this folder, run:

```bash
python3 t1_experiment.py
```

The script creates two labeled plots:

- `t1_experiment.png` shows the ideal CUDA-Q Dynamics result.
- `t1_experiment_noisy.png` shows a sparse finite-shot experiment.

The ideal excited-state probability begins near 1, decays exponentially,
reaches about 0.37 after one T1, and approaches 0 at long times.

The finite-shot plot estimates each displayed probability from 64 binary
measurements. Its scatter is physically meaningful quantum projection noise:
a real experiment only observes excited or ground on each shot and estimates
the probability from those outcomes. It does not include readout error,
state-preparation error, thermal excitation, or device drift.

## Interpret the calibration

1. Compare the smooth and finite-shot plots.
2. Open the
   [Ising Calibration playground](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b/playground).
3. Upload `t1_experiment_noisy.png`.
4. Ask: **Estimate T1 from this calibration result. Explain how you identified
   the decay timescale despite the finite-shot scatter, and assess whether the
   result appears healthy.**

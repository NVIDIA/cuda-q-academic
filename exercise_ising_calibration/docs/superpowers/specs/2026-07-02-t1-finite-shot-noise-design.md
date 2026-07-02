# T1 Finite-Shot Noise Design

## Goal

Extend the existing T1 exercise so one run produces both an ideal CUDA-Q
Dynamics result and a sparse, scattered result that resembles finite-shot
experimental data. The noisy plot must retain an inferable T1 while requiring
the learner to reason about the trend instead of reading a perfect curve.

## Scope

Modify the two existing learner-facing files:

- `t1_experiment.py` will create the ideal and finite-shot plots.
- `README.md` will explain both outputs and ask learners to interpret the noisy
  result with Ising Calibration.

No second script, NumPy dependency, or CuPy dependency will be added.

## Simulation and Measurement Model

The CUDA-Q Dynamics model remains unchanged. It evolves a relaxing two-level
spin with T1 equal to 10 time units and returns the ideal excited-state
probability at 101 delay times.

The script will continue saving that smooth result as `t1_experiment.png`.
It will then select every fifth delay time, leaving 21 experimental delays.
At each selected delay, it will simulate 32 independent projective
measurements. Each measurement reports excited with the ideal CUDA-Q
probability and ground otherwise. The measured excited-state fraction is the
number of excited outcomes divided by 32. Compared with 64 shots, this raises
the typical statistical scatter by about 41 percent while retaining an
interpretable exponential trend.

Python's standard-library `random.Random` will generate the Bernoulli outcomes.
A fixed seed will make the workshop image reproducible. This sampling models
finite-shot quantum projection noise. It does not claim to model state
preparation error, readout error, thermal excitation, or device drift.

## Plot and Console Behavior

The ideal plot remains a smooth line with its existing title and labeled axes.
The new plot will:

- show only unconnected finite-shot data markers;
- use the title `T1 Calibration with Finite-Shot Noise`;
- label its axes `Time` and `Measured excited-state fraction`;
- avoid showing the ideal curve or true T1 value; and
- save as `t1_experiment_noisy.png`.

The script will print the two output filenames and prompt the learner to
estimate T1 from the noisy plot. Matplotlib's headless backend will save both
plots without trying to open display windows.

## README Changes

The README will explain that finite-shot noise arises because a real experiment
estimates probability from a limited number of binary measurements. It will
tell learners to compare `t1_experiment.png` with
`t1_experiment_noisy.png`, upload the noisy image to Ising Calibration, and ask
the model to estimate T1 and explain its reasoning.

## Verification

Checks will confirm that:

- the script and README mention both output images;
- the implementation imports the Python `random` module but not NumPy or CuPy;
- the sampling uses 21 delays and 32 shots per delay;
- the seeded noisy data are reproducible, bounded between zero and one, and
  differ from the ideal probabilities;
- the ideal CUDA-Q result still has probability near `1/e` at one T1;
- both PNG files are created and nonempty; and
- headless execution produces no warnings.

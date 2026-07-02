# Ising Calibration T1 Exercise Design

## Goal

Create a small, self-contained workshop exercise that demonstrates a T1
relaxation experiment with CUDA-Q Dynamics. A learner runs one Python script,
receives a saved and displayed plot, and uploads that plot to NVIDIA's Ising
Calibration model for interpretation.

## Deliverables

The exercise contains two learner-facing files:

- `README.md` with the run command, expected output image, and a link to the
  Ising Calibration playground.
- `t1_experiment.py`, one teaching-oriented Python script that performs and
  plots the experiment.

This design document is supporting development documentation, not an
additional learner task.

## Experiment Design

The script models a single two-level spin. CUDA-Q's
`dynamics.InitialState.ZERO` is treated as the upper-energy spin state. A
collapse operator proportional to `spin.minus(0)` relaxes that state with rate
`1 / T1`. A zero Hamiltonian isolates relaxation from coherent motion.

The simulation uses `T1 = 10.0` time units and samples from zero through
`5 * T1`. Time points are created with Python built-ins so the simulation does
not depend on NumPy or CuPy. CUDA-Q Dynamics supplies the schedule, evolution,
collapse operator, and intermediate expectation values.

The observable is Pauli Z. Each expectation value is converted to the
upper-state probability with `(1 + <Z>) / 2`. The expected probability is 1 at
time zero, approximately `1/e`, or 0.37, at one T1, and close to zero after
five T1 periods.

## Script Behavior

The script will:

1. Select CUDA-Q's `dynamics` target.
2. Define the two-level system, zero Hamiltonian, relaxation collapse
   operator, initial state, and time schedule.
3. Call `cudaq.evolve` while saving intermediate expectation values.
4. Convert the Pauli-Z results to excited-state probabilities.
5. Print a short description of the expected exponential decay before
   plotting.
6. Create a plot titled `CUDA-Q T1 Relaxation Experiment` with axes labeled
   `Time` and `Excited-state probability`.
7. Save the plot as `t1_experiment.png` and display it.

Imports are limited to `cudaq`, Python's standard-library `math` module, and
`matplotlib.pyplot`. Matplotlib is used only to create and save the required
plot.

## README Flow

The README briefly explains that a T1 experiment measures energy relaxation.
It tells learners to run:

```bash
python3 t1_experiment.py
```

It then tells them to locate `t1_experiment.png`, open the
[Ising Calibration playground](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b/playground),
upload the image, and ask the model to interpret the calibration result. The
README also states the expected exponential-decay shape so learners can
compare the model's interpretation with the known result.

## Error Handling

The exercise intentionally avoids custom exception handling. Import failures,
an unavailable CUDA-Q Dynamics target, or plotting failures should remain
visible as ordinary Python errors so workshop facilitators can diagnose the
environment directly. The README assumes the workshop environment already
provides CUDA-Q and Matplotlib.

## Verification

Automated checks will confirm that:

- both learner-facing files exist;
- the script contains no NumPy or CuPy dependency;
- the README includes the exact run command and Ising Calibration link; and
- the script parses as valid Python.

The script will then be run in the workshop environment with a noninteractive
Matplotlib backend. Verification will confirm successful completion, expected
console guidance, creation of a nonempty PNG, and a decreasing probability
curve with a value near 0.37 at one T1.

## Deferred Realism

This version shows the ideal ensemble-average T1 curve. Finite-shot scatter,
readout error, thermal re-excitation, and calibration drift are explicitly out
of scope. They can be added in a later exercise without changing this
exercise's core explanation.

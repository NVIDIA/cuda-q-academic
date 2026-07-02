# T1 Finite-Shot Noise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing T1 exercise so one run produces both the ideal CUDA-Q Dynamics curve and a reproducible finite-shot experimental scatter plot.

**Architecture:** `t1_experiment.py` remains a linear teaching script: CUDA-Q computes the ideal probabilities, then Python's seeded standard-library random generator samples binary measurement outcomes at sparse delays. `README.md` explains the distinction and routes the noisy image to Ising Calibration.

**Tech Stack:** Python 3, CUDA-Q Dynamics, Python `math` and `random`, Matplotlib

---

### Task 1: Finite-Shot Measurement Plot

**Files:**
- Modify: `exercise_ising_calibration/t1_experiment.py`

- [ ] **Step 1: Run the failing finite-shot contract check**

Run from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("exercise_ising_calibration/t1_experiment.py").read_text()
assert "import random" in text
assert "shots_per_delay = 64" in text
assert "time_steps[::5]" in text
assert "excited_state_probability[::5]" in text
assert "random.Random(7)" in text
assert 'set_ylabel("Measured excited-state fraction")' in text
assert 'savefig("t1_experiment_noisy.png")' in text
PY
```

Expected: FAIL on `assert "import random" in text` because finite-shot
sampling has not been added.

- [ ] **Step 2: Add the minimal sampling and second plot**

Replace `exercise_ising_calibration/t1_experiment.py` with:

```python
import math
import random

import cudaq
import matplotlib.pyplot as plt
from cudaq import spin
from cudaq.dynamics import InitialState, Schedule


cudaq.set_target("dynamics")

# Model one two-level spin and watch it for five relaxation times.
t1 = 10.0
number_of_steps = 101
time_steps = [
    5.0 * t1 * step / (number_of_steps - 1)
    for step in range(number_of_steps)
]
schedule = Schedule(time_steps, ["time"])

dimensions = {0: 2}
hamiltonian = 0.0 * spin.z(0)
initial_state = InitialState.ZERO
relaxation = math.sqrt(1.0 / t1) * spin.minus(0)

result = cudaq.evolve(
    hamiltonian,
    dimensions,
    schedule,
    initial_state,
    collapse_operators=[relaxation],
    observables=[spin.z(0)],
    store_intermediate_results=cudaq.IntermediateResultSave.EXPECTATION_VALUE,
)

# For this spin convention, (1 + <Z>) / 2 is the upper-state probability.
excited_state_probability = [
    (1.0 + values[0].expectation()) / 2.0
    for values in result.expectation_values()
]

print("Expected result:")
print("The excited-state probability should decay exponentially from 1 to 0.")
print(f"At T1 = {t1}, it should be about 1/e = {1.0 / math.e:.2f}.")

figure, axes = plt.subplots()
axes.plot(time_steps, excited_state_probability)
axes.set_title("CUDA-Q T1 Relaxation Experiment")
axes.set_xlabel("Time")
axes.set_ylabel("Excited-state probability")
axes.set_ylim(0.0, 1.05)
axes.grid(True)
figure.tight_layout()
figure.savefig("t1_experiment.png")
print("Saved ideal plot to t1_experiment.png")

# A real experiment estimates each probability from a finite number of binary
# measurements. Sampling only some delays makes that shot noise visible.
shots_per_delay = 64
measurement_times = time_steps[::5]
ideal_measurement_probabilities = excited_state_probability[::5]
random_generator = random.Random(7)
measured_excited_state_fraction = [
    sum(
        random_generator.random() < probability
        for _ in range(shots_per_delay)
    ) / shots_per_delay
    for probability in ideal_measurement_probabilities
]

noisy_figure, noisy_axes = plt.subplots()
noisy_axes.scatter(measurement_times, measured_excited_state_fraction)
noisy_axes.set_title("T1 Calibration with Finite-Shot Noise")
noisy_axes.set_xlabel("Time")
noisy_axes.set_ylabel("Measured excited-state fraction")
noisy_axes.set_ylim(0.0, 1.05)
noisy_axes.grid(True)
noisy_figure.tight_layout()
noisy_figure.savefig("t1_experiment_noisy.png")
print("Saved finite-shot plot to t1_experiment_noisy.png")
print("Estimate T1 from the noisy points and explain your reasoning.")

if plt.get_backend().lower() != "agg":
    plt.show()
```

- [ ] **Step 3: Re-run the finite-shot contract check**

Run the command from Step 1 again.

Expected: PASS with no output.

- [ ] **Step 4: Commit the script change**

```bash
git add exercise_ising_calibration/t1_experiment.py
git commit -m "feat: add finite-shot T1 plot"
```

### Task 2: Two-Plot Learner Workflow

**Files:**
- Modify: `exercise_ising_calibration/README.md`

- [ ] **Step 1: Run the failing README contract check**

Run from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("exercise_ising_calibration/README.md").read_text()
assert "t1_experiment.png" in text
assert "t1_experiment_noisy.png" in text
assert "64" in text
assert "finite-shot" in text.lower()
assert "estimate t1" in text.lower()
assert "explain" in text.lower()
PY
```

Expected: FAIL on the missing `t1_experiment_noisy.png` assertion.

- [ ] **Step 2: Explain and route both plots**

Replace `exercise_ising_calibration/README.md` with:

````markdown
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
````

- [ ] **Step 3: Re-run the README contract check**

Run the command from Step 1 again.

Expected: PASS with no output.

- [ ] **Step 4: Commit the README change**

```bash
git add exercise_ising_calibration/README.md
git commit -m "docs: explain finite-shot T1 result"
```

### Task 3: Runtime and Visual Verification

**Files:**
- Verify: `exercise_ising_calibration/t1_experiment.py`
- Verify: `/tmp/t1_experiment.png`
- Verify: `/tmp/t1_experiment_noisy.png`

- [ ] **Step 1: Compile without creating a repository cache**

Run from the repository root:

```bash
PYTHONPYCACHEPREFIX=/tmp/ising_calibration_pycache python3 -m py_compile exercise_ising_calibration/t1_experiment.py
```

Expected: exit status 0 with no output.

- [ ] **Step 2: Run the real simulation with numerical assertions**

Run from `/tmp` with the noninteractive backend and warnings promoted to
errors:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/ising_calibration_matplotlib PYTHONWARNINGS=error /home/mawolf/anaconda3/bin/python - <<'PY'
import math
import random
import runpy
from pathlib import Path

values = runpy.run_path(
    "/home/mawolf/gitlab_cudaq_ac/exercise_ising_calibration/t1_experiment.py"
)
times = values["time_steps"]
ideal = values["excited_state_probability"]
measurement_times = values["measurement_times"]
measurement_ideal = values["ideal_measurement_probabilities"]
measured = values["measured_excited_state_fraction"]
shots = values["shots_per_delay"]
t1 = values["t1"]

expected_generator = random.Random(7)
expected_measured = [
    sum(
        expected_generator.random() < probability
        for _ in range(shots)
    ) / shots
    for probability in measurement_ideal
]

assert len(times) == len(ideal) == 101
assert len(measurement_times) == len(measurement_ideal) == len(measured) == 21
assert shots == 64
assert abs(ideal[times.index(t1)] - 1.0 / math.e) < 0.01
assert measured == expected_measured
assert all(0.0 <= probability <= 1.0 for probability in measured)
assert any(
    abs(sample - probability) > 1e-6
    for sample, probability in zip(measured, measurement_ideal)
)
for filename in ("t1_experiment.png", "t1_experiment_noisy.png"):
    image = Path("/tmp") / filename
    assert image.is_file() and image.stat().st_size > 0

print(
    "Runtime verification: PASS "
    f"(P(T1)={ideal[times.index(t1)]:.3f}, noisy points={len(measured)})"
)
PY
```

Expected: clean exit with `P(T1)=0.368` and `noisy points=21`.

- [ ] **Step 3: Inspect both plots**

Open both PNGs and confirm that the ideal image is a smooth exponential line,
the noisy image contains only 21 unconnected scattered markers, and every
title and axis label is readable.

### Task 4: Final Scope Check

**Files:**
- Verify: `exercise_ising_calibration/README.md`
- Verify: `exercise_ising_calibration/t1_experiment.py`

- [ ] **Step 1: Check formatting and dependencies**

Run:

```bash
git diff --check 696c2ad..HEAD
rg -n "numpy|cupy" exercise_ising_calibration/README.md exercise_ising_calibration/t1_experiment.py
```

Expected: the diff check exits successfully. The dependency scan finds no
matches and exits with status 1.

- [ ] **Step 2: Confirm repository scope**

Run:

```bash
git status --short
```

Expected: only the pre-existing untracked root `.gitignore` may appear. No PNG,
cache, or sibling-exercise change appears.

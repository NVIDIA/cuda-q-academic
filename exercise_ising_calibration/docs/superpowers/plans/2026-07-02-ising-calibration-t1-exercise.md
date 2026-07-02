# Ising Calibration T1 Exercise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained workshop exercise that runs a clean CUDA-Q Dynamics T1 relaxation simulation, saves and displays a labeled plot, and sends learners to Ising Calibration for interpretation.

**Architecture:** The exercise has two learner-facing files. `t1_experiment.py` is a linear teaching script that owns simulation, console guidance, and plotting; `README.md` owns the learner workflow. Development checks are inline commands so the exercise does not gain a second Python file.

**Tech Stack:** Python 3, CUDA-Q Dynamics, Python standard library, Matplotlib

---

### Task 1: Learner Instructions

**Files:**
- Create: `exercise_ising_calibration/README.md`

- [ ] **Step 1: Run the failing README contract check**

Run from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path

readme = Path("exercise_ising_calibration/README.md")
assert readme.is_file()
text = readme.read_text()
assert "python3 t1_experiment.py" in text
assert "t1_experiment.png" in text
assert "https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b/playground" in text
assert "upload" in text.lower()
assert "interpret" in text.lower()
PY
```

Expected: FAIL because `exercise_ising_calibration/README.md` does not exist.

- [ ] **Step 2: Write the focused learner workflow**

Create `exercise_ising_calibration/README.md` with:

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
````

- [ ] **Step 3: Re-run the README contract check**

Run the command from Step 1 again.

Expected: PASS with no output.

- [ ] **Step 4: Commit the README**

```bash
git add exercise_ising_calibration/README.md
git commit -m "docs: add T1 calibration exercise instructions"
```

### Task 2: Clean CUDA-Q Dynamics Experiment

**Files:**
- Create: `exercise_ising_calibration/t1_experiment.py`

- [ ] **Step 1: Run the failing script contract check**

Run from the repository root:

```bash
python3 - <<'PY'
import ast
from pathlib import Path

script = Path("exercise_ising_calibration/t1_experiment.py")
assert script.is_file()
text = script.read_text()
ast.parse(text)
assert "numpy" not in text.lower()
assert "cupy" not in text.lower()
assert 'cudaq.set_target("dynamics")' in text
assert "cudaq.evolve(" in text
assert "collapse_operators=" in text
assert 'set_xlabel("Time")' in text
assert 'set_ylabel("Excited-state probability")' in text
assert 'savefig("t1_experiment.png")' in text
PY
```

Expected: FAIL because `exercise_ising_calibration/t1_experiment.py` does not
exist.

- [ ] **Step 2: Implement the minimal experiment**

Create `exercise_ising_calibration/t1_experiment.py` with:

```python
import math

import cudaq
import matplotlib.pyplot as plt
from cudaq import spin
from cudaq.dynamics import InitialState, Schedule


cudaq.set_target("dynamics")

# Model one two-level spin and watch it for five relaxation times.
t1 = 10.0
number_of_steps = 101
time_steps = [5.0 * t1 * step / (number_of_steps - 1)
              for step in range(number_of_steps)]
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
print("Saved plot to t1_experiment.png")
plt.show()
```

- [ ] **Step 3: Re-run the script contract check**

Run the command from Step 1 again.

Expected: PASS with no output.

- [ ] **Step 4: Commit the script**

```bash
git add exercise_ising_calibration/t1_experiment.py
git commit -m "feat: add CUDA-Q Dynamics T1 experiment"
```

### Task 3: Runtime Verification

**Files:**
- Verify: `exercise_ising_calibration/t1_experiment.py`
- Verify: `/tmp/t1_experiment.png`

- [ ] **Step 1: Compile the script**

Run from the repository root:

```bash
PYTHONPYCACHEPREFIX=/tmp/ising_calibration_pycache python3 -m py_compile exercise_ising_calibration/t1_experiment.py
```

Expected: exit status 0 with no output.

- [ ] **Step 2: Run the experiment without opening a GUI**

Run from `/tmp` so the generated verification image does not alter the
repository:

```bash
MPLBACKEND=Agg /home/mawolf/anaconda3/bin/python /home/mawolf/gitlab_cudaq_ac/exercise_ising_calibration/t1_experiment.py
```

Expected output includes:

```text
Expected result:
The excited-state probability should decay exponentially from 1 to 0.
At T1 = 10.0, it should be about 1/e = 0.37.
Saved plot to t1_experiment.png
```

- [ ] **Step 3: Verify the generated plot**

Run:

```bash
test -s /tmp/t1_experiment.png
file /tmp/t1_experiment.png
```

Expected: both commands succeed and `file` reports a nonempty PNG image.

- [ ] **Step 4: Inspect the plot**

Open `/tmp/t1_experiment.png` and confirm that the curve begins near 1,
decreases smoothly, is near 0.37 at time 10, and approaches 0 by time 50.
Confirm that the title and both axis labels are readable.

### Task 4: Final Scope and Repository Check

**Files:**
- Verify: `exercise_ising_calibration/README.md`
- Verify: `exercise_ising_calibration/t1_experiment.py`
- Verify: `exercise_ising_calibration/docs/superpowers/specs/2026-07-02-ising-calibration-t1-exercise-design.md`
- Verify: `exercise_ising_calibration/docs/superpowers/plans/2026-07-02-ising-calibration-t1-exercise.md`

- [ ] **Step 1: Check formatting and forbidden dependencies**

```bash
git diff --check HEAD~2..HEAD
rg -n "numpy|cupy" exercise_ising_calibration/README.md exercise_ising_calibration/t1_experiment.py
```

Expected: `git diff --check` exits successfully. `rg` finds no matches and
therefore exits with status 1.

- [ ] **Step 2: Confirm unrelated files remain untouched**

```bash
git status --short
```

Expected: the pre-existing untracked root `.gitignore` may remain. No generated
PNG, cache directory, or unrelated exercise change appears.

- [ ] **Step 3: Review recent commits**

```bash
git log -4 --oneline
```

Expected: recent history includes separate design, plan, README, and script
commits for the T1 exercise.

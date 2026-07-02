# Increase T1 Shot Noise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increase the finite-shot scatter in the noisy T1 plot by reducing each displayed estimate from 64 measurements to 32.

**Architecture:** Keep the CUDA-Q Dynamics simulation, 21 sampled delays, random seed, plotting, and filenames unchanged. Update the single shot-count parameter and its learner-facing explanation so the code and README remain consistent.

**Tech Stack:** Python 3, CUDA-Q Dynamics, Python standard library, Matplotlib pyplot

---

### Task 1: Reduce the Finite-Shot Count

**Files:**
- Modify: `exercise_ising_calibration/t1_experiment.py`
- Modify: `exercise_ising_calibration/README.md`

- [ ] **Step 1: Run the failing 32-shot contract check**

Run from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path

script = Path("exercise_ising_calibration/t1_experiment.py").read_text()
readme = Path("exercise_ising_calibration/README.md").read_text()
assert "shots_per_delay = 32" in script
assert "32 binary" in readme
assert "shots_per_delay = 64" not in script
assert "64 binary" not in readme
PY
```

Expected: FAIL because the script and README still specify 64 shots.

- [ ] **Step 2: Apply the minimal synchronized change**

In `exercise_ising_calibration/t1_experiment.py`, replace:

```python
shots_per_delay = 64
```

with:

```python
shots_per_delay = 32
```

In `exercise_ising_calibration/README.md`, replace:

```markdown
The finite-shot plot estimates each displayed probability from 64 binary
```

with:

```markdown
The finite-shot plot estimates each displayed probability from 32 binary
```

- [ ] **Step 3: Re-run the 32-shot contract check**

Run the command from Step 1 again.

Expected: PASS with no output.

- [ ] **Step 4: Commit the synchronized change**

```bash
git add exercise_ising_calibration/t1_experiment.py exercise_ising_calibration/README.md
git commit -m "tune: increase finite-shot T1 noise"
```

### Task 2: Runtime and Visual Verification

**Files:**
- Verify: `exercise_ising_calibration/t1_experiment.py`
- Verify: `/tmp/ising_calibration_32_shots/t1_experiment.png`
- Verify: `/tmp/ising_calibration_32_shots/t1_experiment_noisy.png`

- [ ] **Step 1: Compile without creating a repository cache**

```bash
PYTHONPYCACHEPREFIX=/tmp/ising_calibration_pycache python3 -m py_compile exercise_ising_calibration/t1_experiment.py
```

Expected: exit status 0 with no output.

- [ ] **Step 2: Create an isolated output directory**

```bash
mkdir -p /tmp/ising_calibration_32_shots
```

- [ ] **Step 3: Run the real CUDA-Q simulation with assertions**

Run from `/tmp/ising_calibration_32_shots`:

```bash
MPLCONFIGDIR=/tmp/ising_calibration_matplotlib PYTHONWARNINGS=error /home/mawolf/anaconda3/bin/python - <<'PY'
import math
import random
import runpy
from pathlib import Path

values = runpy.run_path(
    "/home/mawolf/gitlab_cudaq_ac/exercise_ising_calibration/t1_experiment.py"
)
ideal = values["ideal_measurement_probabilities"]
measured = values["measured_excited_state_fraction"]
shots = values["shots_per_delay"]

expected_generator = random.Random(7)
expected_measured = [
    sum(expected_generator.random() < probability for _ in range(shots)) / shots
    for probability in ideal
]

assert shots == 32
assert len(ideal) == len(measured) == 21
assert measured == expected_measured
assert all(0.0 <= probability <= 1.0 for probability in measured)
assert any(abs(a - b) > 1e-6 for a, b in zip(measured, ideal))
assert math.sqrt(0.25 / shots) > math.sqrt(0.25 / 64)
for filename in ("t1_experiment.png", "t1_experiment_noisy.png"):
    image = Path.cwd() / filename
    assert image.is_file() and image.stat().st_size > 0

print("Runtime verification: PASS (32 shots, 21 noisy points, 2 PNG files)")
PY
```

Expected: warning-free execution and the printed PASS line.

- [ ] **Step 4: Inspect the noisy plot**

Open `/tmp/ising_calibration_32_shots/t1_experiment_noisy.png` and confirm that
the 21 unconnected points show stronger scatter while the overall exponential
decay remains recognizable.

### Task 3: Final Scope Check

**Files:**
- Verify: `exercise_ising_calibration/t1_experiment.py`
- Verify: `exercise_ising_calibration/README.md`

- [ ] **Step 1: Check formatting and dependency scope**

```bash
git diff --check 3223574..HEAD
rg -n "numpy|cupy" exercise_ising_calibration/t1_experiment.py exercise_ising_calibration/README.md
```

Expected: the diff check succeeds. The dependency scan finds no matches and
exits with status 1.

- [ ] **Step 2: Confirm unrelated files remain untouched**

```bash
git status --short
```

Expected: the user's existing untracked `.gitignore`, `t1_experiment.png`, and
`t1_experiment_noisy.png` may remain. No unrelated tracked file is modified.

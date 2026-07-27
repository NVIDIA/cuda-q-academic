# Exercise Folder Cleanup and READMEs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 03/04 exercise contents with the approved source files and make the 02 and 03/04 READMEs describe only the files present.

**Architecture:** Treat each exercise directory as an independent workshop workspace. The 03/04 folder will have an exact six-file manifest: five Python files copied from the source workspace plus one orientation README; the 02 folder keeps its six Python files and receives a shorter orientation README.

**Tech Stack:** Markdown, Python file assets, shell manifest and byte-comparison checks

---

### Task 1: Clean and repopulate the 03/04 exercise

**Files:**
- Replace: `03_04_exercise_qaoa_and_adapt/adapt_qaoa.py`
- Create: `03_04_exercise_qaoa_and_adapt/qaoa_maxcut.py`
- Create: `03_04_exercise_qaoa_and_adapt/qaoa_maxcut_solvers.py`
- Create: `03_04_exercise_qaoa_and_adapt/workshop_graphs.py`
- Create: `03_04_exercise_qaoa_and_adapt/tests/test_qaoa_maxcut.py`
- Delete: `03_04_exercise_qaoa_and_adapt/.gitignore`
- Delete: `03_04_exercise_qaoa_and_adapt/assets/`
- Delete: `03_04_exercise_qaoa_and_adapt/maxcut_instances/`
- Delete: `03_04_exercise_qaoa_and_adapt/parallel_adapt_qaoa.py`
- Delete: `03_04_exercise_qaoa_and_adapt/results/`
- Delete: `03_04_exercise_qaoa_and_adapt/run_qedc_input.py`
- Delete: all test files except `tests/test_qaoa_maxcut.py`

- [ ] **Step 1: Remove the known legacy files and generated caches**

Remove only the explicitly scoped legacy paths from
`03_04_exercise_qaoa_and_adapt`. Do not modify another exercise directory.

- [ ] **Step 2: Copy the approved source files**

Copy these source paths byte-for-byte:

```text
/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa/adapt_qaoa.py
/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa/qaoa_maxcut.py
/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa/qaoa_maxcut_solvers.py
/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa/workshop_graphs.py
/home/mawolf/vibeshop-cudaq/03_04_qaoa_and_adapt_qaoa/tests/test_qaoa_maxcut.py
```

- [ ] **Step 3: Verify every copied file**

Run `cmp -s` between each source and destination path. Expected: every command
returns exit code 0.

### Task 2: Write the 03/04 file-orientation README

**Files:**
- Replace: `03_04_exercise_qaoa_and_adapt/README.md`

- [ ] **Step 1: Replace the README with this content**

```markdown
# QAOA and ADAPT-QAOA Exercise Files

The workshop handout provides the exercises; this README only identifies the
files included in this folder.

| File | Purpose |
| --- | --- |
| `workshop_graphs.py` | Defines the weighted MaxCut graphs shared by the QAOA examples and selects the graph to run. |
| `qaoa_maxcut.py` | Implements and runs MaxCut QAOA directly with CUDA-Q kernels and SciPy optimization. |
| `qaoa_maxcut_solvers.py` | Solves the same MaxCut problem through the higher-level CUDA-Q Solvers QAOA API. |
| `adapt_qaoa.py` | Implements ADAPT-QAOA for the selected weighted MaxCut graph. |
| `tests/test_qaoa_maxcut.py` | Checks the custom QAOA state and compares its optimized result with CUDA-Q Solvers. |
```

### Task 3: Shorten the exercise 02 README

**Files:**
- Replace: `02_exercise_cudaq_kernels/README.md`

- [ ] **Step 1: Replace the README with this content**

```markdown
# CUDA-Q Kernel Exercise Files

The workshop handout provides the exercises; this README only identifies the
files included in this folder.

| File | Purpose |
| --- | --- |
| `template_ghz_kernel.py` | Provides an incomplete GHZ kernel for practicing kernel arguments, circuit construction, sampling, and noise. |
| `solution_ghz_kernel.py` | Contains the completed GHZ kernel, sampling workflow, and depolarizing-noise example. |
| `run_ghz_template.py` | Provides an incomplete dynamic-kernel example using measurement, reset, control flow, and a typed return value. |
| `run_ghz_solution.py` | Contains the completed measurement-and-reset dynamic-kernel example. |
| `mps_observe.py` | Compares QAOA-chain expectation values from state-vector and matrix-product-state simulation. |
| `tensor_network_observe.py` | Evaluates a QAOA layer with the TensorNet simulator and contraction-path settings. |
```

### Task 4: Verify the final documentation and manifests

**Files:**
- Verify: `02_exercise_cudaq_kernels/`
- Verify: `03_04_exercise_qaoa_and_adapt/`

- [ ] **Step 1: Verify the 03/04 manifest**

Run:

```bash
find 03_04_exercise_qaoa_and_adapt -type f -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' -print | sort
```

Expected paths:

```text
03_04_exercise_qaoa_and_adapt/README.md
03_04_exercise_qaoa_and_adapt/adapt_qaoa.py
03_04_exercise_qaoa_and_adapt/qaoa_maxcut.py
03_04_exercise_qaoa_and_adapt/qaoa_maxcut_solvers.py
03_04_exercise_qaoa_and_adapt/tests/test_qaoa_maxcut.py
03_04_exercise_qaoa_and_adapt/workshop_graphs.py
```

- [ ] **Step 2: Verify the exercise 02 README covers every Python file**

Compare `rg --files 02_exercise_cudaq_kernels -g '*.py' | sort` with the six
README table entries. Expected: every Python path has one matching entry.

- [ ] **Step 3: Verify the exercise 03/04 README covers every Python file**

Compare `rg --files 03_04_exercise_qaoa_and_adapt -g '*.py' | sort` with the
five README table entries. Expected: every Python path has one matching entry.

- [ ] **Step 4: Review the scoped Git diff**

Run:

```bash
git status --short -- 02_exercise_cudaq_kernels 03_04_exercise_qaoa_and_adapt
git diff -- 02_exercise_cudaq_kernels 03_04_exercise_qaoa_and_adapt
```

Expected: only the approved exercise cleanup, copied files, and README changes.

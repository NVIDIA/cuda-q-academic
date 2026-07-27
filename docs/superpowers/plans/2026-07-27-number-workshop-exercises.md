# Numbered Workshop Exercises Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the wiki and QAOA workshop folders, add the existing CUDA-Q kernel examples as exercise 02, and finish cleaning the superseded QEC wrapper.

**Architecture:** Keep all workshop topics as flat top-level folders. Treat the numbered QAOA directory as an execution workspace rather than an importable Python package, so its modules and tests use sibling imports. Copy the six kernel examples byte-for-byte and document which files are intentionally incomplete templates.

**Tech Stack:** Git file moves, Python, CUDA-Q, pytest, Markdown, shell file comparison

---

## File Structure

- `demos_autoresearch/.gitignore`: ignore rules for the reorganized autoresearch demos.
- `demos_wiki_llm/`: renamed research wiki demo.
- `02_exercise_cudaq_kernels/README.md`: kernel exercise overview and run guidance.
- `02_exercise_cudaq_kernels/*.py`: six copied CUDA-Q examples and templates.
- `03_04_exercise_qaoa_and_adapt/`: renamed QAOA/ADAPT-QAOA exercise using local module imports.

### Task 1: Finish the QEC wrapper cleanup

**Files:**

- Move: `demo_qec_autoresearch/.gitignore` → `demos_autoresearch/.gitignore`
- Modify: `demos_autoresearch/.gitignore`

- [ ] **Step 1: Confirm the leftover is limited to the ignore file**

Run:

```bash
find demo_qec_autoresearch -maxdepth 2 -type f -print
git ls-files demo_qec_autoresearch
```

Expected: both commands identify only `demo_qec_autoresearch/.gitignore`.

- [ ] **Step 2: Move and update the ignore rules**

Run:

```bash
git mv demo_qec_autoresearch/.gitignore demos_autoresearch/.gitignore
rmdir demo_qec_autoresearch
```

Replace `demos_autoresearch/.gitignore` with:

```gitignore
**/__pycache__/
**/*.pyc
**/.pytest_cache/
**/output/data/
cudaq_qec_decoder/ready_to_run/output/ledger/
cudaq_qec_decoder/ready_to_run/output/plots/
reports/
```

- [ ] **Step 3: Verify the cleanup**

Run:

```bash
set -euo pipefail
test ! -e demo_qec_autoresearch
grep -F 'cudaq_qec_decoder/ready_to_run/output/ledger/' demos_autoresearch/.gitignore
grep -F 'cudaq_qec_decoder/ready_to_run/output/plots/' demos_autoresearch/.gitignore
```

Expected: the old wrapper is absent and both reorganized ready-to-run paths print.

- [ ] **Step 4: Commit**

```bash
git add demos_autoresearch/.gitignore
git commit -m "fix: finish autoresearch wrapper cleanup"
```

### Task 2: Rename the wiki demo

**Files:**

- Move: `exercise_wiki_llm/` → `demos_wiki_llm/`
- Modify: `demos_wiki_llm/README.md`

- [ ] **Step 1: Move the wiki**

Run:

```bash
git mv exercise_wiki_llm demos_wiki_llm
```

Expected: all wiki agent instructions, local skills, prompts, documents, and blank wiki files move together.

- [ ] **Step 2: Update participant prompt examples**

In both “Add Papers Later” prompt blocks in `demos_wiki_llm/README.md`,
replace:

```text
Work in exercise_wiki_llm.
```

with:

```text
Work in demos_wiki_llm.
```

- [ ] **Step 3: Verify the rename and local links**

Run:

```bash
set -euo pipefail
test ! -e exercise_wiki_llm
test -f demos_wiki_llm/AGENTS.md
test -f demos_wiki_llm/skills/ingest-research-paper/SKILL.md
! rg -n 'exercise_wiki_llm' demos_wiki_llm
python3 -c 'import pathlib,re; f=pathlib.Path("demos_wiki_llm/README.md"); links=re.findall(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)",f.read_text()); missing=[link for link in links if not (f.parent/link).exists()]; assert not missing,missing; print("wiki links valid")'
```

Expected: the old folder/reference is absent and `wiki links valid` prints.

- [ ] **Step 4: Commit**

```bash
git add demos_wiki_llm/README.md
git commit -m "refactor: rename research wiki as a demo"
```

### Task 3: Add the CUDA-Q kernels exercise

**Files:**

- Create: `02_exercise_cudaq_kernels/README.md`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/mps_observe.py`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/tensor_network_observe.py`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_template.py`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_solution.py`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/template_ghz_kernel.py`
- Copy: `~/vibeshop-cudaq/02_intro_to_cudaq/solution_ghz_kernel.py`

- [ ] **Step 1: Confirm the six source files**

Run:

```bash
set -euo pipefail
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/mps_observe.py
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/tensor_network_observe.py
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_template.py
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_solution.py
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/template_ghz_kernel.py
test -f ~/vibeshop-cudaq/02_intro_to_cudaq/solution_ghz_kernel.py
```

Expected: all assertions pass.

- [ ] **Step 2: Copy the source files**

Run:

```bash
mkdir -p 02_exercise_cudaq_kernels
cp ~/vibeshop-cudaq/02_intro_to_cudaq/mps_observe.py 02_exercise_cudaq_kernels/
cp ~/vibeshop-cudaq/02_intro_to_cudaq/tensor_network_observe.py 02_exercise_cudaq_kernels/
cp ~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_template.py 02_exercise_cudaq_kernels/
cp ~/vibeshop-cudaq/02_intro_to_cudaq/run_ghz_solution.py 02_exercise_cudaq_kernels/
cp ~/vibeshop-cudaq/02_intro_to_cudaq/template_ghz_kernel.py 02_exercise_cudaq_kernels/
cp ~/vibeshop-cudaq/02_intro_to_cudaq/solution_ghz_kernel.py 02_exercise_cudaq_kernels/
```

Expected: exactly six Python files exist in the new folder.

- [ ] **Step 3: Create the exercise README**

Create `02_exercise_cudaq_kernels/README.md` with:

```markdown
# CUDA-Q Kernels and GPU Simulators

This exercise introduces CUDA-Q kernels through two guided GHZ activities and
two complete GPU simulator examples.

## Prerequisites

Run these files from this folder in a Python environment with CUDA-Q installed.
The `nvidia`, `tensornet`, and `tensornet-mps` targets require a compatible
NVIDIA GPU and driver.

## Files

| File | Purpose |
| --- | --- |
| `run_ghz_template.py` | Intentionally incomplete kernel exercise covering typed returns, mid-circuit measurement, and reset. |
| `run_ghz_solution.py` | Completed solution for the mid-circuit kernel exercise. |
| `template_ghz_kernel.py` | Intentionally incomplete GHZ construction and sampling exercise. |
| `solution_ghz_kernel.py` | Completed GHZ construction, drawing, sampling, and noise example. |
| `mps_observe.py` | Complete state-vector versus MPS expectation-value comparison. |
| `tensor_network_observe.py` | Complete TensorNet expectation-value example with contraction-path settings. |

The two files with `template` in their names contain syntax-level placeholders
and are not expected to run until you complete them.

## Suggested workflow

1. Complete `template_ghz_kernel.py`, then compare it with
   `solution_ghz_kernel.py`.
2. Complete `run_ghz_template.py`, then compare it with
   `run_ghz_solution.py`.
3. Run the complete simulator examples:

   ```bash
   python mps_observe.py
   python tensor_network_observe.py
   ```

The simulator examples may take longer than the small GHZ exercises and require
GPU memory appropriate for their configured circuit sizes.
```

- [ ] **Step 4: Verify byte identity and complete-file syntax**

Run:

```bash
set -euo pipefail
for name in mps_observe.py tensor_network_observe.py run_ghz_template.py run_ghz_solution.py template_ghz_kernel.py solution_ghz_kernel.py; do
  cmp ~/vibeshop-cudaq/02_intro_to_cudaq/"$name" 02_exercise_cudaq_kernels/"$name"
done
python3 -c 'import ast,pathlib; names=("mps_observe.py","tensor_network_observe.py","run_ghz_solution.py","solution_ghz_kernel.py"); [ast.parse((pathlib.Path("02_exercise_cudaq_kernels")/name).read_text(),filename=name) for name in names]; print("four complete kernel examples parse")'
grep -F 'Intentionally incomplete' 02_exercise_cudaq_kernels/README.md
```

Expected: all six comparisons pass, the four complete examples parse, and both template rows are documented as intentionally incomplete.

- [ ] **Step 5: Smoke-test the CPU-compatible solution**

Run from `02_exercise_cudaq_kernels`:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/mawolf/cudaq-workspace/.venv/bin/python run_ghz_solution.py
```

Expected: exit code 0 and a ten-element result list. GPU-target scripts are not executed in this checkout because its CUDA driver is older than the installed CUDA runtime; byte identity and syntax checks cover their import into the workshop.

- [ ] **Step 6: Commit**

```bash
git add 02_exercise_cudaq_kernels
git commit -m "feat: add CUDA-Q kernels exercise"
```

### Task 4: Rename and adapt the QAOA exercise

**Files:**

- Move: `exercise_adapt_qaoa/` → `03_04_exercise_qaoa_and_adapt/`
- Modify: `03_04_exercise_qaoa_and_adapt/README.md`
- Modify: `03_04_exercise_qaoa_and_adapt/adapt_qaoa.py`
- Modify: `03_04_exercise_qaoa_and_adapt/parallel_adapt_qaoa.py`
- Modify: `03_04_exercise_qaoa_and_adapt/run_qedc_input.py`
- Modify: `03_04_exercise_qaoa_and_adapt/tests/test_adapt_qaoa.py`
- Modify: `03_04_exercise_qaoa_and_adapt/tests/test_qedc_inputs.py`
- Preserve locally: `03_04_exercise_qaoa_and_adapt/results/`
- Remove: generated `.pytest_cache/` and `__pycache__/` directories

- [ ] **Step 1: Run the baseline tests**

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/mawolf/cudaq-workspace/.venv/bin/python -m pytest -p no:cacheprovider exercise_adapt_qaoa/tests -q
```

Expected: `11 passed`.

- [ ] **Step 2: Rename the complete exercise directory**

Run:

```bash
git mv exercise_adapt_qaoa 03_04_exercise_qaoa_and_adapt
```

Expected: tracked source and ignored local results move together.

- [ ] **Step 3: Verify the existing tests expose the old imports**

Run from `03_04_exercise_qaoa_and_adapt`:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/mawolf/cudaq-workspace/.venv/bin/python -m pytest -p no:cacheprovider tests -q
```

Expected: test collection fails with `ModuleNotFoundError` for
`exercise_adapt_qaoa`, proving that the package-name dependency must be
removed.

- [ ] **Step 4: Convert source files to sibling imports**

In `adapt_qaoa.py`:

1. Change the docstring command to:

   ```text
   python adapt_qaoa.py
   ```

2. Remove `import sys`.
3. Remove the `PROJECT_ROOT` path-manipulation block.
4. Replace the package/fallback import block with:

   ```python
   from run_qedc_input import DEFAULT_QEDC_INSTANCE, load_qedc_maxcut
   ```

Make the same import and path-cleanup changes in `parallel_adapt_qaoa.py`, but
use this file-specific docstring command:

```text
python parallel_adapt_qaoa.py
```

In `run_qedc_input.py`:

1. Change the example commands to:

   ```text
   python run_qedc_input.py --list
   python run_qedc_input.py mc_004_003_000
   ```

2. Remove `import sys`.
3. Remove the `PROJECT_ROOT` path-manipulation block.
4. In `main`, replace the package import with:

   ```python
   from adapt_qaoa import RunSettings, run_adapt_qaoa
   ```

- [ ] **Step 5: Convert tests to the active-folder workflow**

In `tests/test_adapt_qaoa.py`, use:

```python
from adapt_qaoa import (
    MANUAL_EDGES,
    MANUAL_QUBITS,
    QEDC_INSTANCE,
    PROBLEM_SOURCE,
    RunSettings,
    choose_problem,
    run_adapt_qaoa,
    run_from_top_level_settings,
)
```

and change the direct-script subprocess command to:

```python
[sys.executable, "adapt_qaoa.py"]
```

In `tests/test_qedc_inputs.py`, use:

```python
from run_qedc_input import (
    DEFAULT_DATA_DIR,
    DEFAULT_QEDC_INSTANCE,
    QedcInputError,
    build_parser,
    list_qedc_instances,
    load_qedc_maxcut,
)
```

and change the listing subprocess command to:

```python
[sys.executable, "run_qedc_input.py", "--list"]
```

- [ ] **Step 6: Update README packaging guidance**

Replace the old package-folder reference with:

```markdown
- ☐ **Package the exercise folder.** Ask AI to create a zip file of the full
  `03_04_exercise_qaoa_and_adapt/` folder, including code, tests, benchmark
  outputs, plots or reports, planning notes, and saved conversations.
```

- [ ] **Step 7: Remove generated caches while preserving results**

Run:

```bash
rm -rf 03_04_exercise_qaoa_and_adapt/.pytest_cache
rm -rf 03_04_exercise_qaoa_and_adapt/__pycache__
rm -rf 03_04_exercise_qaoa_and_adapt/tests/__pycache__
test -f 03_04_exercise_qaoa_and_adapt/results/manual_4q_complete_adapt_qaoa.json
test -f 03_04_exercise_qaoa_and_adapt/results/mc_008_005_000_adapt_qaoa.json
```

Expected: caches are absent and both existing local result files remain.

- [ ] **Step 8: Run the renamed exercise tests**

Run from `03_04_exercise_qaoa_and_adapt`:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/mawolf/cudaq-workspace/.venv/bin/python -m pytest -p no:cacheprovider tests -q
```

Expected: `11 passed`.

- [ ] **Step 9: Verify old references are gone**

Run:

```bash
set -euo pipefail
test ! -e exercise_adapt_qaoa
! rg -n 'exercise_adapt_qaoa' 03_04_exercise_qaoa_and_adapt
```

Expected: both assertions pass.

- [ ] **Step 10: Commit**

```bash
git add 03_04_exercise_qaoa_and_adapt
git commit -m "refactor: number the QAOA and ADAPT exercise"
```

### Task 5: Verify the completed reorganization

**Files:**

- Verify: `demos_autoresearch/`
- Verify: `demos_wiki_llm/`
- Verify: `02_exercise_cudaq_kernels/`
- Verify: `03_04_exercise_qaoa_and_adapt/`

- [ ] **Step 1: Verify the final top-level structure**

Run:

```bash
set -euo pipefail
test -d demos_autoresearch
test -d demos_wiki_llm
test -d 02_exercise_cudaq_kernels
test -d 03_04_exercise_qaoa_and_adapt
test ! -e demo_qec_autoresearch
test ! -e exercise_wiki_llm
test ! -e exercise_adapt_qaoa
find . -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort
```

Expected: the requested folders appear and all three superseded folders are absent.

- [ ] **Step 2: Re-run byte, syntax, and reference checks**

Run:

```bash
set -euo pipefail
for name in mps_observe.py tensor_network_observe.py run_ghz_template.py run_ghz_solution.py template_ghz_kernel.py solution_ghz_kernel.py; do
  cmp ~/vibeshop-cudaq/02_intro_to_cudaq/"$name" 02_exercise_cudaq_kernels/"$name"
done
python3 -c 'import ast,pathlib; names=("mps_observe.py","tensor_network_observe.py","run_ghz_solution.py","solution_ghz_kernel.py"); [ast.parse((pathlib.Path("02_exercise_cudaq_kernels")/name).read_text(),filename=name) for name in names]; print("complete kernel files parse")'
! rg -n 'exercise_wiki_llm' demos_wiki_llm
! rg -n 'exercise_adapt_qaoa' 03_04_exercise_qaoa_and_adapt
```

Expected: copied sources match, complete files parse, and old references are absent.

- [ ] **Step 3: Re-run QAOA tests**

Run from `03_04_exercise_qaoa_and_adapt`:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/mawolf/cudaq-workspace/.venv/bin/python -m pytest -p no:cacheprovider tests -q
```

Expected: `11 passed`.

- [ ] **Step 4: Validate local README links**

Run:

```bash
python3 -c 'import pathlib,re; files=[pathlib.Path("demos_autoresearch/README.md"),pathlib.Path("demos_wiki_llm/README.md"),pathlib.Path("02_exercise_cudaq_kernels/README.md"),pathlib.Path("03_04_exercise_qaoa_and_adapt/README.md")]; missing=[]; pattern=re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)"); [(missing.append(f"{f}:{link}") if not (f.parent/link).exists() else None) for f in files for link in pattern.findall(f.read_text())]; assert not missing,missing; print("local README links valid")'
```

Expected: `local README links valid`.

- [ ] **Step 5: Check cache, ignore, and Git state**

Run:

```bash
set -euo pipefail
! find demos_wiki_llm 02_exercise_cudaq_kernels 03_04_exercise_qaoa_and_adapt -type d \( -name __pycache__ -o -name .pytest_cache \) -print -quit | grep -q .
grep -F 'cudaq_qec_decoder/ready_to_run/output/ledger/' demos_autoresearch/.gitignore
grep -F 'cudaq_qec_decoder/ready_to_run/output/plots/' demos_autoresearch/.gitignore
git diff --check
! git status --porcelain | grep -q .
```

Expected: no caches, correct ignore paths, no whitespace errors, and clean Git status.

# Workshop Repository Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Group the CUDA-Q autoresearch demos by topic, retain only the remote-backed Ising calibration exercise, and add the requested optional calibration notebook.

**Architecture:** Replace the QEC-only demo wrapper with a two-topic `demos_autoresearch` hierarchy. Move the existing QEC variants into concise `completed` and `ready_to_run` directories, import equivalently named TensorNet variants from the local source repository while filtering transient files, and rename the retained calibration exercise to the workshop's numbered name.

**Tech Stack:** Git file moves, Markdown, Jupyter Notebook JSON, Python, pytest, rsync

---

## File Structure

- `demos_autoresearch/README.md`: entry point for all autoresearch demos.
- `demos_autoresearch/cudaq_qec_decoder/README.md`: QEC decoder demo overview.
- `demos_autoresearch/cudaq_qec_decoder/completed/`: existing completed QEC study.
- `demos_autoresearch/cudaq_qec_decoder/ready_to_run/`: existing clean QEC starter.
- `demos_autoresearch/cudaq_tensornet/README.md`: TensorNet demo overview.
- `demos_autoresearch/cudaq_tensornet/completed/`: imported completed TensorNet study.
- `demos_autoresearch/cudaq_tensornet/ready_to_run/`: imported clean TensorNet starter.
- `01_exercise_ising_calibration/README.md`: retained remote calibration exercise plus optional-notebook guidance.
- `01_exercise_ising_calibration/calibration_example.png`: retained remote example image.
- `01_exercise_ising_calibration/optional_intro_ising_calibration.ipynb`: downloaded optional notebook.
- Remove `demo_qec_autoresearch/`.
- Remove `exercise_calibration/` after its contents move to the numbered directory.
- Remove the extra local `exercise_ising_calibration/` and all of its contents.

### Task 1: Reorganize the QEC autoresearch demo

**Files:**

- Move: `demo_qec_autoresearch/README.md` → `demos_autoresearch/cudaq_qec_decoder/README.md`
- Move: `demo_qec_autoresearch/completed_qec_autoresearch/` → `demos_autoresearch/cudaq_qec_decoder/completed/`
- Move: `demo_qec_autoresearch/ready_to_run_qec_autoresearch/` → `demos_autoresearch/cudaq_qec_decoder/ready_to_run/`
- Create: `demos_autoresearch/README.md`
- Modify: `demos_autoresearch/cudaq_qec_decoder/README.md`

- [ ] **Step 1: Record the pre-move state**

Run:

```bash
git status --short
test -d demo_qec_autoresearch/completed_qec_autoresearch
test -d demo_qec_autoresearch/ready_to_run_qec_autoresearch
```

Expected: only the two previously approved untracked T1 plot files are unrelated to the design/plan commits, and both QEC variants exist.

- [ ] **Step 2: Move the QEC wrapper and variants**

Run:

```bash
git mv demo_qec_autoresearch demos_autoresearch
mkdir -p demos_autoresearch/cudaq_qec_decoder
git mv demos_autoresearch/README.md demos_autoresearch/cudaq_qec_decoder/README.md
git mv demos_autoresearch/completed_qec_autoresearch demos_autoresearch/cudaq_qec_decoder/completed
git mv demos_autoresearch/ready_to_run_qec_autoresearch demos_autoresearch/cudaq_qec_decoder/ready_to_run
```

Expected: both QEC variants now live below `cudaq_qec_decoder`, and no `demo_qec_autoresearch` directory remains.

- [ ] **Step 3: Update the QEC topic README**

Replace its variant list with:

````markdown
# CUDA-Q QEC Decoder Autoresearch

This topic contains two self-contained versions of the CUDA-Q QLDPC decoder
autoresearch exercise.

- [`completed/`](completed/) preserves a complete 15-round run so you can
  inspect its hypotheses, ledger, plots, and final decoder.
- [`ready_to_run/`](ready_to_run/) starts from the baseline decoder with empty
  notes and output, ready for a new run.

Enter the variant you want, start Codex there, and prompt:

```text
Read AGENTS.md and run autoresearch for N iterations.
```
````

- [ ] **Step 4: Create the umbrella README**

Create `demos_autoresearch/README.md` with:

```markdown
# CUDA-Q Autoresearch Demos

These demos show agents running iterative CUDA-Q research against fixed
evaluation harnesses. Each topic provides a completed study for inspection and
a clean copy ready for a new run.

| Topic | Description |
| --- | --- |
| [`cudaq_qec_decoder/`](cudaq_qec_decoder/) | Improve a CUDA-Q QLDPC decoder across fixed error-correction datasets. |
| [`cudaq_tensornet/`](cudaq_tensornet/) | Optimize CUDA-Q TensorNet simulator settings for two fixed circuits. |

Within a topic, choose `completed/` to inspect prior results or
`ready_to_run/` to launch a fresh autoresearch study.
```

- [ ] **Step 5: Check the moved QEC files**

Run:

```bash
test -f demos_autoresearch/cudaq_qec_decoder/completed/AGENTS.md
test -f demos_autoresearch/cudaq_qec_decoder/ready_to_run/AGENTS.md
test ! -e demo_qec_autoresearch
```

Expected: all three assertions pass.

- [ ] **Step 6: Commit the QEC reorganization**

```bash
git add -A -- demos_autoresearch demo_qec_autoresearch
git commit -m "refactor: group QEC autoresearch demo by topic"
```

### Task 2: Import the TensorNet autoresearch demo

**Files:**

- Create: `demos_autoresearch/cudaq_tensornet/README.md`
- Create: `demos_autoresearch/cudaq_tensornet/completed/`
- Create: `demos_autoresearch/cudaq_tensornet/ready_to_run/`
- Modify: `demos_autoresearch/cudaq_tensornet/{completed,ready_to_run}/AGENTS.md`
- Modify: `demos_autoresearch/cudaq_tensornet/{completed,ready_to_run}/README.md`
- Source: `/home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_completed/`
- Source: `/home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_ready_to_run/`

- [ ] **Step 1: Confirm the source variants**

Run:

```bash
test -f /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_completed/AGENTS.md
test -f /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_completed/research/nonlocal/results.tsv
test -f /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_ready_to_run/AGENTS.md
test ! -e /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_ready_to_run/research/nonlocal/results.tsv
```

Expected: the completed copy has results, while the ready-to-run copy does not.

- [ ] **Step 2: Copy both variants without transient local files**

Run:

```bash
mkdir -p demos_autoresearch/cudaq_tensornet/completed
mkdir -p demos_autoresearch/cudaq_tensornet/ready_to_run
rsync -a --exclude '__pycache__/' --exclude '.pytest_cache/' --exclude '.mplconfig/' --exclude '.gpu.lock' /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_completed/ demos_autoresearch/cudaq_tensornet/completed/
rsync -a --exclude '__pycache__/' --exclude '.pytest_cache/' --exclude '.mplconfig/' --exclude '.gpu.lock' /home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_ready_to_run/ demos_autoresearch/cudaq_tensornet/ready_to_run/
```

Expected: the study code and completed artifacts are copied, with no machine-local caches or lock.

- [ ] **Step 3: Make the runnable commands portable**

In both imported `AGENTS.md` files, replace:

```text
/home/mawolf/cudaq-workspace/.venv/bin/python \
  run_round.py <nonlocal-or-controlled>
```

with:

```text
python run_round.py <nonlocal-or-controlled>
```

In both imported variant `README.md` files, replace the two machine-specific
commands with:

```bash
python run_round.py nonlocal
```

and:

```bash
python run_round.py controlled
```

In the completed `research/*/logs/` files, replace the machine-specific Python
interpreter and source-directory prefixes in each command header with `python`
and paths relative to the completed project. Do not alter experimental
settings, timings, results, rationales, or conclusions.

- [ ] **Step 4: Create the TensorNet topic README**

Create `demos_autoresearch/cudaq_tensornet/README.md` with:

```markdown
# CUDA-Q TensorNet Autoresearch

This topic contains two self-contained versions of the CUDA-Q TensorNet
performance autoresearch demo.

- [`completed/`](completed/) preserves the completed per-circuit ledgers,
  logs, findings, plots, and combined summary.
- [`ready_to_run/`](ready_to_run/) retains the fixed benchmark and baseline
  proposals with no prior ledgers or logs.

Enter the variant you want and read its `README.md` and authoritative
`AGENTS.md` before running the study. A CUDA-capable NVIDIA GPU and a CUDA-Q
installation with the TensorNet backend are required for evaluations.
```

- [ ] **Step 5: Verify the import boundary**

Run:

```bash
find demos_autoresearch/cudaq_tensornet -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mplconfig \) -print
find demos_autoresearch/cudaq_tensornet -type f -name .gpu.lock -print
test -f demos_autoresearch/cudaq_tensornet/completed/research/controlled/results.tsv
test -f demos_autoresearch/cudaq_tensornet/completed/results.png
test ! -e demos_autoresearch/cudaq_tensornet/ready_to_run/research/controlled/results.tsv
! rg -n '/home/mawolf' demos_autoresearch/cudaq_tensornet/{completed,ready_to_run}/{AGENTS.md,README.md}
```

Expected: both `find` commands print nothing, completed artifacts exist, and ready-to-run ledgers do not.

- [ ] **Step 6: Commit the TensorNet import**

```bash
git add demos_autoresearch
git commit -m "feat: add CUDA-Q TensorNet autoresearch demos"
```

### Task 3: Consolidate the calibration exercise

**Files:**

- Move: `exercise_calibration/` → `01_exercise_ising_calibration/`
- Remove: `exercise_ising_calibration/`
- Create: `01_exercise_ising_calibration/optional_intro_ising_calibration.ipynb`
- Modify: `01_exercise_ising_calibration/README.md`

- [ ] **Step 1: Move the remote-backed exercise**

Run:

```bash
git mv exercise_calibration 01_exercise_ising_calibration
```

Expected: `README.md` and `calibration_example.png` move together.

- [ ] **Step 2: Remove the extra local exercise**

Run:

```bash
rm exercise_ising_calibration/t1_experiment.png
rm exercise_ising_calibration/t1_experiment_noisy.png
git rm -r exercise_ising_calibration
```

Expected: the old T1 script, generated plots, and local design records are gone; only the remote-backed exercise remains under its numbered name.

- [ ] **Step 3: Download the optional notebook**

Run:

```bash
curl --fail --location https://raw.githubusercontent.com/Squirtle007/cudaq-agentic-coding/main/_intro_Ising_Calibration.ipynb --output 01_exercise_ising_calibration/optional_intro_ising_calibration.ipynb
```

Expected: HTTP succeeds and writes a non-empty notebook JSON file.

- [ ] **Step 4: Add optional exercise guidance**

Append to `01_exercise_ising_calibration/README.md`:

```markdown

## Optional notebook exercise

For an additional guided activity, open
[`optional_intro_ising_calibration.ipynb`](optional_intro_ising_calibration.ipynb)
in Jupyter and work through the notebook after completing the playground
exercise above. This notebook is optional and is not required for the main
calibration workflow.
```

- [ ] **Step 5: Validate the calibration folder**

Run:

```bash
python -m json.tool 01_exercise_ising_calibration/optional_intro_ising_calibration.ipynb >/dev/null
test -f 01_exercise_ising_calibration/calibration_example.png
test ! -e exercise_calibration
test ! -e exercise_ising_calibration
```

Expected: the notebook parses as JSON, the sample image exists, and both superseded top-level paths are absent.

- [ ] **Step 6: Commit the calibration consolidation**

```bash
git add -A
git commit -m "refactor: consolidate Ising calibration exercise"
```

### Task 4: Verify the reorganized workshop

**Files:**

- Verify: `demos_autoresearch/`
- Verify: `01_exercise_ising_calibration/`

- [ ] **Step 1: Parse every imported Python file**

Run:

```bash
python -c 'import ast, pathlib; files=list(pathlib.Path("demos_autoresearch").rglob("*.py")); [ast.parse(path.read_text(), filename=str(path)) for path in files]; print(f"parsed {len(files)} Python files")'
```

Expected: all Python files parse and the command prints the parsed file count.

- [ ] **Step 2: Run the QEC plotting tests**

Run from `demos_autoresearch/cudaq_qec_decoder/completed`:

```bash
python -m pytest tests/test_plot_ledger.py -q
```

Then run the same command from
`demos_autoresearch/cudaq_qec_decoder/ready_to_run`.

Expected: each variant reports `1 passed`.

- [ ] **Step 3: Validate TensorNet state and JSON files**

Run:

```bash
python -c 'import json, pathlib; roots=[pathlib.Path("demos_autoresearch/cudaq_tensornet/completed"), pathlib.Path("demos_autoresearch/cudaq_tensornet/ready_to_run")]; [json.loads((root / "reference.json").read_text()) for root in roots]; assert (roots[0] / "research/nonlocal/results.tsv").exists(); assert not (roots[1] / "research/nonlocal/results.tsv").exists(); print("TensorNet variants valid")'
```

Expected: `TensorNet variants valid`.

- [ ] **Step 4: Check local Markdown links**

Run:

```bash
python -c 'import pathlib,re; files=[pathlib.Path("demos_autoresearch/README.md"),pathlib.Path("demos_autoresearch/cudaq_qec_decoder/README.md"),pathlib.Path("demos_autoresearch/cudaq_tensornet/README.md"),pathlib.Path("01_exercise_ising_calibration/README.md")]; missing=[]; pattern=re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)"); [(missing.append(f"{f}:{link}") if not (f.parent/link).exists() else None) for f in files for link in pattern.findall(f.read_text())]; assert not missing, missing; print("local README links valid")'
```

Expected: `local README links valid`.

- [ ] **Step 5: Inspect the final diff and worktree**

Run:

```bash
git diff --check
git status --short
find demos_autoresearch -maxdepth 3 -type d | sort
find 01_exercise_ising_calibration -maxdepth 1 -type f | sort
```

Expected: no whitespace errors; only intended committed changes are present; the final hierarchy matches the design.

- [ ] **Step 6: Record any verification-only correction**

If verification required a documentation or packaging correction, stage only those files and run:

```bash
git commit -m "fix: finalize workshop reorganization"
```

Expected: either a small verification-fix commit is created, or this step is skipped because no correction was needed.

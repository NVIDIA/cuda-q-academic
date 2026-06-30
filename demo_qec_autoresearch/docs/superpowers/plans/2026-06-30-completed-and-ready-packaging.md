# Completed and Ready QEC Autoresearch Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing QEC autoresearch exercise as a completed 15-round example and a clean ready-to-run example under one documented parent directory.

**Architecture:** Build two self-contained runnable snapshots from the current exercise before removing the old root-level runnable files. Keep only development specifications at the parent level, make the two child README and AGENTS files byte-identical, and distinguish variants solely through decoder, notes, and output state.

**Tech Stack:** Python 3, CUDA-Q QEC, pytest, Markdown, JSON Lines, Git ignore rules

---

### Task 1: Snapshot the two runnable variants

**Files:**
- Create: `completed_qec_autoresearch/`
- Create: `ready_to_run_qec_autoresearch/`
- Preserve source: `decoders/qldpc_agent/decoder_initial_settings.py`

- [ ] **Step 1: Record the initial and completed decoder hashes**

Run:

```bash
sha256sum decoders/qldpc_agent/decoder.py decoders/qldpc_agent/decoder_initial_settings.py
```

Expected: two distinct hashes, proving that the final and initial decoder states are both available before restructuring.

- [ ] **Step 2: Create variant directories**

Run:

```bash
mkdir -p completed_qec_autoresearch ready_to_run_qec_autoresearch
```

Expected: both directories exist and are empty.

- [ ] **Step 3: Copy the current runnable project into the completed variant**

Run:

```bash
cp -a AGENTS.md README.md decoders scripts tests completed_qec_autoresearch/
mkdir -p completed_qec_autoresearch/docs completed_qec_autoresearch/output
cp docs/QLDPC_DECODER_SUMMARY.md completed_qec_autoresearch/docs/
cp -a output/ledger output/plots completed_qec_autoresearch/output/
touch completed_qec_autoresearch/output/.gitkeep
```

Expected: the completed copy contains the final decoder, 15 notes entries, ledger, plots, scripts, tests, and reference documentation, but no dataset directory.

- [ ] **Step 4: Copy shared runnable content into the ready variant**

Run:

```bash
cp -a AGENTS.md README.md scripts tests ready_to_run_qec_autoresearch/
mkdir -p ready_to_run_qec_autoresearch/decoders/qldpc_agent ready_to_run_qec_autoresearch/docs ready_to_run_qec_autoresearch/output
cp docs/QLDPC_DECODER_SUMMARY.md ready_to_run_qec_autoresearch/docs/
cp decoders/qldpc_agent/decoder_initial_settings.py ready_to_run_qec_autoresearch/decoders/qldpc_agent/decoder.py
touch ready_to_run_qec_autoresearch/output/.gitkeep
```

Expected: the ready copy contains the initial decoder and no generated result directories.

### Task 2: Write parent and shared documentation

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`
- Modify identically: `completed_qec_autoresearch/README.md`
- Modify identically: `ready_to_run_qec_autoresearch/README.md`
- Modify identically: `completed_qec_autoresearch/AGENTS.md`
- Modify identically: `ready_to_run_qec_autoresearch/AGENTS.md`

- [ ] **Step 1: Replace the parent README**

Use `apply_patch` to make `README.md` a short variant guide containing:

````markdown
# QEC Autoresearch Examples

This directory contains two self-contained versions of the CUDA-Q QEC
autoresearch exercise.

- `completed_qec_autoresearch/` preserves a complete 15-round run so you can
  inspect its hypotheses, ledger, plots, and final decoder.
- `ready_to_run_qec_autoresearch/` starts from the baseline decoder with empty
  notes and output, ready for a new run.

Enter the variant you want, start Codex there, and prompt:

```text
Read AGENTS.md and run autoresearch for N iterations.
```
````

- [ ] **Step 2: Replace the parent ignore rules**

Use `apply_patch` so `.gitignore` contains:

```gitignore
**/__pycache__/
**/*.pyc
**/.pytest_cache/
**/output/data/
ready_to_run_qec_autoresearch/output/ledger/
ready_to_run_qec_autoresearch/output/plots/
reports/
```

Expected: downloaded data and caches are ignored everywhere, future ready-run results are ignored, and completed results are not ignored.

- [ ] **Step 3: Make the child README state-neutral and portable**

Use `apply_patch` on `completed_qec_autoresearch/README.md`, then copy that
exact file to `ready_to_run_qec_autoresearch/README.md`. Preserve the existing
overview and folder-layout material while making these exact edits:

```text
Replace the "From the workshop root" paragraph and `cd` block with: "Start Codex from this exercise directory, then prompt the agent:"
"Starts empty except `.gitkeep`." -> "May be empty or may contain datasets, ledger rows, and plots from prior rounds."
Replace every absolute virtual-environment interpreter prefix before `scripts/run_round.py` with `python`.
```

Add this sentence immediately after the output table:

```markdown
If `output/` already contains a ledger, new rounds continue from that history;
otherwise the first round creates it.
```

Expected: the shared README is state-neutral, portable, and documents dataset
download plus ledger and plot paths.

- [ ] **Step 4: Normalize the child AGENTS guide**

Use `apply_patch` on `completed_qec_autoresearch/AGENTS.md`, then copy that exact file to `ready_to_run_qec_autoresearch/AGENTS.md`. Make these exact edits:

```text
"Generated datasets, ledger, and plots. Starts empty except `.gitkeep`." -> "Generated datasets, ledger, and plots; may contain prior rounds."
Replace the absolute virtual-environment interpreter prefix before `scripts/run_round.py` with `python`.
```

The resulting evaluator command is:

```bash
python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30
```

Expected: the exploration guidance and edit boundaries remain unchanged.

### Task 3: Finalize variant-specific decoder and notes state

**Files:**
- Preserve: `completed_qec_autoresearch/decoders/qldpc_agent/decoder.py`
- Preserve: `completed_qec_autoresearch/decoders/qldpc_agent/NOTES.md`
- Create: `ready_to_run_qec_autoresearch/decoders/qldpc_agent/NOTES.md`
- Remove: `completed_qec_autoresearch/decoders/qldpc_agent/decoder_initial_settings.py`

- [ ] **Step 1: Create the clean notes template**

Use `apply_patch` to create `ready_to_run_qec_autoresearch/decoders/qldpc_agent/NOTES.md` with exactly:

```markdown
# QLDPC Autoresearch Notes

Use this file as the run log. For each iteration, record:

- hypothesis
- exact decoder change
- command run
- five-dataset result summary
- worst-case dataset
- next idea
```

- [ ] **Step 2: Remove the redundant completed baseline file**

Run:

```bash
rm completed_qec_autoresearch/decoders/qldpc_agent/decoder_initial_settings.py
```

Expected: each variant has exactly one canonical editable decoder at `decoders/qldpc_agent/decoder.py`.

- [ ] **Step 3: Verify decoder state constants**

Run in the completed variant:

```bash
python -c "from decoders.qldpc_agent import decoder as d; print(d.MAX_ITERATIONS, d.BP_METHOD, d.OSD_METHOD, d.OSD_ORDER, d.SCALE_FACTOR, d.PROC_FLOAT)"
```

Expected: `90 0 3 2 None fp32`.

Run in the ready variant:

```bash
python -c "from decoders.qldpc_agent import decoder as d; print(d.MAX_ITERATIONS, d.BP_METHOD, d.OSD_METHOD, d.OSD_ORDER, d.SCALE_FACTOR, d.PROC_FLOAT)"
```

Expected: `30 1 1 0 0.75 fp32`.

### Task 4: Sanitize preserved completed-run metadata

**Files:**
- Modify: `completed_qec_autoresearch/decoders/qldpc_agent/NOTES.md`
- Modify: `completed_qec_autoresearch/output/ledger/experiments.jsonl`

- [ ] **Step 1: Normalize all recorded commands in NOTES**

Run this mechanical replacement, which accepts any local username without
embedding it in the packaged files:

```bash
sed -E -i 's#/home/[^/]+/cudaq-workspace/\.venv/bin/python scripts/run_round\.py#python scripts/run_round.py#g' completed_qec_autoresearch/decoders/qldpc_agent/NOTES.md
```

Expected: all 15 note entries retain their hypotheses and measurements, with
no user-specific absolute path.

- [ ] **Step 2: Normalize ledger decoder paths**

Run this JSON-aware mechanical rewrite:

```bash
python -c 'import json, pathlib; p=pathlib.Path("completed_qec_autoresearch/output/ledger/experiments.jsonl"); rows=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]; [row.__setitem__("decoder_path", "decoders/qldpc_agent/decoder.py") for row in rows]; p.write_text("".join(json.dumps(row, sort_keys=True) + "\\n" for row in rows))'
```

It changes every `decoder_path` value to:

```json
"decoder_path": "decoders/qldpc_agent/decoder.py"
```

Expected: all other JSON fields retain their original values and ordering.

- [ ] **Step 3: Verify completed evidence counts**

Run:

```bash
wc -l completed_qec_autoresearch/output/ledger/experiments.jsonl
rg -c '^## Iteration [0-9]+$' completed_qec_autoresearch/decoders/qldpc_agent/NOTES.md
find completed_qec_autoresearch/output/plots -maxdepth 1 -name 'round_*.png' -type f | wc -l
```

Expected output is `75`, `15`, and `15` respectively.

### Task 5: Remove obsolete root-level runnable material

**Files:**
- Remove: root-level `AGENTS.md`, `decoders/`, `scripts/`, `tests/`, `output/`
- Remove: old files under `docs/superpowers/plans/` and `docs/superpowers/specs/`
- Preserve: current packaging plan and design

- [ ] **Step 1: Remove old root-level runnable files after both snapshots exist**

Run:

```bash
rm -rf AGENTS.md decoders scripts tests output .pytest_cache
```

Expected: the parent now acts only as the variant selector and development-documentation location.

- [ ] **Step 2: Remove superseded development documents**

Remove these four old files with `apply_patch`:

```text
docs/superpowers/plans/2026-06-30-clean-two-run-baseline.md
docs/superpowers/plans/2026-06-30-ledger-guided-exploration.md
docs/superpowers/specs/2026-06-30-clean-two-run-baseline-design.md
docs/superpowers/specs/2026-06-30-ledger-guided-exploration-design.md
```

Expected: only the current packaging design and implementation plan remain under `docs/superpowers/`.

- [ ] **Step 3: Remove cache files created or copied during packaging**

Run:

```bash
find completed_qec_autoresearch ready_to_run_qec_autoresearch -type d -name __pycache__ -prune -exec rm -rf {} +
find completed_qec_autoresearch ready_to_run_qec_autoresearch -type d -name .pytest_cache -prune -exec rm -rf {} +
```

Expected: no cache directories remain.

### Task 6: Verify behavior, consistency, and publication safety

**Files:**
- Test: `completed_qec_autoresearch/tests/test_plot_ledger.py`
- Test: `ready_to_run_qec_autoresearch/tests/test_plot_ledger.py`
- Audit: all publishable files under `demo_qec_autoresearch/`

- [ ] **Step 1: Run both test suites independently**

Run from each child directory:

```bash
python -m pytest tests -q
```

Expected: both commands exit zero with all tests passing.

- [ ] **Step 2: Verify identical shared files**

Run:

```bash
cmp completed_qec_autoresearch/README.md ready_to_run_qec_autoresearch/README.md
cmp completed_qec_autoresearch/AGENTS.md ready_to_run_qec_autoresearch/AGENTS.md
diff -qr completed_qec_autoresearch/scripts ready_to_run_qec_autoresearch/scripts
diff -qr completed_qec_autoresearch/tests ready_to_run_qec_autoresearch/tests
cmp completed_qec_autoresearch/docs/QLDPC_DECODER_SUMMARY.md ready_to_run_qec_autoresearch/docs/QLDPC_DECODER_SUMMARY.md
```

Expected: every command exits zero and prints no differences.

- [ ] **Step 3: Verify ledger structure and CUDA-Q use**

Run:

```bash
python -c 'import collections, json, pathlib; rows=[json.loads(line) for line in pathlib.Path("completed_qec_autoresearch/output/ledger/experiments.jsonl").read_text().splitlines() if line.strip()]; by_round=collections.defaultdict(list); [by_round[row["round"]].append(row) for row in rows]; assert len(rows)==75; assert sorted(by_round)==list(range(1,16)); assert all(len(group)==5 for group in by_round.values()); assert all(row["used_cudaq_qec"] is True for row in rows); print("75 rows, 15 rounds, all CUDA-Q QEC")'
```

Expected: the command prints `75 rows, 15 rounds, all CUDA-Q QEC` and exits zero.

- [ ] **Step 4: Verify ready output is clean**

Run:

```bash
find ready_to_run_qec_autoresearch/output -mindepth 1 -maxdepth 2 -type f -printf '%P\n'
```

Expected: only `.gitkeep`.

- [ ] **Step 5: Run the publication audit**

Run:

```bash
rg -n --hidden -S '/home/[^/]+/|BEGIN [A-Z ]*PRIVATE KEY|authorization:[[:space:]]*(Bearer|Basic)|api[_-]?key[[:space:]]*[:=]|access[_-]?token[[:space:]]*[:=]|password[[:space:]]*[:=]' . -g '!docs/superpowers/**'
find . -type f \( -name '*.pyc' -o -name '*.json.bz2' \) -print
find . -type d \( -name __pycache__ -o -name .pytest_cache \) -print
find . -type f -size +1M -printf '%P %s bytes\n'
```

The development plan is excluded from the text scan because it necessarily
documents the forbidden patterns themselves. Inspect it separately for actual
credential values and user-specific paths.

Review every match manually because documentation may mention security terms
without containing a credential. Expected: no secrets, personal paths, cache
files, dataset archives, or unexpected large files.

- [ ] **Step 6: Verify Git publication behavior**

Run:

```bash
git check-ignore -v completed_qec_autoresearch/output/ledger/experiments.jsonl || true
git check-ignore -v completed_qec_autoresearch/output/plots/round_015.png || true
git check-ignore -v ready_to_run_qec_autoresearch/output/data/example.json.bz2
git check-ignore -v ready_to_run_qec_autoresearch/output/ledger/example.jsonl
git check-ignore -v ready_to_run_qec_autoresearch/output/plots/example.png
```

Expected: completed ledger and plots are not ignored; all three hypothetical ready/generated paths are ignored.

- [ ] **Step 7: Remove test caches and inspect final status**

Run:

```bash
find completed_qec_autoresearch ready_to_run_qec_autoresearch -type d -name __pycache__ -prune -exec rm -rf {} +
find completed_qec_autoresearch ready_to_run_qec_autoresearch -type d -name .pytest_cache -prune -exec rm -rf {} +
git status --short -- demo_qec_autoresearch
```

Expected: only intentional packaging files and removals appear; no cache, data, or secret-bearing files appear.

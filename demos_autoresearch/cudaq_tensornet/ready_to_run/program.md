# Independent researcher instructions

`AGENTS.md` is the authoritative protocol. This file is its short operational
checklist.

You own exactly one circuit: `nonlocal` or `controlled`.

Your objective is to minimize that circuit's valid CUDA-Q `observe` runtime.
The circuit, observable, reference value, evaluator, and timeout are fixed.
Round 1 is also fixed: copy `initial_experiment.py` to your assigned
`experiment.py` and evaluate it unchanged. It uses FP64 so every fresh study
has the same baseline. Your experimental decisions begin at round 2.

## What you may inspect

- This file and `README.md`.
- `benchmark.py`, but do not edit it.
- Only your own `research/<circuit>/experiment.py`.
- Only your own `research/<circuit>/results.tsv` and logs.

Do not inspect another researcher's directory or ledger when selecting changes.

## One research round

1. Read your ledger's latest result and its observation.
2. Form an informed reason for the next experiment.
3. Edit only your `experiment.py`.
4. Change only one key in `SETTINGS` per round.
5. Update `RATIONALE` to cite evidence from your own previous round.
6. Update `HYPOTHESIS` with a falsifiable prediction.
7. Run:

   ```bash
   python run_round.py <your-circuit>
   ```

The runner validates literals, locks the shared GPU, enforces a 30-second
timeout, checks the exact expectation value, appends the ledger, and refreshes
the combined plot and summaries. Your new rationale is also copied into the
previous row's `next_round_reasoning` column.

Lower runtime is better. A timeout is a valid negative result; do not retry an
obviously oversized setting. Small differences (roughly 5% or less) may be
timing or path-search noise and should be described cautiously.

## Allowed settings

- `precision`: `"fp32"` or `"fp64"`
- `controlled_rank`: integer 1–8
- `path_reuse`: `True` or `False`
- `hyper_samples`: integer 1–128
- `find_threads`: integer 1–64
- `find_limit`: `True` or `False`
- `deterministic`: `True` or `False`
- `scratch_percentage`: integer 5–95

These map directly to CUDA-Q's exact `tensornet` target and its documented
`CUDAQ_TENSORNET_*` environment controls.

You, the researcher agent, must run the fixed baseline and author every later
proposal. Do not use a script, loop, predetermined sweep, or optimizer to
choose or mutate settings.

Complete exactly 30 recorded rounds including the baseline. Afterward, write
`research/<circuit>/insights.md` using only your ledger. Separate strong effects
from weak/noisy evidence, explain failures, and state the best observed settings.
Also write two or three concise sentences with the main qualitative findings to
`research/<circuit>/figure_summary.txt` for display beneath your plot.

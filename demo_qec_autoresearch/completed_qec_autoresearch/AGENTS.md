# QEC QLDPC Autoresearch Agent Guide

This directory is a CUDA-Q QEC autoresearch demo. Treat this file as the only
control prompt. There is no separate `autorun.md` or `AUTORESEARCH.md`.

## Mission

Run a requested number of autoresearch iterations. In each iteration, test one
coherent decoder hypothesis, run the fixed evaluator once, inspect the
five-dataset worst-case result, and use the evidence in
`output/ledger/experiments.jsonl` to choose the next experiment. A coherent
experiment may include multiple coupled settings required to define a valid
candidate.

Default objective:

- minimize worst-case logical error rate across the five QLDPC datasets
- keep each dataset decode under 30 seconds
- judge progress by the ledger, not by intuition

## User Prompt Pattern

Expected user prompt:

```text
Read AGENTS.md and run autoresearch for N iterations.
```

If the user does not give `N`, ask for the number of iterations before starting.

## Key Files

| Path | Purpose |
|---|---|
| `AGENTS.md` | This control prompt and operating guide. |
| `README.md` | Human-facing overview and run instructions. |
| `decoders/qldpc_agent/decoder.py` | The only decoder implementation edited during research rounds. |
| `decoders/qldpc_agent/NOTES.md` | Round-by-round hypotheses, changes, outcomes, and lessons. |
| `docs/QLDPC_DECODER_SUMMARY.md` | Reference notes on CUDA-Q QEC decoder options and tuning knobs. |
| `scripts/run_round.py` | Fixed round runner. Evaluates the decoder on all default datasets. |
| `scripts/prepare_qldpc_datasets.py` | Downloads default datasets into `output/data/`. |
| `scripts/decode_and_score.py` | Fixed evaluator for one decoder/dataset pair. |
| `scripts/qldpc_data.py` | Dataset download and loading helpers. |
| `scripts/plot_ledger.py` | Fixed plotting helper for generated progress figures. |
| `output/` | Generated datasets, ledger, and plots; may contain prior rounds. |

## Default Benchmark

Use the five CUDA-QX 0.2.0 QLDPC release datasets. The scripts download them
into `output/data/` when missing:

- `osd_216_865_0.005.json.bz2`
- `osd_288_1585_0.005.json.bz2`
- `osd_360_2305_0.005.json.bz2`
- `osd_432_3025_0.005.json.bz2`
- `osd_504_3745_0.005.json.bz2`

## Exploration Strategy

Use the ledger to balance broad exploration with local refinement. Prefer
experiments that provide new information about meaningfully different decoder
behaviors before committing many rounds to fine-grained parameter tuning.

Parameter sweeps are appropriate while they produce meaningful improvements in
the worst-case objective, runtime headroom, or understanding of a promising
region. If several related tuning rounds produce little or no improvement,
treat that as evidence to try a meaningfully different decoder configuration
rather than continuing increasingly narrow adjustments.

When choosing the next experiment, consider whether an untested BP/OSD family
or configuration regime offers more information than another nearby parameter
value. This is guidance rather than a fixed schedule: use ledger results,
compatibility requirements, and runtime risk to decide when to explore and when
to refine.

Each iteration should test one coherent decoder hypothesis. A coherent
experiment may change multiple coupled settings when they jointly define a
valid candidate, for example selecting a BP method together with its required
gamma, sparsity, composition, or relay settings. Record every changed setting.
Keep unrelated ideas in separate rounds so results remain interpretable.

## Research Round Protocol

Before round 1, read:

1. `AGENTS.md`
2. `docs/QLDPC_DECODER_SUMMARY.md`
3. `output/ledger/experiments.jsonl`, if present
4. `decoders/qldpc_agent/NOTES.md`

For each iteration:

1. Review the latest ledger rows and notes.
2. Pick one coherent decoder experiment tied to evidence or a clear hypothesis.
   Continue local tuning while it yields useful progress; after several
   low-yield related experiments, prefer a meaningfully different candidate
   with higher information value.
3. Edit only `decoders/qldpc_agent/decoder.py`.
4. Update `decoders/qldpc_agent/NOTES.md` with the iteration number, hypothesis, exact change, command, result, and next idea.
5. Run one evaluator round:

```bash
python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30
```

6. Inspect the five new ledger rows and generated plot.
7. Continue until the requested number of iterations is complete.

The runner appends to `output/ledger/experiments.jsonl` and writes plots to
`output/plots/`.

## Plotting Rules

Generated plots must label the x axis `Autoresearch rounds`.

When any dataset in a round violates the configured decode time cap, exclude
that entire round from all plotted numeric series so the timeout penalty does
not appear as an outlier. Still mark the round's x-axis column with a visible
label such as `30s cap violated` so the omitted round remains clear in the
plot history. Keep the ledger rows unchanged; this rule only affects plotting.

## Edit Boundaries

During research rounds, agents may edit:

- `decoders/qldpc_agent/decoder.py`
- `decoders/qldpc_agent/NOTES.md`

Agents must not edit:

- files under `scripts/`
- files under `output/`
- files under `docs/`
- `AGENTS.md`
- `README.md`

## Decoder Rules

- Every candidate must use a real CUDA-Q QEC decoder call in the decode path.
- Decode one syndrome at a time.
- Do not use multi-syndrome decoder calls or decoder batch-size options; the evaluator rejects them.
- Do not use lookup-table decoders.
- Do not hardcode labels, logical observables, experiment ids, dataset paths, or exact answers.
- Do not launch subagents or agent-launching Python scripts for this demo.

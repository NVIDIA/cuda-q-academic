# Clean Two-Run QLDPC Baseline Design

## Goal

Remove all artifacts and notes from prior autoresearch runs, preserve the five
cached QLDPC input datasets, configure the requested decoder baseline, and run
that identical baseline twice so its per-run results can be compared.

## Reset Scope

- Preserve all files under `output/data/` and all `.gitkeep` placeholders.
- Delete the existing experiment ledger and generated round plots.
- Reset `decoders/qldpc_agent/NOTES.md` to an empty run-log template.
- Do not change scripts, documentation other than this design, or benchmark
  inputs.

## Baseline Configuration

Set `decoders/qldpc_agent/decoder.py` to the user-provided configuration:

```python
DECODER_NAME = "nv-qldpc-decoder"
MAX_ITERATIONS = 30
BP_METHOD = 1
USE_SPARSITY = True
ERROR_RATE = None
USE_OSD = True
OSD_METHOD = 1
OSD_ORDER = 0
N_THREADS = None
ITER_PER_CHECK = 5
CLIP_VALUE = None
REPEATABLE = None
SCALE_FACTOR = 0.75
PROC_FLOAT = "fp64"
COMPOSITION = None
GAMMA0 = None
GAMMA_DIST = None
EXPLICIT_GAMMAS = None
SRELAY_CONFIG = None
BP_SEED = None
```

## Execution and Results

Run the standard evaluator twice, as two separate rounds:

```bash
/home/mawolf/cudaq-workspace/.venv/bin/python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30
```

After each execution, record its five per-dataset logical error rates, decode
times, statuses, worst-case logical error rate, and whether every dataset met
the 30-second cap. The completed state contains ten ledger rows and two plots.

## Verification

- Confirm the five cached dataset files are unchanged and still present.
- Confirm prior ledger rows, plots, and notes are absent before the first run.
- Confirm the decoder constants exactly match the requested values.
- Confirm round 1 and round 2 each contribute exactly five ledger rows.
- Report both runs separately and note any repeatability or timing differences.

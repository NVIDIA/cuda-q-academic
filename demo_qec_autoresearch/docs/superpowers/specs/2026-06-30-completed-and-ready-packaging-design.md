# Completed and Ready QEC Autoresearch Packaging Design

## Goal

Repackage the existing QEC autoresearch exercise as two independent runnable
examples beneath `demo_qec_autoresearch/`:

- `completed_qec_autoresearch/` demonstrates the completed 15-round research
  process.
- `ready_to_run_qec_autoresearch/` provides a clean starting point for a new
  autoresearch run.

The parent directory will contain a short README that explains which variant
to use. The two variants must remain independently runnable and must not rely
on symlinks or files outside their own directories.

## Target Layout

```text
demo_qec_autoresearch/
├── README.md
├── .gitignore
├── completed_qec_autoresearch/
│   ├── README.md
│   ├── AGENTS.md
│   ├── decoders/
│   ├── docs/
│   ├── scripts/
│   ├── tests/
│   └── output/
│       ├── ledger/experiments.jsonl
│       └── plots/round_001.png ... round_015.png
└── ready_to_run_qec_autoresearch/
    ├── README.md
    ├── AGENTS.md
    ├── decoders/
    ├── docs/
    ├── scripts/
    ├── tests/
    └── output/.gitkeep
```

Development specifications may remain under the parent `docs/superpowers/`
directory, but they will not be copied into either runnable variant.

## Shared Runnable Content

Each variant will contain its own copy of the fixed evaluator scripts, tests,
and `docs/QLDPC_DECODER_SUMMARY.md`. The child `README.md` and `AGENTS.md`
files must be byte-identical across both variants.

The shared README will be state-neutral: it will explain that `output/` may be
empty for a fresh run or prepopulated in an example run. Commands will use
portable `python` invocations rather than a user-specific virtual-environment
path.

The shared `AGENTS.md` will retain the ledger-guided exploration protocol and
edit boundaries. It will describe `output/` as generated state that may already
contain prior rounds instead of claiming that it always starts empty. Its
evaluator command will also use `python`.

## Completed Variant

The completed variant will preserve:

- the best round-15 decoder;
- all 15 research-note entries;
- the 75-row five-dataset ledger;
- plots `round_001.png` through `round_015.png`;
- the fixed scripts, tests, and decoder reference documentation.

The five downloaded CUDA-QX dataset archives will be excluded. The existing
download helper can retrieve them when another evaluator round is requested.

Machine-specific paths in notes and ledger records will be normalized:

- commands become `python scripts/run_round.py ...`;
- ledger `decoder_path` values become the repository-relative
  `decoders/qldpc_agent/decoder.py`.

Result values, timings, round status, hashes, and timestamps remain unchanged.

## Ready-to-Run Variant

The ready variant will contain:

- `decoder.py` restored to the original 30-iteration min-sum configuration
  with FP32, scale factor `0.75`, and OSD-0;
- a clean `NOTES.md` template with no experiment entries;
- an `output/` directory containing only `.gitkeep`;
- the same fixed scripts, tests, README, AGENTS guide, and decoder reference
  documentation as the completed variant.

The separate `decoder_initial_settings.py` file will not be included because
the ready variant's `decoder.py` itself is the canonical initial decoder.

## Parent Documentation and Ignore Rules

The parent README will briefly explain that the completed variant is for
studying an evidence-backed 15-round run and that the ready variant is for
starting a new run. It will include the `cd` and Codex prompt needed for each.

Parent ignore rules will exclude:

- Python and pytest caches everywhere;
- downloaded `output/data/` directories in both variants;
- future generated ledger and plot files in the ready variant.

The completed ledger and plots must remain visible to Git so they can be
published as the example result.

## Cleanup and Publication Audit

The packaged variants will exclude:

- `__pycache__/` directories and `.pyc` files;
- `.pytest_cache/` directories;
- downloaded dataset archives;
- the redundant `decoder_initial_settings.py`;
- old implementation plans and design specifications from the runnable
  copies.

Before completion, scan all publishable filenames and text for credential-like
content, private keys, access tokens, passwords, authorization headers,
user-specific absolute paths, and unexpectedly large files. Any machine path
found in the preserved run artifacts must be normalized without altering the
experimental measurements.

Downloaded third-party datasets are not redistributed. Source links and
download code remain because they are necessary to reproduce the benchmark.

## Verification

Completion requires fresh evidence that:

1. Both child READMEs are byte-identical.
2. Both child AGENTS files are byte-identical.
3. Fixed scripts, tests, and decoder reference documentation match across both
   variants.
4. Both test suites pass.
5. The completed ledger contains exactly 75 rows grouped as five rows for each
   round 1 through 15, with all rows reporting CUDA-Q QEC use.
6. The completed copy has exactly 15 plots and 15 note entries.
7. The ready copy has no datasets, ledger, plots, or note entries.
8. The ready decoder exactly matches the preserved initial settings.
9. Neither copy contains cache files, downloaded datasets, redundant baseline
   decoder files, credentials, secrets, or user-specific absolute paths.
10. Git ignore checks show that completed result artifacts are publishable and
    ready-run generated artifacts are ignored.


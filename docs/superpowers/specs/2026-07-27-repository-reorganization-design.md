# Workshop Repository Reorganization Design

## Goal

Reorganize the workshop so autoresearch demos are grouped by topic, retain only
the calibration exercise from the remote branch, and add the supplied Ising
calibration notebook as an optional activity.

## Final Layout

```text
demos_autoresearch/
├── README.md
├── cudaq_qec_decoder/
│   ├── README.md
│   ├── completed/
│   └── ready_to_run/
└── cudaq_tensornet/
    ├── README.md
    ├── completed/
    └── ready_to_run/

01_exercise_ising_calibration/
├── README.md
├── calibration_example.png
└── optional_intro_ising_calibration.ipynb
```

The existing QEC completed and ready-to-run projects will move without changing
their substantive contents. The tensor-network completed and ready-to-run
projects will be copied from:

- `/home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_completed`
- `/home/mawolf/vibeshop-cudaq/cudaq_tensornet_autoresearch_ready_to_run`

Transient local files such as `__pycache__`, `.pytest_cache`, `.gpu.lock`, and
the local Matplotlib cache directory will not be copied.

Machine-specific absolute paths in the completed TensorNet command logs will
be rewritten as portable relative commands. Experimental settings, timings,
results, rationales, and conclusions will remain unchanged.

## Documentation

`demos_autoresearch/README.md` will explain the two demo topics and direct
participants to choose either a completed example for inspection or a
ready-to-run example for a new autoresearch session.

Each topic folder will have a short README describing its objective and its two
variants. Existing variant-specific README and `AGENTS.md` instructions will
remain authoritative inside each runnable project.

The calibration README will retain the remote exercise instructions and add an
“Optional notebook exercise” section linking to
`optional_intro_ising_calibration.ipynb`.

## Calibration Source and Removal

The final `01_exercise_ising_calibration` folder will be based only on the
remote-backed `exercise_calibration` directory.

The extra local `exercise_ising_calibration` directory will be removed in full,
including its tracked T1 exercise, design documents, and untracked generated
plot images. None of those local-only materials will be folded into the final
exercise.

The notebook will be downloaded from:

`https://github.com/Squirtle007/cudaq-agentic-coding/blob/main/_intro_Ising_Calibration.ipynb`

and saved under the explicitly optional filename
`optional_intro_ising_calibration.ipynb`.

## Validation

Validation will cover:

1. The expected directory tree and absence of the superseded top-level folders.
2. Valid JSON structure for the downloaded notebook.
3. No copied transient cache or lock files.
4. Python syntax compilation for copied demo scripts.
5. Available lightweight tests for both autoresearch topics.
6. README links and referenced local paths.

Full 30-round tensor-network or QEC autoresearch studies are outside this
reorganization because they are long-running GPU research workflows. The
completed artifacts will be preserved, while lightweight harness checks will
establish that the ready-to-run folders are internally coherent.

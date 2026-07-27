# Numbered Exercises and Wiki Demo Design

## Goal

Finish the workshop's top-level organization by naming the research wiki as a
demo, adding a numbered CUDA-Q kernels exercise from the existing local source,
and renaming the QAOA/ADAPT-QAOA exercise to its numbered workshop slot.

## Final Layout

```text
demos_wiki_llm/
├── AGENTS.md
├── README.md
├── documents/
├── prompts/
├── skills/
└── wiki/

02_exercise_cudaq_kernels/
├── README.md
├── mps_observe.py
├── tensor_network_observe.py
├── run_ghz_template.py
├── run_ghz_solution.py
├── template_ghz_kernel.py
└── solution_ghz_kernel.py

03_04_exercise_qaoa_and_adapt/
├── README.md
├── adapt_qaoa.py
├── parallel_adapt_qaoa.py
├── run_qedc_input.py
├── assets/
├── maxcut_instances/
├── tests/
└── results/
```

The numbered QAOA folder will retain the existing exercise contents. Its
ignored local `results/` directory will move with the exercise and remain
ignored rather than becoming committed workshop source.

## Wiki Demo Rename

`exercise_wiki_llm` will move to `demos_wiki_llm`. The two participant prompt
examples in its README that currently say `Work in exercise_wiki_llm` will be
updated to the new path. The local agent guide, skills, prompts, document list,
and blank wiki will otherwise remain unchanged.

## CUDA-Q Kernels Exercise

The six Python files from `~/vibeshop-cudaq/02_intro_to_cudaq` will be copied
without modifying their exercise content:

- `run_ghz_template.py` and `run_ghz_solution.py`
- `template_ghz_kernel.py` and `solution_ghz_kernel.py`
- `mps_observe.py`
- `tensor_network_observe.py`

The two template files are intentionally incomplete and contain syntax-level
placeholders for participants to fill in. Validation will not treat those
placeholders as defects.

A new README will describe the template/solution pairs, the complete simulator
examples, and the requirement to use a CUDA-Q Python environment. It will
clearly label the template files as incomplete workshop starting points.

## QAOA Exercise Rename and Imports

`exercise_adapt_qaoa` will move to
`03_04_exercise_qaoa_and_adapt`.

Because a Python module name cannot begin with a digit, code and tests will no
longer import through the top-level exercise directory name. They will use
folder-local module imports:

- `adapt_qaoa.py` and `parallel_adapt_qaoa.py` will import
  `run_qedc_input` locally.
- `run_qedc_input.py` will import `adapt_qaoa` locally where needed.
- Tests will import `adapt_qaoa` and `run_qedc_input` from the exercise
  directory and run subprocess commands relative to that directory.

The exercise is intended to be entered before running scripts, tests, or
Codex, consistent with the root workshop guidance. README commands, Python
usage examples, subprocess tests, and packaging instructions will use the new
folder name or paths relative to the active exercise folder.

Ignored generated results will be preserved. Generated `__pycache__` and
`.pytest_cache` directories will be removed because they are reproducible
machine-local artifacts.

## QEC Wrapper Cleanup

The earlier QEC reorganization left a tracked `.gitignore` in
`demo_qec_autoresearch/`. It will move to `demos_autoresearch/.gitignore`, and
its ready-to-run QEC output paths will be updated for the new
`cudaq_qec_decoder/ready_to_run` hierarchy.

After that move, `demo_qec_autoresearch` must no longer exist.

## Validation

Validation will cover:

1. The requested top-level directory names exist and the three superseded
   names do not.
2. The six copied kernel files match their source files byte-for-byte.
3. The four complete kernel examples parse as Python; the two intentionally
   incomplete templates are present and documented.
4. The QAOA tests pass when run from the renamed exercise directory.
5. QAOA source, tests, and documentation contain no references to the old
   `exercise_adapt_qaoa` path.
6. Wiki documentation contains no references to `exercise_wiki_llm`.
7. Local Markdown links resolve.
8. No generated cache directories are left in the renamed exercises.
9. The QEC ignore rules point to the reorganized hierarchy.
10. `git diff --check` passes and the final Git status contains only intended
    changes.

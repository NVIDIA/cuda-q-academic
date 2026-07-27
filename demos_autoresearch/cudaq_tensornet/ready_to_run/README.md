# CUDA-Q TensorNet autoresearch demo

This project demonstrates agent-directed performance research with CUDA-Q's
exact `tensornet` simulator.

Two independent researcher agents optimize two fixed quantum circuits:

- `nonlocal`: a 30-qubit circuit with irregular long-range gates;
- `controlled`: a 21-qubit circuit with repeated controlled rotations.

Every study starts from the same FP64 round-one template. After that baseline,
the agents may tune only CUDA-Q TensorNet settings. They cannot change the
circuits, answers, timer, or scoring rules. Each agent changes one setting,
records its reasoning, runs one evaluation, studies the result, and then
decides what to try next.

## Key files

| File | Purpose |
| --- | --- |
| `STUDY_STATE.md` | Says whether this copy is completed or ready to run. |
| `AGENTS.md` | Authoritative rules for the coordinator and researcher agents. |
| `initial_experiment.py` | Immutable FP64 settings and reasoning for round 1. |
| `benchmark.py` | Fixed circuits and observables. Researchers must not edit it. |
| `reference.json` | Fixed expected answers and benchmark identity. |
| `evaluate.py` | Runs and checks one proposal. |
| `run_round.py` | Runs one timed round, enforces the 30-second limit, and records the result. |
| `research/nonlocal/experiment.py` | The only file the nonlocal researcher edits. |
| `research/controlled/experiment.py` | The only file the controlled researcher edits. |
| `research/*/results.tsv` | Each researcher's append-only experimental ledger. |
| `research/*/insights.md` | Each researcher's final interpretation of its own results. |
| `research/*/figure_summary.txt` | Short agent-authored findings shown under that circuit's plot. |
| `results.png` | Each circuit's plot, best-settings table, and research notes. |
| `summary.md` | Combined written results. |

`plot_results.py` and `summarize_results.py` regenerate the final reports.
`program.md` is a short description of the research loop.

## How to run it with agents

Start your coding agent in this directory, or give it the path to this
directory. Then use this prompt:

```text
Read AGENTS.md completely and follow it as the authoritative protocol.
Do not use Superpowers skills or workflows for this study.

Run the ready-to-run 30-round CUDA-Q TensorNet autoresearch study for both the
nonlocal and controlled circuits. Confirm that no prior ledgers or logs exist.
Do not delete or modify anything in a separate completed-results folder.
Do not modify initial_experiment.py, benchmark.py, reference.json, evaluate.py,
run_round.py, the circuits, or the scoring rules.

Act as the coordinator and assign one independent researcher agent to each
circuit. The coordinator must not choose any settings. Each researcher must
copy and run the fixed initial_experiment.py contents as round 1. It must then
choose every later proposal, read only its own research history, edit only its
own experiment.py, and change at most one setting per round. Before every
post-baseline evaluation, the researcher must write an informed
RATIONALE and falsifiable HYPOTHESIS. It must run one round, inspect the
recorded result, and only then decide the next experiment. Do not use a
scripted parameter sweep or a script that chooses settings.

The researchers may reason in parallel, but all GPU evaluations must use
run_round.py so its lock serializes them. Complete 30 recorded rounds for
each circuit, restore each experiment.py to its best valid settings, write
each researcher's insights.md and figure_summary.txt from only its own ledger,
and then have the coordinator generate results.png and summary.md and verify
the artifacts.
```

That prompt intentionally fixes the shared FP64 baseline and delegates every
post-baseline experimental decision to the researcher agents. The Python files
provide fixed measurement and record-keeping infrastructure; they do not
choose the next TensorNet settings.

## What one researcher runs

After editing its `experiment.py`, a researcher evaluates exactly one proposal:

```bash
python run_round.py nonlocal
```

or:

```bash
python run_round.py controlled
```

Use the CUDA-Q Python environment available on your machine if it is installed
at a different path. A CUDA-capable NVIDIA GPU and a CUDA-Q installation with
the TensorNet backend are required.

## Result interpretation

Every round checks the measured expectation against `reference.json`. A valid
new runtime minimum is labeled `keep`; a slower result is labeled `discard`.
This label is mechanical and does not decide the next experiment.

GPU timing has normal run-to-run noise. An agent should therefore repeat or
reverse important tests and treat small timing changes cautiously. Evaluations
that exceed 30 seconds are recorded as timeouts and still count as rounds.

## References

- [CUDA-Q tensor-network simulators](https://nvidia.github.io/cuda-quantum/latest/using/backends/sims/tnsims.html)
- [Karpathy's autoresearch loop](https://github.com/karpathy/autoresearch)

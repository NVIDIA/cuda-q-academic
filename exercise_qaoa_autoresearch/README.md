# AutoResearch QAOA Exercise

This exercise uses an AutoResearch-style agent loop to explore a small MaxCut
circuit-design problem in CUDA-Q.

## Specific Goal

Use an agent to search for a custom QAOA-style ansatz that keeps solution
quality close to a fixed baseline while using a simpler circuit.

## Problem Setup

The exercise is intentionally small and measurable. It contains:

- a fixed QED-C MaxCut instance,
- a fixed QAOA baseline,
- a small editable candidate circuit,
- a harness that evaluates solution quality, gate cost, and experiment history.

Participants should scan the code to discover the exact instance, baseline,
scoring rules, and edit boundaries before asking the agent to run the loop.

## Learning Outcomes

By the end of the exercise, participants should be able to explain:

- how local instructions constrain an AI coding agent,
- which files define the experiment and scoring rules,
- where the agent is allowed to change code,
- how each experiment round is evaluated and recorded,
- how approximation ratio and gate score trade off in this setup,
- how the final report identifies the best custom ansatz.

## Step 1: Read the Agent Instructions

Start with `AGENTS.md`.

This file tells the agent what it must optimize, which rules it must follow,
and which files it may edit during experiment rounds. Read it before prompting
the agent so you understand the local context the agent is expected to ingest.

Focus on:

- the pass threshold,
- the gate-score formula,
- the one-logical-change-per-round rule,
- the files the agent may edit,
- the CUDA-Q gates allowed in the candidate circuit.

## Step 2: Inspect the Experiment Files

Before running the loop, examine the files that define the exercise:

| Path | Purpose |
| --- | --- |
| `program.md` | Research objective, pass threshold, gate-score formula, and final report requirements. |
| `candidate_kernel.py` | Editable CUDA-Q ansatz surface. |
| `harness.py` | Fixed evaluator, baseline circuit, optimization loop, gate counting, ledger writing, and report generation. |
| `hamiltonian.py` | MaxCut instance loading and scoring helpers. |
| `instances/` | Real QED-C MaxCut input and solution used for the run. |
| `ledger.md` | Experiment log where baseline and candidate evaluations are recorded. |
| `reports/` | Output directory for the final plot and Markdown comparison. |

The important boundary is that `candidate_kernel.py` is the circuit search
surface. The other files define the exercise and should be treated as fixed
infrastructure during experiment rounds.

## Step 3: Run the Experiment Loop

From this directory, ask the agent to read the local instructions and run a
fixed number of experiment rounds.

Example prompt:

```text
Read AGENTS.md and run the AutoResearch experiment for 30 iterations.
```

The agent should evaluate the fixed baseline, propose one logical circuit
change per round, run the harness, and record the outcome.

## Step 4: Review the Outputs

Generate the final report:

```bash
python3 harness.py report
```

The report command produces:

- `reports/ratio_vs_gate_score.png`: a scatter plot of approximation ratio
  against gate score, with passing points in green and failing points in red.
- `reports/ansatz_comparison.md`: a compact Markdown comparison of the
  baseline, the best candidate, and passing gate-score levels.

Use these outputs to identify which circuit changes produced the largest
gate-score savings while staying inside the 95% baseline approximation-ratio
threshold.

## Step 5: Discuss the Result

After reviewing the ledger and reports, discuss:

- Which custom ansatz had the best passing gate score?
- How much gate-score reduction did it achieve relative to the baseline?
- Which circuit patterns appeared helpful?
- Which changes failed the approximation-ratio threshold?
- What additional constraints would make the experiment more realistic?

## Step 6: Extensions

If time allows, try one of the following extensions:

- Modify the scoring metric to better reflect hardware cost.
- Add a stricter or looser approximation-ratio threshold.
- Generalize the harness to a larger QED-C MaxCut instance.
- Improve the final report with additional plots or tables.
- Add stronger agent instructions for avoiding unproductive circuit changes.

## Resources And Provenance

This exercise is based on Andrej Karpathy's
[`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) example: a
small, measurable research loop where an agent repeatedly edits one candidate
file, evaluates the result, and records what happened.

The MaxCut instance in `instances/` comes from QED-C's
[`SRI-International/QC-App-Oriented-Benchmarks`](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
quantum benchmark repository.

Additional resources:

- [NVIDIA CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/)
- [CUDA-Q Max-Cut with QAOA example](https://nvidia.github.io/cuda-quantum/latest/applications/python/qaoa.html)
- [QED-C application-oriented benchmark repository](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
- [Karpathy AutoResearch example](https://github.com/karpathy/autoresearch)

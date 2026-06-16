# AutoResearch QAOA Exercise

Goal: use an AutoResearch-inspired setup to find a custom 6-parameter ansatz
with a simpler circuit that stays within the allowed approximation-ratio band of
traditional QAOA.

## Provenance and Requirements

This exercise is based on Andrej Karpathy's
[`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) example: a
small, measurable research loop where an agent repeatedly edits one candidate
file, evaluates the result, and records what happened.

The MaxCut instance in `instances/` comes from QED-C's
[`SRI-International/QC-App-Oriented-Benchmarks`](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
quantum benchmark repository.

## Exercise Goal

By the end of the exercise, participants should be able to explain:

- what instructions the agent receives before starting,
- which files define the experiment and scoring rules,
- where the agent is allowed to change code,
- how each experiment round is recorded,
- how the agent reasoned about and made changes.

## Step 1: Read the Agent Instructions

Start with `AGENTS.md`.

This file tells the agent what it must optimize, what rules it must follow, and
which files it may edit during experiment rounds. Read it before prompting the
agent so you know what local context the agent is expected to ingest.

Key question:

```text
What constraints does AGENTS.md place on the agent before it does any work?
```

## Step 2: Inspect the Experiment Files

Before running the loop, examine the files that define the exercise:

- `program.md`: the research objective, pass threshold, gate-score formula, and
  final report requirements.
- `candidate_kernel.py`: the editable CUDA-Q ansatz surface.
- `harness.py`: the fixed evaluator, baseline circuit, optimization loop, gate
  counting, ledger writing, and report generation.
- `hamiltonian.py`: MaxCut instance loading and scoring helpers.
- `instances/`: the real QED-C MaxCut input and solution used for the run.
- `ledger.md`: the experiment log where each baseline and candidate evaluation
  is recorded.
- `reports/`: the output directory for the final plot and Markdown comparison.

Key question:

```text
Which files define the rules of the experiment, which file contains the circuit
the agent is supposed to improve, and which files should the agent edit or not?
```

## Step 3: Prompt the Agent to Run the Experiment

From this directory, ask the agent to read the local instructions and run a fixed
number of iterations.

Example prompt:

```text
Read AGENTS.md and run the AutoResearch experiment for 30 iterations.
```

## Step 4: Review the Outputs

The report command produces:

- `reports/ratio_vs_gate_score.png`: a scatter plot of approximation ratio
  against gate score, with passing points in green and failing points in red.
- `reports/ansatz_comparison.md`: a compact Markdown summary comparing the
  baseline, the best candidate, and the passing gate-score levels.

The current harness does not generate an HTML report. To visualize the data,
open the PNG plot and read the Markdown comparison report.

Key question:

```text
Looking at ledger.md, reports/ratio_vs_gate_score.png, and
reports/ansatz_comparison.md, which circuit changes produced the largest
gate-score savings while staying inside the 95% baseline approximation-ratio
threshold, and what pattern do those successful changes suggest?
```

## Step 5: Extensions

Consider the following questions and use them as motivation to optionally extend
this work:

- How could you modify this experiment with a better scoring metric or goal?
- Are we missing any constraints or rules for the agent that would improve this?
- Try generalizing this to a larger problem or a completely new problem setup.

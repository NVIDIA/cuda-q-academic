# Agent-run autoresearch protocol

This file is authoritative for agents working anywhere in this project.

The purpose of this demo is to test agent-directed research. Round 1 is a fixed
FP64 baseline from `initial_experiment.py`. Starting with round 2, an agent must
choose each experiment, edit the proposal, run the fixed evaluation machinery,
interpret the result, and then choose the next experiment. No script may select
later settings, generate a parameter sweep, or decide the next research
question.

## Roles

Assign one independent researcher agent to each fixed circuit:

- `nonlocal` owns `research/nonlocal/`.
- `controlled` owns `research/controlled/`.

The coordinator may scaffold the project, assign agents, mechanically copy
`initial_experiment.py` into both proposal files, and verify final artifacts.
It must not choose settings for either researcher. The baseline settings are
fixed by the template rather than chosen by the coordinator or researchers.
Each researcher runs its own round 1 from that template.

Researchers may reason concurrently, but GPU evaluations must pass through the
file lock in `run_round.py` and therefore execute one at a time.

## Researcher isolation

A researcher may inspect:

- this `AGENTS.md`;
- `program.md` and `README.md`;
- the fixed `initial_experiment.py` baseline template;
- the fixed portion of `benchmark.py` defining its assigned circuit;
- its own `research/<circuit>/experiment.py`;
- its own `research/<circuit>/results.tsv` and logs.

A researcher must not inspect the other circuit's research directory, ledger,
settings, logs, insights, plot, or summary while choosing experiments. It must
not use conclusions from an earlier run unless the user explicitly asks for a
continuation rather than a fresh study.

## Agent decision loop

For round 1, copy `initial_experiment.py` to the assigned
`research/<circuit>/experiment.py` without altering any literal and run it once.
`run_round.py` enforces this when the ledger is empty.

For rounds 2–30, the researcher agent must perform these steps itself:

1. Read only its own latest ledger row and, when useful, its own log.
2. Form an informed explanation of what the result suggests.
3. Choose exactly one CUDA-Q tensornet setting to test next.
4. Edit only its own `research/<circuit>/experiment.py`.
5. Change no more than one `SETTINGS` key relative to the immediately
   preceding proposal, including the move away from the fixed baseline.
6. Before evaluation, write a concrete `RATIONALE` grounded in its own prior
   evidence and a falsifiable `HYPOTHESIS`.
7. Invoke one fixed evaluation:

   ```bash
   python run_round.py <nonlocal-or-controlled>
   ```

8. Wait for that evaluation to finish and inspect the appended result before
   choosing the following round.

The agent must repeat this loop one round at a time. It may not precompute a
30-row sweep, write a driver that mutates settings, have a script select the
next configuration, or launch several proposals without observing the
intervening results.

## What the scripts are allowed to decide

The scripts are fixed, mechanical experiment infrastructure:

- `benchmark.py` defines the immutable circuits and observables.
- `initial_experiment.py` defines the immutable FP64 round-one settings.
- `reference.json` pins the benchmark hash and expected answers.
- `evaluate.py` validates literal settings, configures CUDA-Q, runs one circuit,
  times `cudaq.observe`, and checks correctness.
- `run_round.py` serializes GPU access, enforces the timeout, appends the exact
  settings and agent-authored reasoning to the ledger, and mechanically marks a
  valid new minimum as `keep` or a slower result as `discard`.
- `plot_results.py` and `summarize_results.py` report recorded data.

The `keep`/`discard`, correctness, timeout, and plotting decisions are
deliberately mechanical. They do not select the next setting. Only the
researcher agent makes that decision.

During a study, researchers must not edit any of those fixed files. They also
must not change a circuit, observable, expected answer, timer, timeout, scoring
rule, or reporting logic.

## Allowed proposal settings

Only the following literals in the assigned `experiment.py` may change:

- `precision`: `"fp32"` or `"fp64"`
- `controlled_rank`: integer 1–8
- `path_reuse`: `True` or `False`
- `hyper_samples`: integer 1–128
- `find_threads`: integer 1–64
- `find_limit`: `True` or `False`
- `deterministic`: `True` or `False`
- `scratch_percentage`: integer 5–95

An agent should prefer tests that distinguish competing explanations. It should
reverse or repeat important changes, test interactions after strong structural
effects, and treat differences of roughly 5% or less as possibly noisy.
Timeouts and failed hypotheses are legitimate results and count as rounds.

## Fixed and deterministic aspects

The circuit data, pairing seed, circuit arguments, observable, expectation
reference, benchmark hash, evaluator, timeout, and ledger schema are fixed for
every round. `evaluate.py` also calls `cudaq.set_random_seed(20260723)`.

This does not promise bitwise-identical timing. CUDA-Q contraction-path search
may vary when the proposal has `deterministic=False`, and GPU timing naturally
has noise. `deterministic` is itself a research setting and must not be forced
outside `experiment.py`. Here, "fixed evaluator" means every proposal runs
through the same guarded files—not that all path searches or timings are
identical.

## Recording and completion

- A normal study contains exactly 30 ledger rows per researcher, including the
  fixed FP64 baseline.
- Every non-final ledger row must contain the complete settings, measured
  result, `reasoning_for_change`, `hypothesis`, observation, and reasoning
  selected for the following round. The final row may state that the study is
  complete and no next round is planned.
- The agent must continue after a timeout unless all requested rounds are
  complete.
- At completion, the researcher writes
  `research/<circuit>/insights.md` using only its own ledger. It must separate
  strong findings, interaction-dependent findings, negative results, and
  weak/noisy evidence.
- The researcher also writes `research/<circuit>/figure_summary.txt` using only
  its own ledger. It must contain two or three concise sentences summarizing
  the most important qualitative findings for display beneath that circuit's
  plot.
- The researcher restores its `experiment.py` to the best valid observed
  settings without recording an extra research round.
- Only after both researchers finish may the coordinator compare ledgers,
  regenerate combined reports, and verify that the restored proposals match
  each ledger's best row.

# Fifteen-layer QAOA two-agent, observe-budgeted autoresearch protocol

This file is authoritative for every agent working in this project. The study
objective is:

> Find the lowest circuit energy observed in any valid round within a hard
> budget of 300 counted `cudaq.observe` calls, using optimizer-code changes
> only.

The single case is `qaoa_depth15`. It uses the weighted six-node `small` graph
from `../03_04_qaoa_and_adapt_qaoa/workshop_graphs.py`, with fifteen QAOA
layers and 30 parameters ordered as fifteen `gamma` values followed by fifteen
`beta` values.

## What is fixed

The following are immutable throughout all 20 rounds:

- the six-node weighted graph and Max-Cut Hamiltonian;
- the QAOA circuit structure and fifteen-layer depth;
- the case's seeded 30-parameter initial vector;
- the accepted-iterate convergence rule and tolerances;
- the hard 300-observe scientific budget;
- the secondary 120-second evaluator guard and 135-second subprocess guard;
- NVIDIA FP64 simulator target and random seed;
- energy oracle, trace schema, scoring, and fixed-file manifest.

Every round starts from a fresh copy of exactly the same initial parameter
vector. The harness evaluates that vector as counted call 1 before optimizer
code runs and passes its energy as `initial_energy`.

The researcher may edit only:

```text
research/qaoa_depth15/optimizer.py
```

The complete optimizer implementation may change between rounds. No other file
may be edited during research.

## Objective, observe cap, and status

One invocation of `objective(parameter_vector)` is one counted
`cudaq.observe` call. The evaluator records every completed call, its elapsed
time, energy, parameters, and running lowest energy.

The scientific budget is exactly 300 counted calls, including the fixed
initial circuit evaluation as call 1. The evaluator records and scores call
300, then immediately stops the round with `call_cap`; call 301 never begins.
The lowest energy from the 300 completed observations is preserved. A
120-second evaluator timer remains only as a secondary safety guard for
unexpectedly slow execution.

Every valid round is scored by:

```text
lowest energy observed across all counted objective calls in that round
```

Lower is better. Energies within `1e-6` of the raw lowest energy are treated as
a close tie. Among close contenders, prefer a round that converged or returned
before exhausting its observe budget, then lower evaluator elapsed time, then
fewer observe calls, then the earlier round. A materially lower energy always
wins regardless of convergence.

Possible normal outcomes are:

- `converged`: the fixed accepted-energy rule fired before the observe cap;
- `call_cap`: all 300 counted observes completed before convergence;
- `not_converged`: optimizer code returned before convergence;
- `time_cap`: the secondary 120-second safety guard fired first.

All four outcomes remain valid energy results when at least one finite
observation was recorded. A time-capped or otherwise non-converged round is
not a failed experiment. Evaluator errors, protocol violations, crashes, and
outer subprocess timeouts are invalid.

## Accepted-iterate convergence diagnostic

The optimizer must call `accepted(parameter_vector)` after every accepted
optimizer iteration. The accepted point must exactly match an already-counted
objective evaluation, and at least one new objective call must have occurred
since the preceding accepted report. The callback performs no circuit call.

Convergence is diagnostic but must be reported honestly:

```text
absolute accepted-iterate energy change <= 0.000001
patience = 3 consecutive accepted iterations
minimum accepted optimizer iterations = 5
```

The fixed initial point is accepted iteration 0. When convergence is reached,
the harness stops the round immediately. The scored energy is still the lowest
energy from any counted call in the round, including gradient, line-search,
stochastic, and rejected probes.

An optimizer that does not converge or return early may use all 300 observes
and is then stopped and scored normally. Optimizers must report accepted
iterates whenever their own algorithm accepts a point.

## What the researcher may inspect

Before round 1, the coordinator may inspect:

- this file, `README.md`, and `program.md`;
- `initial_optimizer.py`;
- `research/qaoa_depth15/optimizer.py`;
- the workshop's `qaoa_maxcut.py` and `workshop_graphs.py`.

After each recorded round, benchmark-result evidence for the next proposal is
limited to:

```text
research/qaoa_depth15/results.tsv
```

For implementation context, the active research role may also inspect:

- `initial_optimizer.py`;
- the current optimizer source;
- the source snapshot from the best-energy valid recorded round;
- general optimizer documentation or ideas that do not contain results from
  this benchmark.

Do not inspect trace JSON, round logs, per-call parameter or energy histories,
the benchmark implementation, reference data, evaluator internals, verifier,
tests, calibration material, an earlier completed study, or external results
for this benchmark while choosing proposals.

## Alternating research roles

The primary agent is the sole coordinator and evaluator. It uses exactly two
persistent subagents as proposal authors:

- **Explorer** owns even-numbered rounds 2, 4, ..., 20. It prioritizes
  materially new optimizer families, search geometries, schedules, gradient
  estimators, restarts, time allocation, and hybrid mechanisms.
- **Improver** owns odd-numbered rounds 3, 5, ..., 19. It starts from the
  best-energy valid recorded optimizer and prioritizes controlled tuning,
  reversals, replications, removal of wasted work, and better use of the
  300-observe budget.

Only the role that owns the next round may make a proposal. Do not request
competing proposals, merge proposals, or allow a subagent to evaluate. Each
proposal must:

- identify the round and role;
- cite specific ledger rows;
- state the current lowest observed energy and winning round;
- state whether that winner converged or reached the time cap;
- describe exactly one proposed optimizer;
- explain the material change;
- provide a concrete `RATIONALE`;
- give a falsifiable `HYPOTHESIS` about lowest energy, convergence, calls, or
  observe-cap behavior;
- identify an expected failure mode.

## One adaptive round at a time

Round 1 is fixed. The existing optimizer is an exact copy of
`initial_optimizer.py` and preserves the preceding study's first optimizer
settings:

```text
method = COBYLA
rhobeg = 1.0
tol = 1e-7
catol = 0.0
```

Evaluate it without editing:

```bash
python run_round.py qaoa_depth15
```

For rounds 2 through 20:

1. Read the latest row in the ledger.
2. Activate only the role assigned by round parity.
3. Require one complete proposal grounded only in recorded ledger evidence.
4. Have the coordinator review and implement that proposal.
5. Write a concrete evidence-based `RATIONALE`.
6. Write a falsifiable `HYPOTHESIS`.
7. Have only the coordinator run exactly one evaluation.
8. Inspect the appended ledger row before activating the other role.

Never queue multiple proposals, run an unrecorded evaluation, probe the energy
oracle outside `run_round.py`, or generate a hidden parameter sweep.

## Permitted optimizer changes

The researcher may change:

- `OPTIMIZER_LABEL`, `RATIONALE`, and `HYPOTHESIS`;
- the complete body of `optimize`;
- optimizer family, schedules, steps, termination, restarts, hybrids, and
  time-use strategy;
- permitted NumPy, SciPy, math, statistics, and random utilities;
- counted finite-difference, parameter-shift, stochastic, or other gradient
  estimators.

The required API remains:

```python
def optimize(
    objective,
    initial_parameters,
    initial_energy,
    max_calls,
    seed,
    accepted,
):
    ...
```

`max_calls` is the hard scientific budget of 300 total objective calls,
including the fixed initial evaluation. Optimizer code receives that value but
not the evaluator clock. It should budget its probes so it can finish cleanly,
or continue useful work until convergence, return, or the evaluator stops it
before call 301.

## Circuit-call accounting

- Every objective invocation is charged, including duplicate vectors.
- The fixed initial evaluation is call 1.
- At most 299 optimizer-initiated objective calls remain after the fixed start.
- Call 300 is recorded and scored, then the round stops before call 301.
- Finite differences, shifts, line searches, stochastic samples, restart
  probes, and SciPy evaluations all count.
- Batching is unsupported.
- `accepted(parameters)` reuses a counted observation and costs no call.
- No post-optimization circuit evaluations occur.
- Gradient construction must operate through the counted objective.
- No free CUDA-Q gradient, direct Hamiltonian access, alternate simulator, or
  hidden analytic energy is allowed.

## Anti-gaming rules

- Always begin from the provided `initial_parameters`.
- Do not replace or warm-start the fixed input.
- Do not hard-code parameter vectors, energies, or case-specific guesses
  learned from prior traces.
- Do not carry parameters or state between rounds.
- Generic algorithm constants and ledger-supported hyperparameters may be
  hard-coded.
- Optimizer code may not read files, environment variables, local modules,
  process state, evaluator internals, or clocks.
- Do not import CUDA-Q or call a simulator directly.
- Do not inspect, replace, monkey-patch, or introspect the objective or
  accepted callback.
- Do not persist state outside the recorded optimizer source.
- Do not intentionally waste time after useful optimization has ended.

The source audit rejects common file, process, network, reflection, CUDA-Q,
clock, and local-harness access.

## Completion

After exactly 20 rounds:

1. Restore `optimizer.py` to the winning source under the energy and close-tie
   rules without running an extra evaluation.
2. Write `research/qaoa_depth15/insights.md` using only the ledger and saved
   optimizer sources.
3. Write a two- or three-sentence `figure_summary.txt`.
4. Run:

   ```bash
   python summarize_results.py
   python plot_results.py
   python verify_study.py --complete
   ```

Required deliverables are:

- `lowest_energy_by_round.png`: lowest energy per round, with marker shape for
  convergence and color for new-best status;
- `energy_trajectories_3d.png`: static round × observe call × best-energy
  trajectories;
- `energy_trajectories_3d.html`: polished, rotatable, dependency-free
  NVIDIA-style demo widget;
- mechanical Markdown summaries, ledger, traces, logs, and source snapshots.

`insights.md` must explain the winning optimizer, improvement over round 1,
Explorer and Improver contributions, convergence versus budget-cap behavior,
useful and wasteful optimizer mechanisms, reversals, failures, and evidence
that is weak or sensitive to the 300-observe boundary.

The completed verifier must pass before the study is reported as finished.

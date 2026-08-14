# Research loop and optimizer interface

The `qaoa_depth15` study has 20 sequential experiments. Round 1 records the
fixed COBYLA baseline. Explorer and Improver alternate by round parity, while
the coordinator alone implements and evaluates.

For each round, the evaluator:

1. Validates immutable files and the fixed 30-parameter start.
2. Audits and loads `research/qaoa_depth15/optimizer.py`.
3. Configures the fixed simulator and random seed.
4. Starts the secondary 120-second safety guard.
5. Evaluates the fixed starting vector as counted call 1.
6. Calls `optimize(objective, initial_parameters, initial_energy, max_calls,
   seed, accepted)` with `max_calls=300`.
7. Stops on accepted-energy convergence, optimizer return, the 300-observe
   cap, or the secondary time guard.
8. Records the lowest energy and parameters from every completed observation.
9. Appends the ledger and saves the trace, log, and optimizer source.

The oracle records and scores call 300, immediately raises its controlled stop,
and therefore never begins call 301. The best energy among calls 1–300 is
preserved.

The optimizer must call `accepted(parameters)` whenever it accepts an
iteration. That vector must exactly match a counted objective observation with
new objective work since the preceding report. The callback costs no call.

Accepted-energy convergence is three consecutive changes no larger than
`1e-6` after at least five optimizer iterations. A materially lower energy
beats a converged result; only energies within `1e-6` use convergence or early
completion as a tie-break.

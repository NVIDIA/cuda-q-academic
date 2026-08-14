# Depth-15 QAOA observe-budgeted optimizer autoresearch design

## Scientific question

Given the same seeded 30-parameter depth-fifteen QAOA start, which optimizer finds
the lowest circuit energy using at most 300 counted observes?

The graph, Hamiltonian, circuit, start, simulator, and evaluator are fixed.
Only optimizer code changes.

## Outcome and tie-breaking

The primary outcome is the minimum energy across every completed
`cudaq.observe` call in a round, including rejected probes and numerical
gradient calls. Energies within `1e-6` of the raw minimum form a close-tie set.
Within that set, convergence or early completion wins first, followed by lower
elapsed time, fewer calls, and earlier round.

## Budget enforcement

The fixed initial evaluation is call 1. Immediately after recording call 300,
the oracle raises the controlled `call_cap` stop, so call 301 cannot begin.
It serializes the best of the 300 completed observations. A 120-second internal
timer and 135-second subprocess timeout remain secondary safety guards.

## Guardrails

1. Every round starts from the same seeded 30-parameter vector.
2. One objective call equals one `cudaq.observe`.
3. The oracle records call count, elapsed time, and running best energy.
4. Optimizer code cannot inspect files, clocks, process state, CUDA-Q, or
   evaluator internals.
5. Accepted iterations match counted observations exactly.
6. Traces and source snapshots allow mechanical verification.
7. The verifier recomputes convergence, running minima, budget enforcement,
   leader flags, tie-breaking, and the restored winning source.

## Visual encoding

The static and interactive 3D plots show round, observe call, and running
lowest energy. The interactive widget defaults to orthographic projection and
adds camera presets, sliders, round isolation, keyboard controls, endpoint
labels, and clickable rows for easier reading.

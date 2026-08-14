# CUDA-Q depth-15, observe-budgeted QAOA optimizer autoresearch

This completed 20-round study used the weighted six-node `small` workshop
graph and fixed a fifteen-layer QAOA circuit with 30 parameters:

```text
gamma[0], ..., gamma[14], beta[0], ..., beta[14]
```

The objective is to find the lowest circuit energy under a hard budget of 300
counted `cudaq.observe` calls per round. Call 1 always evaluates the same seeded
initial vector, leaving at most 299 optimizer-initiated calls.

## Scoring and convergence

Every `objective(parameters)` invocation is one counted observe. The evaluator
records and scores call 300, then immediately stops the round; call 301 never
begins, and the best completed observation is preserved.

Accepted-energy convergence is:

```text
absolute delta energy <= 1e-6
patience = 3 accepted iterations
minimum accepted optimizer iterations = 5
```

Energy remains primary. Results within `1e-6` of the raw lowest energy use
convergence or early completion, then lower elapsed time, fewer calls, and
earlier round as tie-breakers. A secondary 120-second guard handles
unexpectedly slow execution but is not the scientific budget.

## Two-agent research loop

- Explorer proposes even rounds 2–20.
- Improver proposes odd rounds 3–19.
- The coordinator alone edits and evaluates.
- Only `research/qaoa_depth15/optimizer.py` may change during research.
- Every proposal uses only `results.tsv` as benchmark-result evidence.

Read `AGENTS.md` for the full protocol.

## Completed-study validation

```bash
python verify_study.py --complete
```

See `summary.md` and `research/qaoa_depth15/insights.md` for the outcome. The
winning optimizer is restored in `research/qaoa_depth15/optimizer.py`.

The interactive widget uses counted observes as its vertical axis and includes
camera presets, yaw/tilt/zoom controls, orthographic and perspective modes,
round isolation, keyboard controls, and clickable outcome rows.

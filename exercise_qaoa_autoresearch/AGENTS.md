# AutoResearch Agent Guide (MaxCut Custom Ansatz)

This folder is a minimal Karpathy-style autoresearch loop where the agent drives
each round by editing one CUDA-Q candidate kernel.

## Goal

Run a fixed 3-layer QAOA baseline for `mc_008_003_000` with 10 optimizer
iterations, then search for a custom 6-parameter ansatz with lower gate score.

Passing candidates satisfy:

```text
approx_ratio >= 0.95 * baseline_approx_ratio
```

Passing points are plotted green. Failing points are plotted red.

Gate score:

- `1 * (# single-qubit gates)`
- `10 * (# two-qubit gates)`

## Hard Rules

1. Make exactly one logical circuit change per round.
2. A logical change may add, remove, or modify multiple gates if they implement one coherent strategy.
3. Make circuit changes only in `candidate_kernel.py`.
4. Candidate circuits may use only `rx`, `ry`, `rz`, and CNOT gates via `x.ctrl`.
5. Keep exactly 6 variational parameters in the candidate.
6. Parameters may be placed anywhere and reused by multiple gates.
7. The harness calculates gate counts from the CUDA-Q kernel trace; do not add gate-count constants to the candidate.
8. Write the reasoning for that logical change in `--note` and ledger.
9. Keep experiment budget fixed at 10 optimizer iterations.
10. Do not edit evaluator logic or scoring logic during experiment rounds.
11. Do not define candidate-specific optimizer initial parameters.
12. Do not use CUDA-Q subkernels in the candidate file; write gates explicitly in `candidate_superkernel`.
13. If a change is worse, revert or replace it next round with exactly one logical change.
14. Use only real MaxCut instances in `instances/` (no synthetic data).

## Files You May Edit During Rounds

- `candidate_kernel.py`
- `ledger.md` (normally appended by harness)
- optional: `notes.md`

Treat all other files as harness infrastructure during experiment rounds.

## Candidate Kernel Contract

The editable candidate is a Python CUDA-Q module:

```text
candidate_kernel.py
```

Keep this editable candidate interface stable:

```python
PARAMETER_COUNT = 6

@cudaq.kernel
def candidate_superkernel(
    qubits: cudaq.qview,
    angles: List[float],
):
    ...
```

The harness owns the fixed `main_kernel`; do not edit it during rounds. It
creates the 8-qubit register, applies `h` to all qubits, and calls
`candidate_superkernel`.

The harness owns the fixed instance metadata for `mc_008_003_000` and always
starts optimization from all-zero parameters. The candidate file owns only:

- `PARAMETER_COUNT`
- the explicit gates in `candidate_superkernel`

## Quick Start

From this directory:

```bash
python3 harness.py baseline
python3 harness.py eval --change "initial custom ansatz" --note "starting candidate"
```

## Agent Round Loop

1. Read `program.md`.
2. Read recent rows in `ledger.md`.
3. Inspect `candidate_kernel.py`.
4. Make exactly one logical circuit edit in `candidate_kernel.py`.
5. Evaluate:

```bash
python3 harness.py eval --change "..." --note "..."
```

6. Repeat.
7. Generate report:

```bash
python3 harness.py report
```

Report requirements:

- Keep the existing eval data; do not rewrite ledger rows just to change reporting.
- Plot points with numeric run labels only, not full change text.
- Produce `reports/ansatz_comparison.md` as a compact report with:
  - a baseline-vs-best-candidate summary table,
  - a small table of passing custom gate-score levels,
  - a brief explanation of how the best custom ansatz differs from the fixed
    3-layer QAOA baseline.
- Do not print full CUDA-Q circuit drawings in the Markdown report; they are too
  large for this report format.

## Real Instance Notes

Use the real QED-C MaxCut files already present in `instances/`:

- `mc_008_003_000.txt` with `mc_008_003_000.sol`

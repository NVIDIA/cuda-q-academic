# Program: Agent-Orchestrated MaxCut AutoResearch

The agent runs this loop autonomously.

## Objective

1. Run the fixed baseline once:

```bash
python3 harness.py baseline
```

The baseline is the hardcoded 3-layer QAOA circuit for `mc_008_003_000`,
optimized from all-zero parameters for exactly 40 iterations.

2. Use the baseline approximation ratio to define the passing band:

```text
pass_threshold = 0.95 * baseline_approx_ratio
```

Any candidate with `approx_ratio >= pass_threshold` is passing and is plotted
green. Candidates below that threshold are plotted red. Ratios above the upper
side of the +/- 5% band are also passing.

3. Among passing candidates, minimize gate score:

```text
gate_score = (#single_qubit_gates) + 10*(#two_qubit_gates)
```

Failing candidates receive a large objective penalty so quality stays ahead of
gate count.

## Data Constraint

Use only real MaxCut instances already in `instances/`. Do not create synthetic
instances.

## Editable Circuit Surface

The circuit candidate is a CUDA-Q Python kernel module:

```text
candidate_kernel.py
```

The harness owns the fixed `main_kernel`, which creates the 8-qubit register,
applies `h` to all qubits, and then calls the editable
`candidate_superkernel`.

The candidate module owns only:

- `PARAMETER_COUNT = 6`
- `candidate_superkernel(qubits, angles)`

The six variational parameters may be placed anywhere in the candidate circuit
and may be reused by multiple gates. The custom ansatz gate alphabet is:

- `rx(...)`
- `rz(...)`
- `ry(...)`
- `x.ctrl(...)` for CNOT gates

Do not define candidate-specific optimizer initial parameters. The harness
always starts from six zeros.

Do not pass edge-index arrays into the candidate. Write the gates explicitly in
`candidate_superkernel`.

The harness calculates gate counts from a CUDA-Q translation of the evaluated
kernel. Do not declare gate-count constants in the candidate.

## One-Logical-Change Rule

Per round, perform exactly one logical change in `candidate_kernel.py`.

A logical change is one coherent strategy decision and may involve multiple
gate edits if they implement the same idea, for example:

- remove one entangling block,
- change a CNOT pattern,
- move one parameterized rotation family,
- reuse one angle across a group of gates,
- replace one rotation axis pattern.

Do not bundle multiple unrelated strategy decisions into a single round.

## Evaluation Commands

Reset files, then run:

```bash
python3 harness.py baseline
python3 harness.py eval --change "..." --note "..."
```

The optimizer budget defaults to 40 iterations. Keep it fixed.

The `--change` text should name exactly what changed in
`candidate_kernel.py`. The `--note` text should explain why that single logical
change was proposed.

## Final Report

```bash
python3 harness.py report
```

This produces:

- `reports/ratio_vs_gate_score.png`
- `reports/ansatz_comparison.md`

with:

- approximation ratio vs gate score,
- the baseline ratio,
- the 95% passing threshold,
- a shaded +/- 5% baseline band,
- green passing points and red failing points,
- numeric run labels on plotted points,
- a compact Markdown comparison report that summarizes the baseline, the best
  custom ansatz, all passing custom gate-score levels, and how the best custom
  ansatz differs from the fixed 3-layer QAOA baseline.

The Markdown report should not include full CUDA-Q circuit drawings; those are
too large for this report format.

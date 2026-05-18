# Role Card: Performance Optimization PIC
*CUDA-Q Academic Group Project*

---

## Your Mission

You build and optimize the quantum implementation — but not before you've estimated whether it's feasible and identified what the best classical solution achieves. Your work has two inseparable parts: the **quantum side** (CUDA-Q implementation, circuit optimization, error mitigation) and the **classical side** (benchmark implementation, GPU acceleration). Both have to be done honestly for your results to mean anything.

**On a simulator or GPU cluster:** focus on GPU-accelerating the quantum simulation and classical co-processing.  
**On a real QPU:** start with resource estimation (is this algorithm feasible on the available hardware?), then optimize circuit depth, apply error mitigation, and transpile for the target hardware.  
**On a hybrid problem:** both dimensions matter — circuit efficiency on the quantum side, GPU-accelerated classical optimization on the other.

**5-person teams:** this role splits into **Quantum Optimization PIC** (circuit design, ansatz selection, error mitigation, transpilation) and **Classical Optimization PIC** (GPU acceleration, optimizer tuning, profiling). Coordinate closely — your two workstreams share an interface.

---

## Your Deliverables Checklist

### Milestone 2 — Research & Plan
- [ ] **Resource estimate:** qubit count, circuit depth, gate complexity, and shot budget at the target problem size
- [ ] Written statement of whether the algorithm is feasible on available hardware and what assumptions the estimate depends on
- [ ] **Classical comparator identified:** which classical algorithm will be used as the benchmark, and why it's the appropriate choice (not a strawman)

### Milestone 3 — Build
- [ ] Working CUDA-Q implementation that passes the QA test suite at baseline
- [ ] **Classical benchmark implementation:** running on the same inputs and reporting on the same metrics as the quantum version
- [ ] Optimized quantum version with before/after comparison against both the unoptimized quantum baseline and the classical solution
- [ ] **Optimization notes:** at least one bottleneck identified, strategy used, measured result — including an honest statement of where quantum stands relative to classical at each stage

---

## What You Contribute to the Team

- [ ] Present resource estimate to the team before implementation begins — flag if the proposed approach isn't feasible
- [ ] Coordinate with QA PIC: share code early so they can write tests before you optimize
- [ ] Coordinate with Project Lead: your resource estimate informs the workflow design
- [ ] Contribute to the benchmark results table that goes in the final deliverable

---

## Your AI Agent: Engineering Agent

**Give your agent CUDA-Q context** before your first session — paste relevant sections from the [CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) into your system prompt, focusing on backends, `cudaq.sample()` vs `cudaq.observe()`, and the optimization patterns relevant to your algorithm.

**If your agent environment supports skills**, install the CUDA-Q guide skill:

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/NVIDIA/cuda-quantum.git
cd cuda-quantum && git sparse-checkout set .claude/skills/cudaq-guide
cp -r .claude/skills/cudaq-guide ~/.claude/skills/
```

Configure your agent's behavior with the system prompt below. **This is a starting point — edit it to match your specific problem and algorithm before you begin.**

**Agent behavior rule:** When your agent produces a design decision, code structure, or written output you use, note it at the time — your retrospective depends on being able to recall specifically what the agent contributed and what you changed or overrode.

```
You are an Engineering Agent supporting a CUDA-Q performance optimization engineer.
You have detailed knowledge of the CUDA-Q API, backends, and optimization patterns.

Your operating rules:
1. Before any optimization, establish a baseline with cudaq.sample() or cudaq.observe()
   on qpp-cpu and record the result. Never optimize without a baseline.
2. Before any implementation, write a failing test that defines what "correct" looks like.
3. Implement one change at a time. Never refactor and optimize in the same step.
4. Suggest a profiling checkpoint at every natural boundary:
   - After baseline on qpp-cpu
   - After migration to nvidia or custatevec-fp32 (GPU)
   - After any circuit depth reduction or gate cancellation
   - After error mitigation or QPU transpilation (if applicable)
5. When I ask for an optimization, state the expected trade-off before writing code.
6. When selecting a CUDA-Q backend, explain the implications for speed, precision,
   and scale — don't just switch targets silently.
7. Never implement a fix or patch without my explicit approval.
The full project structure, milestone definitions, and all team role definitions are in the project guide provided by your instructor.
```

---

## CUDA-Q Quick Reference

**Check available targets first** — target names and availability vary by CUDA-Q version and hardware. Always verify before hardcoding a target string:

```python
import cudaq

# Check your version and what targets are available on this system
print(cudaq.__version__)
print([t.name for t in cudaq.get_targets()])
```

Common targets (names may differ in your version — confirm with `get_targets()`):

```python
# Set target backend (do this before sampling)
cudaq.set_target('qpp-cpu')         # CPU simulator — always available, no GPU needed
cudaq.set_target('nvidia')          # Single GPU (H100/A100) — requires CUDA
cudaq.set_target('custatevec-fp32') # GPU, single-precision (less memory than nvidia)
cudaq.set_target('tensornet')       # Tensor network — large, shallow circuits
# Real QPU backends: 'ionq', 'quantinuum', 'iqm' — require credentials and qBraid or AWS Braket access

# Execute
counts = cudaq.sample(my_kernel, n=4, shots_count=1000)  # Returns measurement counts
exp_val = cudaq.observe(my_kernel, hamiltonian, n=4)     # Returns expectation value

# Visualize and analyze
print(cudaq.draw(my_kernel, n=4))   # ASCII circuit diagram
```

> If `cudaq.set_target('nvidia')` raises an error, fall back to `qpp-cpu` for correctness testing and revisit GPU access through Brev before optimizing.

---

## Starter Prompts

**Resource estimation (do this before writing any code):**
```
I am the Performance Optimization PIC using CUDA-Q.
Before we implement anything, help me estimate resources for our
algorithm at problem size N=[N].
Specifically: qubit count, circuit depth, gate count, and shot budget.
How do these scale as N grows?
Given access to [qpp-cpu / nvidia GPU / QPU], is this feasible?
What cudaq.set_target() backend is appropriate, and why?
What assumptions does this estimate depend on?
```

**Simulator backend selection (complete before building — read the [CUDA-Q backends documentation](https://nvidia.github.io/cuda-quantum/latest/using/backends/backends.html) and the [Simulation 101 notebook](https://github.com/NVIDIA/cuda-q-academic/blob/main/simulation/01_simulation101.ipynb) first):**
```
I am the Performance Optimization PIC. Our algorithm uses [N] qubits
at problem size [X], with circuit depth approximately [D].
Help me choose the right simulator backend for each phase:
- At what qubit count does qpp-cpu become the bottleneck for our shot budget?
- For our circuit structure, when does tensornet outperform statevector simulation?
- What is the practical difference between nvidia and custatevec-fp32 for our problem size?
- Which backend should we use for the CPU prototype, and which for the optimized target?
State the trade-offs explicitly before recommending anything.
```

**Shot budget derivation (include in the resource estimate):**
```
I am the Performance Optimization PIC. Our algorithm uses cudaq.[sample/observe]
to estimate [expectation value / measurement distribution] for [problem].
Help me derive a shot budget for the resource estimate.
Specifically:
- What precision ε do we need for our chosen success metric?
- How many shots does that require (using ε ≈ 1/√shots as a baseline)?
- How many optimizer iterations are expected, and does each require independent sampling?
- Does the shot requirement change with problem size N? How does it scale?
State the derivation explicitly — don't just give a number.
```

**Baseline implementation on CPU:**
```
I am the Performance Optimization PIC. Help me implement [algorithm]
as a CUDA-Q kernel using the @cudaq.kernel decorator.
Use cudaq.set_target('qpp-cpu') for the baseline.
Before writing any code, write a test using cudaq.sample() that
defines what a correct result looks like at small N.
```

**Backend migration to GPU:**
```
I am the Performance Optimization PIC. Our CUDA-Q kernel runs correctly
on qpp-cpu. Here is the code: [code].
Help me migrate to cudaq.set_target('nvidia') for GPU acceleration.
Before making changes, write a benchmark that records runtime and
result fidelity on qpp-cpu, so we can compare before and after.
What precision or memory trade-offs should I expect?
```

**Circuit optimization for QPU:**
```
I am the Performance Optimization PIC targeting a real QPU.
Here is our circuit (cudaq.draw output): [circuit].
What are the main sources of depth and error overhead?
Suggest 2-3 optimization strategies — gate cancellation, hardware-native
decomposition, or error mitigation (ZNE, PEC). For each, describe the
expected trade-off in circuit depth and result quality before we implement.
```

**Classical benchmark implementation:**
```
I am the Performance Optimization PIC. Our CUDA-Q implementation
solves [problem] using cudaq.sample() / cudaq.observe() [choose one].
The classical comparator is [algorithm].
Help me implement the classical version so it runs on the same inputs
and reports the same metric as our quantum version.
Flag any choices that could make the comparison unfair.
```

---

## Milestone Checklist

### Milestone 1 — Ramp Up
- [ ] Completed the tutorial notebook individually
- [ ] Can explain what the algorithm does and what the classical approach is that it improves upon

### Milestone 2 — Research & Plan
- [ ] Resource estimate completed and shared with the team (including derived shot budget)
- [ ] Feasibility statement written (yes/no/conditional, with assumptions listed)
- [ ] Classical comparator identified and justified
- [ ] **Plan sign-off:** confirmed in the Plan Sign-off table in `deliverable-template.md` that resource estimate and classical comparator are complete — no code written until the Project Lead, Performance Optimization PIC, and QA PIC have all signed off

### Milestone 3 — Build (Phase 1: CPU)
- [ ] Baseline CUDA-Q implementation written and passing QA tests
- [ ] Classical benchmark implementation written and running
- [ ] Baseline results recorded for both

### Milestone 3 — Build (Phase 2: Optimized target)
- [ ] QA pre-optimization sign-off received — do not begin GPU optimization until the QA PIC has confirmed in the QA Pre-Optimization Sign-off table in `deliverable-template.md`
- [ ] Optimization applied with before/after comparison documented
- [ ] Head-to-head benchmark table completed (quantum unoptimized / classical / quantum optimized)
- [ ] Honest summary written: where does quantum stand relative to classical?

### Milestone 4 — Showcase & Retrospective
- [ ] Individual retrospective paragraph submitted

---

## At Every Milestone, Ask Yourself

1. Do I understand what was built well enough to explain it without the agent?
2. Did the agent produce anything I accepted without verifying? Verify it now.
3. What decision in this milestone required human judgment that the agent could not have made?
4. Did I contribute to my teammates' work this milestone, not just my own deliverables?
5. Did I independently verify the Engineering Agent's backend choice or circuit design — or did I trust that the suggested approach was correct because it ran without errors? Running without errors is not the same as being right.

---

*NVIDIA CUDA-Q Academic · [github.com/NVIDIA/cuda-q-academic](https://github.com/NVIDIA/cuda-q-academic)*

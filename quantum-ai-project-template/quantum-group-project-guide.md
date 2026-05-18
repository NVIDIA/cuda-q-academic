# Quantum Computing Group Project Guide

## Role-Based Collaboration with Agentic AI and Quantum-GPU Supercomputing

**Group size:** 4–5 students | **Duration:** 1–3 weeks (adaptable)  
**Repository:** [NVIDIA CUDA-Q Academic](https://github.com/NVIDIA/cuda-q-academic)  
**Structure adapted from:** [MIT iQuHACK 2026 NVIDIA Challenge](https://github.com/iQuHACK/2026-NVIDIA)

---

## Setting Up Your Environment and AI Agent

### CUDA-Q environment

All code in this project uses [CUDA-Q](https://github.com/NVIDIA/cuda-quantum), NVIDIA's open-source platform for hybrid quantum-classical computing. Your implementation will progress through three execution environments. The **CUDA-Q target** is the backend you select with `cudaq.set_target()` — it controls where your circuit runs (CPU simulator, GPU, or real quantum hardware):

| Phase | Environment | CUDA-Q target | When |
| :---- | :---- | :---- | :---- |
| Prototype | [qBraid](https://account.qbraid.com) or Google Colab | `qpp-cpu` (CPU simulator, always available) | Milestones 1–2 and early M3 |
| GPU-accelerated | [Brev](https://brev.nvidia.com/launchable/deploy/now?launchableID=env-39dN1v7RucHHgj97LILUlnXjnk5) | `nvidia` (single GPU) or `custatevec-fp32` (GPU, lower memory) | Milestone 3 optimization |
| Real QPU *(optional)* | qBraid QPU access or AWS Braket | hardware backend | Milestone 3 stretch goal |

Your Performance Optimization PIC is responsible for the backend migration and for documenting the backend selection in the project plan. Every other team member should understand what backend the code is running on and why.

Before Milestone 3, the Performance Optimization PIC should work through the [CUDA-Q backends documentation](https://nvidia.github.io/cuda-quantum/latest/using/backends/backends.html) and the [Simulation 101 notebook](https://github.com/NVIDIA/cuda-q-academic/blob/main/simulation/01_simulation101.ipynb) — the notebook covers the trade-offs between statevector, tensor network, and GPU backends, and includes runnable code snippets for each. The backend selection is a planning decision recorded in the deliverable template, not something to decide mid-build.

### Setting up your AI agent

Use whatever AI coding assistant or chat-based LLM your course provides or your team already has access to — the role card system prompts work with any of them. Pick one tool as a team and use it consistently; switching mid-project creates context gaps.

**Give your agent CUDA-Q context at the start of each session.** Without it, your agent may produce code based on outdated or incorrect API patterns. The simplest approach: paste relevant sections from the [CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) into your system prompt — at minimum, the sections on kernels (`@cudaq.kernel`), backends (`cudaq.set_target()`), and execution (`cudaq.sample()` vs `cudaq.observe()`). If your tool supports web browsing or file upload, point it at the docs directly.

**If your agent environment supports skills**, install the CUDA-Q guide skill for persistent, session-to-session API knowledge:

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/NVIDIA/cuda-quantum.git
cd cuda-quantum && git sparse-checkout set .claude/skills/cudaq-guide
cp -r .claude/skills/cudaq-guide ~/.claude/skills/
```

Each role card includes a starter system prompt to configure your agent's *behavior*. **You are encouraged to edit that system prompt** to match your specific problem, algorithm, and working style — the role card version is a starting point, not a fixed configuration.

**For project planning and brainstorming**, all team members are encouraged to use the [Superpowers brainstorming skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md). Trigger it with `/superpowers:brainstorm` and describe what you're trying to build or decide. It asks one question at a time, proposes 2–3 approaches before settling on one, and won't let you move to implementation until a plan is approved — exactly the discipline Milestone 2 requires. Use it when scoping your problem, selecting your algorithm, or defining your success metric.

---

## The Core Framing

*"In modern quantum R&D, speed matters — but rigor and coordination matter more. Your collective job is to decompose the problem, delegate tasks across your team and AI agents, and — most importantly — verify the work. Let the agents build the code. You build the architecture."*

Each student has a **role** with explicit deliverables and a dedicated **AI agent** configured for that role's work. No one builds before the team has a plan. No plan is complete without a definition of success.

---

## The Roles

Each student is the **Person in Charge (PIC)** of one role — meaning they own the final deliverables for that role and are accountable for their quality (PIC means accountable for that role, not working alone). Every milestone involves the whole team: PICs review each other's work, contribute to shared decisions, and catch problems across role boundaries. The role structure defines *accountability*, not silos.

Teams of 4 use one person per role. Teams of 5 split the Performance Optimization PIC into two: one focused on the **quantum side** (circuit design, error mitigation, noise-aware compilation, QPU transpilation) and one on the **classical side** (GPU acceleration, classical optimizer tuning, profiling).

| Role | Owns | AI Agent |
| :---- | :---- | :---- |
| **Project Lead** | Strategy, decomposition, coordination | Orchestrator |
| **Performance Optimization PIC** | CUDA-Q implementation, optimization | Engineering Agent |
| **Quality Assurance PIC** | Test suite, adversarial review, benchmark fairness | Gremlin + Fixer (an adversarial pair: Gremlin finds failures, Fixer proposes patches) |
| **Technical Marketing PIC** | Showcase, retrospective, attribution | Synthesis Agent |

**Your role card** has everything you need to run your role: deliverables checklist, AI agent setup, and starter prompts. Find yours in the `role-cards/` folder — the files are named `role-card-project-lead.md`, `role-card-performance-optimization.md`, `role-card-quality-assurance.md`, and `role-card-technical-marketing.md`.

---

## The Four Milestones

### Milestone 1 — Ramp Up *(Individual + Team)*

**Goal:** Everyone can run the tutorial and explain what the algorithm is doing before anyone builds anything.

- Each student completes the scaffolded tutorial notebook individually
- Project Lead facilitates a 15-minute team discussion: "what does this algorithm actually do?" — no code, just concepts
- QA PIC logs the team's shared understanding and any open assumptions

**Before moving on:** *Can each team member explain the classical approach the quantum algorithm is trying to improve upon?*

**Platform:** CPU simulation using the `qpp-cpu` target (qBraid, Google Colab, or local Jupyter — no GPU required)

---

### Milestone 2 — Research & Plan *(Project Lead–owned)*

**Goal:** Written strategy with success metric defined, sub-tasks scoped, and first test written — before any implementation.

- Project Lead surveys the algorithmic landscape and proposes algorithm(s) and hybrid workflow for team agreement
- Performance Optimization PIC produces the resource estimate and identifies the classical benchmark
- QA PIC writes the first acceptance test in plain English (not code yet)
- Team reviews and agrees on the full plan before anyone starts building

**Deliverable:** One-page project plan — fill in the **Milestone 2 — Project Plan** section of `deliverable-template.md`.

**Before moving on:** *Does the plan describe the full hybrid workflow, include a resource estimate, and name a specific classical comparator — and does the team agree on all three?*

---

### Milestone 3 — Build *(Performance Optimization PIC + QA PIC co-owned)*

**Goal:** Working CUDA-Q implementation, passing tests on CPU, then migrated to GPU-accelerated execution.

- Performance Optimization PIC implements the quantum solution and the classical comparator (TDD-first)
- QA PIC runs adversarial review of both quantum code and benchmark setup
- Team resolves failures collaboratively
- Performance Optimization PIC applies optimizations and records results in the Optimization Summary section of `deliverable-template.md`

**Deliverable:** Working CUDA-Q code, passing test suite, head-to-head benchmark results table — record in the **Milestone 3 — Build Results** section of `deliverable-template.md`.

**If your quantum implementation does not outperform the classical baseline, this is a valid finding.** Document at what problem size (N) or circuit depth an advantage appears — or confirm that it does not within your tested range. Report the crossover point if you find one, and state honestly what resource budget would be needed to reach it. A rigorous null result is more valuable than an overclaimed positive.

**Before moving on:** *Does the results table compare quantum against classical on the same inputs and metric? If quantum underperformed: have you documented the crossover point or confirmed it is outside your tested range, and does the Technical Marketing PIC have a drafted null-result framing ready for the showcase?*

**Platform transition:** CPU simulation → GPU cluster via Brev, real QPU via qBraid or AWS Braket, or both for hybrid problems

---

### Milestone 4 — Showcase & Retrospective *(Technical Marketing PIC–owned)*

**Goal:** Communicate results to an external audience; reflect critically on the AI-assisted workflow.

- Technical Marketing PIC produces the showcase presentation
- Each team member contributes one paragraph to the retrospective about their AI agent
- Team discussion: "What did we verify that the agent got wrong? What did we trust and shouldn't have?"
- Project Lead ensures all deliverables are in the repository and attributed

**Deliverable:** Showcase presentation + retrospective document — record in the **Milestone 4 — Showcase & Retrospective** section of `deliverable-template.md`.

**Before moving on:** *Does the retrospective distinguish between what the AI generated and what the team decided?*

---

## Assessment Rubric

| Criterion | Weight | Indicators | GPU-Quantum skill assessed |
| :---- | :---- | :---- | :---- |
| **Problem Decomposition and Planning** | 15% | Plan names a specific classical comparator; success metric defined with a rejected alternative; resource estimate (qubit count, circuit depth, shot budget) present; hybrid workflow described end-to-end; Plan Sign-off table in `deliverable-template.md` §"Plan Sign-off" signed by all three PICs before any code is written | Decomposing a hybrid quantum-classical workflow into classical preprocessing, quantum kernel, and GPU post-processing components |
| **Simulator Backend Selection** | 5% | Simulator Backend Selection table in `deliverable-template.md` §"Simulator Backend Selection" completed for both prototype and optimized phases; backend choice is justified, not left as the default; simulation limit stated; if GPU was unavailable, documented explicitly | Selecting and justifying CUDA-Q execution backends (`qpp-cpu`, `nvidia`, `custatevec-fp32`, real QPU) for each project phase |
| **Correctness and Verification** | 20% | Test suite covers nominal, boundary, and adversarial cases; QA Implementation Review in §"QA Implementation Review" is a substantive paragraph naming specific decisions reviewed; Challenged Assumption in §"Challenged Assumption" names the assumption, who held it, and how it was resolved | Understanding shot-count sensitivity and probabilistic output in quantum circuits; the difference between CPU-simulation correctness and GPU-backend validation |
| **Classical Benchmarking** | 20% | Appropriate comparator named and justified in M2; QA Benchmark Fairness Review in §"QA Benchmark Fairness Review" explicitly addresses whether the comparison is on equal terms (same input sizes, same metric, same hardware tier where possible); benchmark results table records the CUDA-Q target/backend for every run; results reported honestly, including null results | Applying rigorous classical benchmarking in the context of quantum-GPU computing; understanding that GPU-accelerated simulation is a distinct execution tier, not just faster CPU |
| **Performance Optimization** | 20% | Optimized implementation shows measurable before/after improvement in §"Optimization Summary" with a named bottleneck and a measured result; head-to-head comparison with classical solution at the same problem size; backend used for optimized run is named; if real QPU was attempted, simulation-vs-hardware differences noted | Circuit-level performance characteristics: qubit count, circuit depth, shot budgets, simulation limits; tradeoffs between simulated and real QPU execution |
| **Executive Summary and Showcase Communication** | 10% | Executive Summary in §"Executive Summary" written by the Technical Marketing PIC, states what was demonstrated at what scale with what resource budget, includes scope limitations; showcase presents quantum vs. classical comparison for a non-specialist; any advantage claim names the backend, problem size, and metric — no overclaimed "quantum advantage" | Communicating the scope and limitations of GPU-accelerated quantum simulation accurately; distinguishing simulated advantage from demonstrated hardware advantage |
| **Individual Retrospectives** | 5% | Four individual retrospective paragraphs in §"Individual Retrospectives", one per role, each written by the person in that role; each names specific agent errors or limitations; paragraphs that only say "the agent was helpful" without critical evaluation do not meet the bar | Critically reflecting on AI-assisted quantum-GPU development: which agent outputs required human correction, and which decisions about circuit design or backend selection could not have been delegated |
| **Collaborative Role Execution** | 5% | Each role's deliverables are present and traceable to a named section in `deliverable-template.md`; AI attribution is explicit; no section left at placeholder text | Operating with shared understanding of backend choices and benchmark design across a role-based team |

---

*Developed for the [NVIDIA CUDA-Q Academic](https://github.com/NVIDIA/cuda-q-academic) repository. Adaptation and reuse with attribution encouraged.*

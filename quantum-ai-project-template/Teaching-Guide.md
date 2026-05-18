# Teaching Guide: Quantum Computing Group Project Template

*This guide is for instructors. The student-facing files in this folder are drafts — not yet ready to distribute. See the [README](./README.md) for status and what needs to be done before sharing with students.*

This document covers how to use the group project template in your course.

---

# Part 1 — Using This Template in Your Course

## What This Template Provides

The project template gives teams a defined structure for a quantum computing group project. You supply the problem and the tutorial notebook. What the template provides:

- **Four defined roles** with explicit deliverables and accountability — Project Lead, Performance Optimization PIC, Quality Assurance PIC, and Technical Marketing PIC (PIC = Person in Charge: accountable for that role's deliverables, not working alone)
- **Four milestones** that enforce a plan-before-build discipline and require honest classical benchmarking
- **Starter AI agent configurations** for each role — system prompts and starter prompts that students adapt to their specific problem
- **A deliverable template** that captures the project plan, benchmark results, and retrospective in one document
- **Suggested project options** ranging from a fully scaffolded problem (MIT iQuHACK 2026 LABS challenge) to student-designed projects

The structure is designed to be adapted into an existing course — the sections below describe what you will need to customize before distributing the files to students.

---

## Before You Deploy: What to Customize

Three things in the template require your input before students see any files. Everything else works as-is.

### 1. Choose or provide the project problem

You have three paths: pick one of the suggested projects below as-is (Options A–D), let students design their own (Option E), or add a course-specific problem of your own. Each suggested project includes a defined problem, a classical comparator, and a link to the relevant CUDA-Q Academic scaffold. The four criteria a valid problem should meet are described in "[Choosing a problem](#choosing-a-problem)" below.

**Option A — LABS Optimization (MIT iQuHACK 2026)**
QAOA-seeded hybrid quantum-classical algorithm for the Low Autocorrelation of Binary Sequences problem, GPU-accelerated with Memetic Tabu Search. *Classical comparator:* MTS run without quantum seeding. Full scaffold at [iQuHACK/2026-NVIDIA](https://github.com/iQuHACK/2026-NVIDIA).

**Option B — QAOA for Max-Cut with Circuit Cutting**
QAOA for graph Max-Cut with CUDA-Q circuit cutting for smaller QPU simulators. *Classical comparator:* Goemans-Williamson SDP (0.878-approximation guarantee). Based on the [CUDA-Q Academic circuit cutting notebooks](https://github.com/NVIDIA/cuda-q-academic).

**Option C — Hybrid Quantum Neural Network**
Hybrid QNN classifier (parametrized quantum circuit layers + classical dense layers) vs. a classical neural network of comparable parameter count. *Classical comparator:* matched parameter count, same dataset and split.

**Option D — Quantum Error Correction Decoder**
Compare decoding strategies for a small error correcting code in CUDA-Q. *Classical comparator:* minimum-weight perfect matching (MWPM), the standard classical decoder for surface codes.

**Option E — Student-Designed Project (open-ended)**
Add a Brainstorm Milestone before Milestone 1 — typically one additional week or a dedicated session. Direct students to the [Superpowers brainstorming skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) (`/superpowers:brainstorm`) alongside the four criteria in "Choosing a problem" below — it enforces a one-question-at-a-time dialogue, proposes 2–3 approaches before settling, and won't advance to implementation until the team approves the design. The Project Lead explores candidate problems with their agent, the QA PIC evaluates each against the four criteria, and the team votes. You may want to review and approve each team's problem statement before they proceed to Milestone 1. If you use this option, share this quick-start prompt with students:

```
We are a quantum computing team in [class name] with access to [hardware/simulator].
Our quantum computing and educational background is [].
We have [] hours over [] weeks to complete this project.
Help us brainstorm 3-5 project ideas. For each, describe:
- The problem and a known classical algorithm that solves it well
- Why that classical algorithm is the right comparator (not a strawman)
- One quantum approach that might improve on it and why
- Two competing metrics we could use to measure the comparison
We will decide — help us reason through the options.
```

**Adding a course-specific problem.** If you have a problem relevant to your domain or course topic, replace one of the options above (or add it as Option F). At minimum, your problem description should include:
- The problem statement and why it is hard classically
- The quantum approach you expect teams to take
- The classical comparator teams should benchmark against, and why it is the right one
- A pointer to any CUDA-Q Academic module or external scaffold that gives teams a starting point

### 2. Tell students what tools and compute they have access to

The student guide and role cards describe agent setup in general terms — students need to know what is actually available to them in your course. Before distributing the files, add a note (in the student guide, a course page, or a separate handout) that specifies:

**Agentic tools:** which AI coding assistant or chat-based LLM students should use — whether that is a university-licensed tool, a specific free-tier service, or their own choice. If your institution has a preferred or supported option, say so explicitly; otherwise students will make inconsistent choices that are harder to support. Also clarify whether the CUDA-Q guide skill install is expected (it requires an agent environment that supports skills) or whether students should use the documentation-pasting approach instead.

**Compute resources:** which execution environments are available and how to access them:
- **CPU simulation** — qBraid or Google Colab are generally accessible without special provisioning; confirm which your course supports
- **GPU acceleration** — if you are provisioning Brev access, GPU cloud credits, or a university HPC allocation for Milestone 3, tell students this before they start and include access instructions; if GPU access is not available, tell them CPU simulation is sufficient and they should document the backend limitation in their results
- **Real QPU access** — if available through a [CUDA-Q hardware backend](https://nvidia.github.io/cuda-quantum/latest/using/backends/hardware.html) directly, qBraid, AWS Braket, or another cloud QPU provider, specify which hardware, how to request access, and any shot budget or cost constraints students should stay within

Students who do not know what compute they have will either under-use what is available or spend time chasing access they do not have. Setting this expectation at kickoff prevents both.

### 3. Add submission instructions and customize the rubric

The template does not include submission instructions — these depend on your course infrastructure. Before distributing the files, add your instructions to the student guide or as a separate handout. At minimum, tell students:

- **Where to submit:** for example, each team creates a GitHub repository and adds you as a collaborator so you can review code, run tests, and access the completed `deliverable-template.md` directly. A shared repo also gives you a timestamped record of when each milestone was completed.
- **What to submit:** the completed `deliverable-template.md` plus the full repository (code, tests, benchmarks). The deliverable template is structured to capture every graded element — you can grade directly from it without chasing separate documents.
- **Milestone check-in format:** whether you want teams to submit the deliverable template incrementally (after each milestone) or once at the end.
- **Showcase format:** in-class presentation, recorded video, written report, or some combination.

Also **replace the rubric in the student guide** with your own version before distributing — see the Assessment section below for the instructor rubric and guidance on what to adapt.

---

## Integrating Into Your Course

### Prerequisites for students

Students should be able to write and run basic CUDA-Q circuits before starting Milestone 1. The [CUDA-Q Academic Quick Start](https://nvidia.github.io/cuda-q-academic/learningpath.html?track=track-quickstart) notebooks (1–3) provide the minimum required background. Students do not need prior experience with hybrid algorithms or quantum hardware — Milestone 1 is explicitly designed to build that foundation.

### Timing

The template is designed for **1–3 weeks** of active project work, not counting any prerequisite modules. A typical deployment:

| Week | Milestones | Student activities |
| :---- | :---- | :---- |
| 1 | M1 + M2 | Tutorial completion, team kickoff, research and planning |
| 2 | M3 | Implementation, testing, optimization |
| 3 | M4 | Showcase preparation and presentation |

For shorter courses or workshops, Milestones 1 and 2 can be compressed into a single session with pre-assigned roles and a guided algorithm selection.

### Group formation

Assign roles before the first session — students should arrive at Milestone 1 knowing their role. For teams of 4, one student per role. For teams of 5, split the Performance Optimization PIC into Quantum Optimization PIC and Classical Optimization PIC (see the role card for details).

For longer courses or multi-project sequences, **role rotation is strongly recommended**. Students who have played the QA PIC role write better code when they move to Performance Optimization, because they have internalized the Verifier's perspective. Students who have played the Technical Marketing PIC role communicate their code more clearly, because they have practiced translating technical results for a non-specialist. The standard POGIL recommendation is for every student to play every role at least once over the course of a term (Farrell et al., 1999; Heller & Hollabaugh, 1992).

### Platform setup

Students need access to at least one of the following environments before Milestone 1:

- **[qBraid](https://account.qbraid.com)** — CUDA-Q pre-installed, supports classroom collaboration, recommended for Milestones 1–2
- **[Google Colab](https://colab.research.google.com)** — Zero setup, uncomment install cell in each notebook
- **[Brev](https://brev.nvidia.com/launchable/deploy/now?launchableID=env-39dN1v7RucHHgj97LILUlnXjnk5)** — One-click GPU environment, needed for Milestone 3 GPU optimization
- **[AWS Braket](https://aws.amazon.com/braket/)** — Managed quantum development environment that can run CUDA-Q notebooks in Jupyter, with optional access to real QPU hardware

Students who pursue real QPU execution have two paths: target a supported QPU directly through a [CUDA-Q hardware backend](https://nvidia.github.io/cuda-quantum/latest/using/backends/hardware.html) (if your course or institution has credentials for that vendor), or go through a cloud QPU provider such as qBraid's hardware access, AWS Braket, or another platform that brokers QPU time.

### AI agent setup

The agent configurations in the role cards are platform-agnostic and can be implemented as system prompt presets in any chat-based LLM, `SKILL.md` files in Claude Code or similar agentic coding environments, or custom instructions in Cursor or Windsurf. The key principle is that each role's agent is configured from the role card starters **before the project begins** — ideally as part of the Milestone 1 kickoff — not improvised mid-task. Students should expect to adapt the system prompts to their specific problem before they begin.

Each role card includes the CUDA-Q skill install command ([`github.com/NVIDIA/cuda-quantum`](https://github.com/NVIDIA/cuda-quantum/tree/main/.claude/skills/cudaq-guide)). Ask students to install it before Milestone 1. With it installed, agent code quality improves noticeably — the skill provides verified API knowledge rather than training data that may reflect older versions.

### Assessment

The student guide includes a summary rubric that students can see. **Before distributing the files, replace that rubric with your own version** — both to align weights with your course and to adapt the indicators for the specific problem you've assigned. A benchmark fairness indicator for QAOA Max-Cut looks different than one for a hybrid QNN; students work better when the criteria are specific to what they are actually building.

The rubric below maps each criterion to the learning objectives from the CS2023 competency framework. Suggested weights are a starting point. Two things worth preserving regardless of what you change: the retrospective should carry individual weight (not just a group deliverable), and the classical benchmarking criterion should be worth meaningful points — it is the element most commonly dropped or hollowed out, and it is one of the most pedagogically important.

| Criterion | Suggested weight | Learning objective (CS2023) | GPU-Quantum Learning Objective | What to look for |
| :---- | :---- | :---- | :---- | :---- |
| **Problem decomposition and planning** | 15% | Systematic decomposition and planning | Understand how a hybrid quantum-classical workflow decomposes into distinct components (classical preprocessing → quantum kernel → GPU post-processing) and why each boundary exists | Written plan names a specific classical comparator; success metric defined with a rejected alternative; resource estimate present (qubit count, circuit depth, shot budget, gate complexity); hybrid workflow described end-to-end; all three PICs signed off before any code written — Plan Sign-off table in `deliverable-template.md` §"Plan Sign-off" is filled in with explicit confirmation from each PIC |
| **Simulator backend selection** | 5% | Systematic decomposition and planning; attention to correctness | Select and justify a CUDA-Q execution backend for each phase; understand the capability boundaries of `qpp-cpu`, `nvidia`, `custatevec-fp32`, and real QPU targets | Simulator Backend Selection table in `deliverable-template.md` §"Simulator Backend Selection" is completed for both the prototype and optimized-target phases; the choice of backend is justified (not left as the default or unexplained); simulation limit (max qubit count or circuit depth) is stated for the prototype backend; if GPU access was unavailable, this is documented explicitly rather than left blank |
| **Correctness and verification** | 20% | Attention to correctness and verification; critical oversight of AI-generated work | Understand circuit-level correctness requirements specific to quantum-GPU execution: shot-count sensitivity, probabilistic output interpretation, and the difference between a passing test on CPU simulation and validated behavior on a GPU backend | Test suite covers nominal, boundary, and at least one adversarial case; QA Implementation Review in `deliverable-template.md` §"QA Implementation Review" is one substantive paragraph from the QA PIC (not a generic sign-off) that names specific decisions reviewed; Challenged Assumption in §"Challenged Assumption" names the original assumption, identifies who held it, and states how it was resolved — "no assumptions challenged" is not an acceptable entry |
| **Classical benchmarking** | 20% | Attention to correctness; persistence in the face of ambiguity | Apply classical benchmarking in the specific context of quantum-GPU computing: same inputs, same metric, and honest accounting of GPU vs. CPU vs. QPU execution conditions; understand why GPU-accelerated simulation is not the same as real QPU execution | Comparator is appropriate, not a strawman — QA Benchmark Fairness Review in `deliverable-template.md` §"QA Benchmark Fairness Review" is a substantive paragraph from the QA PIC that explicitly addresses whether the classical and quantum implementations are compared on equal terms (same input sizes, same metric definitions, same hardware tier where possible); results reported honestly, including negative or null results; the benchmark results table in §"Head-to-Head Benchmark Results" records the CUDA-Q target/backend for every run |
| **Performance optimization** | 20% | Persistence in the face of ambiguity | Measure and improve circuit-level performance characteristics (qubit count, circuit depth, shot budget) and understand the tradeoffs between simulated and real QPU execution; GPU-accelerated simulation is treated as a distinct execution tier, not just "faster CPU" | Optimized implementation shows measurable before/after improvement documented in §"Optimization Summary" with a named bottleneck and a measured result; head-to-head comparison with classical solution is at the same problem size; backend used for the optimized run is named and justified; if real QPU execution was attempted, simulation-vs-hardware differences are noted |
| **Executive summary and showcase communication** | 10% | Effective professional communication; ethical responsibility and transparency | Communicate the scope and limitations of GPU-accelerated quantum simulation accurately to a non-specialist audience; distinguish between simulated advantage and demonstrated hardware advantage | Executive Summary in `deliverable-template.md` §"Executive Summary" is written by the Technical Marketing PIC, states what was demonstrated at what scale with what resource budget, and includes honest scope limitations; showcase presentation presents the quantum vs. classical comparison clearly for a non-specialist; no overclaimed "quantum advantage" — any advantage claim names the backend, problem size, and metric |
| **Individual retrospectives** | 5% | Reflective practice; ethical responsibility and transparency | Critically reflect on AI-assisted quantum-GPU development: which agent outputs required human correction, and which decisions about circuit design, backend selection, or benchmark methodology could not have been delegated | Four individual retrospective paragraphs in `deliverable-template.md` §"Individual Retrospectives" are each present and each person's is their own — one paragraph per role is the minimum; each paragraph names specific agent errors or limitations, not generic observations; paragraphs that say only "the agent was helpful" or describe the agent's contributions without critical evaluation do not meet the bar |
| **Collaborative role execution** | 5% | Collaborative teamwork and shared ownership | Demonstrate that role-based accountability structures function in a hybrid quantum-classical project: each role's deliverables are traceable, and the team operated with shared understanding of backend choices and benchmark design | Each role's deliverables are present and traceable to a named section in `deliverable-template.md`; AI attribution is explicit; individual contributions are distinguishable; no section is missing or left at placeholder text |

**Formative checkpoints.** Each milestone ends with a "Before moving on" question — these are natural low-stakes checkpoints for instructors who want to assess incrementally. Requiring teams to answer them in writing (one or two sentences each) at milestone transitions takes little class time and gives early warning of teams proceeding without real understanding.

**Individual vs. group grades.** The retrospective is the primary mechanism for individual differentiation within a group grade. If your course requires fully individual grades, add an oral explanation requirement — a short check-in where each student explains what the code does without reference to their agent's output. This is described in the "Preventing AI Over-Reliance" section below.

---

## Adapting the Template

### Choosing a problem

Any valid project problem should meet these four criteria:

1. **A classical baseline exists** — teams can answer "what does the best classical algorithm achieve?"
2. **The problem is decomposable** — genuine distinct sub-tasks exist for different roles to own
3. **Success is not pre-defined** — competing metrics require teams to make and defend a choice
4. **Optimization is meaningful** — there is a real performance dimension to explore

The third criterion is the one worth expanding: **the problem should be open-ended enough that success is not pre-defined**. Problems with a single obvious metric are easier to set up, but they eliminate the most important learning opportunity in the Research & Plan milestone. The best problems have at least two or three plausible but genuinely different metrics that require students to make a value judgment about what they care about.

Good candidate problem domains from CUDA-Q Academic: QAOA for combinatorial optimization (Max-Cut, LABS, portfolio optimization), hybrid quantum-classical neural networks, quantum error correction decoding, and circuit simulation benchmarking. Each has a natural quantum-kernel + classical-GPU-workload decomposition, a clear classical baseline, and multiple plausible success metrics.

The suggested project options (A–E) are listed in "[Choose or provide the project problem](#1-choose-or-provide-the-project-problem)" above.

### Scaling for course constraints

**Shorter timeline (1 week or workshop):** Pre-assign algorithms, skip the brainstorm, provide the resource estimate, and compress M1 + M2 into a single guided session. Students still own M3 and M4.

**Longer timeline (4+ weeks):** Add checkpoints within Milestone 3 — separate the CPU baseline from the GPU optimization, and require a mid-build QA review before optimization begins.

**Solo or pair projects:** The template scales down. A solo student takes the Project Lead and Performance Optimization roles; a pair splits all four roles between them and adjusts deliverables accordingly. The classical benchmarking and retrospective requirements remain regardless of team size. See the extended guidance on individual use cases below.

**Advanced courses:** Require real QPU execution in Milestone 3 and add a noise characterization step before circuit optimization. The QA PIC's benchmark fairness review should explicitly address the comparison between simulated and hardware results.

### Individual and independent use cases

The four-role structure was designed for teams, but the deliverables, milestones, and agent configurations are equally useful for a single student working independently. The role structure becomes a checklist of cognitive modes the student moves through, rather than a division of labor across people.

**Capstone project or senior thesis.** A student working alone takes all four roles sequentially: Project Lead thinking sets the direction and defines success (Milestone 2), Performance Optimization PIC thinking does the implementation (Milestone 3), QA PIC thinking challenges the work adversarially before it is considered done (also Milestone 3), and Technical Marketing PIC thinking produces the final write-up and retrospective (Milestone 4). The individual retrospective becomes a reflection on how the student's thinking shifted across the project — a natural fit for the reflective component most capstone programs require. Suggested timeline: 4–6 weeks with checkpoint meetings at each milestone gate.

**Honors thesis.** Same structure as a capstone, with the addition that Milestone 2 carries more weight: the algorithm selection and success metric definition become the thesis proposal. The classical benchmarking requirement fits naturally with the expectation that an honors thesis engages seriously with the existing literature. The QA PIC's benchmark fairness review maps to the methods section. Adjust the rubric weights to reflect the thesis program's evaluation criteria.

**Independent study or research rotation.** The milestone structure provides external scaffolding for self-directed work — useful for students who need guidance on how to organize a research project, not just what to build. A faculty advisor or research mentor can use the milestone gates as natural check-in points without needing to understand the CUDA-Q implementation details.

**Graduate seminar or reading group project.** Small groups (2–3 students) from a seminar can use the template for a paper implementation project: each student takes one or two roles, the resource estimate and classical benchmark requirement ground the implementation in the paper's claims, and the QA benchmark fairness review becomes a direct engagement with whether the paper's comparisons are valid.

In all individual and small-group cases, the core requirements that should not be dropped are: the written success metric definition with a rejected alternative, the classical benchmark implementation and fairness review, and the individual retrospective. These three are the most transferable elements of the project regardless of context.

---

## Preventing AI Over-Reliance

The "let the agents build the code, you build the architecture" framing contains its own safeguard, but three structural practices reinforce it.

**Require plain-English acceptance criteria before code.** All test acceptance criteria should be written by the student before the agent translates them into code. This ensures students maintain semantic ownership of correctness — they know what the test is supposed to catch before they see the code that catches it.

**Make the retrospective an individual graded deliverable.** Students cannot share a retrospective about their own AI interactions. The role-specific retrospective prompts are in `deliverable-template.md` → "Individual Retrospectives" — each role has its own set of questions tailored to that role's agent and deliverables.

**Add at least one oral explanation requirement.** Design a short check-in where the student explains what the code does without reference to the agent's output. This is the most direct way to surface whether understanding has been transferred or just forwarded.

The "Against Frictionless AI" argument from the education technology literature is relevant here: excessive ease in AI-assisted environments can erode the productive struggle that drives learning. The role structure, milestone checkpoints, and individual retrospective are the friction. They should be preserved, not streamlined away.

---

## Common Instructor Questions

**What if students can't get GPU access in time for Milestone 3?**
The benchmark comparison is still meaningful on CPU simulation. Students document `qpp-cpu` as their backend, note the simulation limit, and report results honestly. The pedagogical goal of the optimization phase is the discipline of before/after measurement and honest comparison — not the GPU numbers themselves.

**What if no team member has CUDA-Q experience?**
That's expected. Milestone 1 is designed to build baseline familiarity before anyone writes project code. The CUDA-Q skill and the Engineering Agent's starter prompts are specifically written for students learning the API as they go.

**What if a team's quantum implementation doesn't outperform classical?**
That is a valid and valuable result. The rubric explicitly rewards honest reporting "regardless of which approach won." Teams that report an honest negative result with well-executed benchmarking should score as well as teams with a positive result. Reinforce this at kickoff.

**Do students need to understand the pedagogical rationale?**
No — the student guide is written to be picked up without background.

---

## Tell Us How You're Using This

This template is actively maintained and shaped by instructor feedback. If you are using or adapting it, we would genuinely like to hear from you — what problem you assigned, what worked, what didn't, what you changed, and what your students produced.

Contact us at **[cuda-quantum-academic@nvidia.com](mailto:cuda-quantum-academic@nvidia.com)**. Useful things to share include:

- The problem or domain you used (especially if it's outside the suggested options)
- How you adapted the roles, milestones, or rubric for your course context
- Results or student work you're willing to share
- Pain points or gaps you encountered that the template didn't address
- Whether you used this for a team course, individual capstone, thesis, or other format

Your adaptations directly inform what gets added or improved. If you've designed a course-specific project option that meets the four criteria above and you're willing to share it, we may include it as a suggested option in a future version (with attribution).

---

*Developed for the [NVIDIA CUDA-Q Academic](https://github.com/NVIDIA/cuda-q-academic) repository. Adaptation and reuse with attribution encouraged.*

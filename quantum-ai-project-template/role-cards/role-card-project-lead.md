# Role Card: Project Lead
*CUDA-Q Academic Group Project*

---

## Your Mission

You are the team's **technical architect**. Your job is to decide *what* the team will build — which algorithm(s), which hybrid workflow, which platforms — and then decompose that into sub-tasks that the team can execute. You do not start decomposing until the team has agreed on the design.

You use AI as a **research and reasoning partner**: to survey the landscape, surface trade-offs, and challenge early assumptions. The agent informs the choice. You make it and own it.

---

## Your Deliverables Checklist

### Milestone 2 — Research & Plan
- [ ] **Algorithm and workflow design document:** which algorithm(s) will be used, why chosen over alternatives, how the hybrid workflow connects classical preprocessing → quantum kernel → post-processing
- [ ] **Definition of success:** chosen metric + written justification + one alternative metric considered and rejected
- [ ] **Problem decomposition:** sub-tasks, owners, and acceptance criteria — produced *after* the workflow is agreed by the team
- [ ] Team has reviewed and signed off on the plan before anyone starts building

### Milestone 3 — Build
- [ ] Milestone check-in notes: what's on track, what's at risk, what decisions were made
- [ ] Any plan changes documented and agreed by the team

### Milestone 4 — Showcase & Retrospective
- [ ] Final repository properly structured, all deliverables present and attributed
- [ ] Confirmed that the retrospective includes individual contributions from every team member

---

## What You Contribute to the Team

- [ ] Facilitate the Milestone 1 kickoff discussion ("what does this algorithm actually do?")
- [ ] Present your algorithm and workflow proposal — listen to the team and revise before locking it in
- [ ] Review every role's deliverables for coherence with the overall design
- [ ] Make sure the showcase's claims are consistent with the resource estimates and benchmark results

---

## Team Repository Setup

Set this up before Milestone 1 — it's a Project Lead responsibility.

**Create and share the repo:**
1. Create a new repository at [github.com](https://github.com) (public or private per your course requirements)
2. Go to **Settings → Collaborators → Add people** and invite each teammate by their GitHub username
3. Each teammate accepts the invitation and clones the repo:
   ```bash
   git clone https://github.com/[your-username]/[repo-name].git
   ```

**Suggested folder structure:**
```
your-repo/
├── README.md                  ← project overview and team roster
├── deliverable-template.md    ← copy from the student template folder
├── plan/                      ← Milestone 2 documents
├── src/                       ← CUDA-Q implementation
├── tests/                     ← QA PIC test suite
└── benchmarks/                ← results and comparison data
```

**Basic team workflow:** each person works on a branch (`git checkout -b yourname/feature`), opens a pull request when ready, and the Project Lead reviews and merges. If your team is new to git, [GitHub's quickstart guide](https://docs.github.com/en/get-started/quickstart) covers everything you need.

---

## Your AI Agent: Orchestrator

### Configure your agent

Use whatever AI coding assistant or chat-based LLM your course provides or your team has access to. **Pick one tool and use it consistently** — switching mid-project creates context gaps. Share your choice with the team at the Milestone 1 kickoff.

**Give your agent CUDA-Q context** before your first session. Paste relevant sections from the [CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) into your system prompt, or point your tool at the docs directly if it supports browsing.

**If your agent environment supports skills**, install the CUDA-Q guide skill so every team member's agent has persistent, accurate API knowledge:

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/NVIDIA/cuda-quantum.git
cd cuda-quantum && git sparse-checkout set .claude/skills/cudaq-guide
cp -r .claude/skills/cudaq-guide ~/.claude/skills/
```

Configure your agent's behavior with the system prompt below. **This is a starting point — edit it to match your specific problem and algorithm before you begin.**

**Agent behavior rule:** When your agent produces a design decision, code structure, or written output you use, note it at the time — your retrospective depends on being able to recall specifically what the agent contributed and what you changed or overrode.

```
You are an Orchestrator agent supporting a quantum computing project lead.
You have detailed knowledge of the CUDA-Q API and the CUDA-Q Academic module catalog.

Your job is to help me think, not to decide for me.

Before I propose any design, help me survey the full landscape of approaches
available in CUDA-Q Academic. Reference specific modules and notebooks by name
when they are relevant to the problem.
When I describe a candidate approach, ask: what would a correct result look like,
and which CUDA-Q backend is appropriate for this scale?
Surface trade-offs between approaches — circuit depth, qubit count, simulator
feasibility vs. real QPU feasibility — don't converge on one prematurely.
Track open design questions and flag dependencies I might be missing.
When I'm ready to decompose work, help me write sub-tasks with clear acceptance criteria.
Never finalize a design decision without confirming I've considered at least one alternative.
The full project structure, milestone definitions, and all team role definitions are in the project guide provided by your instructor.
```

---

## Starter Prompts

**Survey the algorithmic landscape (use when the algorithm is not pre-specified):**
```
I am the Project Lead. Our problem is: [description].
Before we commit to any approach, help me survey the options.
What quantum algorithms are candidates for this problem?
For each, what is the hybrid workflow — how does it connect
classical preprocessing, the quantum kernel, and post-processing?
What are the trade-offs in terms of circuit depth, qubit count,
and expected performance relative to classical approaches?
I will decide which to pursue — help me understand the landscape.
```

**Validate a pre-specified algorithm (use when the algorithm is already given, e.g. Options A–D):**
```
I am the Project Lead. Our project specifies using [algorithm] for [problem].
Rather than surveying alternatives, help me validate this choice:
- Why is this algorithm the right match for this problem?
- What assumptions does it depend on — and could any of them fail at our problem size?
- What does the hybrid workflow look like end-to-end for our specific implementation?
- What would a skeptical reviewer say is the weakest part of this approach?
I want to understand the choice deeply, not just accept it.
```

**Define success metrics:**
```
Our problem is open-ended: [description]. Help me think through
what "success" could mean. What metrics are commonly used? What
are the trade-offs? What would a skeptical reviewer say is wrong
with each? I will decide — I need you to help me reason, not choose.
```

**Decompose work (after the team agrees on the workflow):**
```
We have agreed to use [algorithm/workflow].
Help me decompose this into sub-tasks with clear acceptance criteria.
For each sub-task, identify which role owns it, what inputs it needs
from other sub-tasks, and what the QA PIC will need to verify.
```

---

## Milestone Checklist

### Milestone 1 — Ramp Up
- [ ] Created shared GitHub repository and confirmed all team members have access
- [ ] Team agreed on an AI agent environment; everyone has it set up with their role card system prompt
- [ ] Completed the tutorial notebook individually
- [ ] Facilitated the team kickoff discussion
- [ ] Confirmed that every team member can explain the classical approach the algorithm improves upon

### Milestone 2 — Research & Plan
- [ ] Used Orchestrator to survey or validate the algorithm before proposing to the team
- [ ] Proposed algorithm + workflow to team; team agreed before decomposition began
- [ ] Success metric chosen and alternative documented
- [ ] Resource estimate and classical comparator confirmed with Performance Optimization PIC
- [ ] Decomposition document produced and reviewed by team
- [ ] **Plan sign-off:** the Project Lead, Performance Optimization PIC, and QA PIC have all confirmed in the Plan Sign-off table in `deliverable-template.md` — build does not start until this is complete

### Milestone 3 — Build
- [ ] Check-in notes recorded at each natural milestone boundary
- [ ] Any scope or design changes documented and agreed

### Milestone 4 — Showcase & Retrospective
- [ ] Repository structured and all deliverables present
- [ ] Individual retrospective paragraph submitted

---

## At Every Milestone, Ask Yourself

1. Do I understand what was built well enough to explain it without the agent?
2. Did the agent produce anything I accepted without verifying? Verify it now.
3. What decision in this milestone required human judgment that the agent could not have made?
4. Did I contribute to my teammates' work this milestone, not just my own deliverables?
5. Did the Orchestrator's proposed decomposition or workflow get adopted without being challenged? If so, what would a skeptic have said — and was that objection actually considered?

---

*NVIDIA CUDA-Q Academic · [github.com/NVIDIA/cuda-q-academic](https://github.com/NVIDIA/cuda-q-academic)*

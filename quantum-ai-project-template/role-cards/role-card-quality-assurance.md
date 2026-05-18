# Role Card: Quality Assurance PIC (the Verifier)
*CUDA-Q Academic Group Project*

---

## Your Mission

Your job is to make sure the team's results are real. That means two things: verifying that the code does what the team thinks it does, and verifying that the classical benchmark comparison is fair. AI code is confident, syntactically correct, and voluminous — exactly the properties that suppress the instinct to scrutinize. Your role keeps that instinct alive.

**The benchmark fairness check is one of your most important deliverables.** A quantum result that beats a poorly configured or mismatched classical baseline is not a result at all. You are the one who catches this.

All team members are expected to raise concerns when they spot something wrong. But you are the one with explicit accountability for verification — don't wait for others to find your issues, and don't assume others will find theirs.

---

## Your Deliverables Checklist

### Milestone 1 — Ramp Up
- [ ] **Milestone 1 understanding log** — one paragraph capturing the team's shared understanding of the algorithm and any open assumptions, recorded after the Milestone 1 kickoff discussion (graded)

### Milestone 2 — Research & Plan
- [ ] First acceptance test written in plain English — what does a correct result look like? (Not code yet)

### Milestone 3 — Build
- [ ] **Test suite:**
  - [ ] Nominal case (expected inputs, expected outputs)
  - [ ] Boundary case (edge of valid input range)
  - [ ] At least one adversarial case (inputs designed to break the circuit or violate assumptions)
- [ ] **Benchmark fairness review:** written assessment of whether the classical and quantum implementations are being compared on equal terms:
  - [ ] Same input sizes?
  - [ ] Same metric definitions?
  - [ ] Same hardware constraints where possible?
  - [ ] Is the classical algorithm chosen the right comparator, or is there a stronger one?
- [ ] **Written review of the Performance Optimization PIC's implementation** (one paragraph minimum)
- [ ] Documentation of one assumption challenged and how it was resolved

---

## What You Contribute to the Team

- [ ] Review the Project Lead's plan at Milestone 2 and flag any gaps in the success definition or workflow design
- [ ] Write the first acceptance test before any implementation begins
- [ ] Run adversarial review of code as it develops — don't wait until the build is "done"
- [ ] Flag benchmark fairness issues early enough to fix them, not after results are finalized

---

## Your AI Agent: Adversarial Pair (Gremlin + Fixer)

> **Tip:** If your agent environment supports the `/tdd` skill, use it — it automates the test-first workflow described here and is a strong complement to (or replacement for) the Gremlin+Fixer prompts below. Run `/tdd` before any implementation begins, feed it your plain-English acceptance criteria from Milestone 2, and let it drive the test suite structure. Use the Gremlin prompts for adversarial edge cases and benchmark fairness review that `/tdd` won't cover on its own.

**Give your agent CUDA-Q context** before your first session — paste relevant sections from the [CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) into your system prompt, focusing on circuit behavior, measurement, and backend semantics.

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
You are an Adversarial Pair — two agents working together: a Gremlin and a Fixer.

Gremlin: your job is to find failure modes. For any code, test suite, or benchmark setup
I show you, generate inputs or conditions that could break it, expose hidden assumptions,
or make a comparison unfair. Be adversarial, not helpful.

Fixer: for every failure mode the Gremlin finds, propose a patch or correction.
Do not implement any fix without my explicit approval.

When I ask for a benchmark review, the Gremlin asks: is this a fair comparison?
Is the classical algorithm the right one? Are both sides measured on the same terms?
The Fixer proposes how to correct any unfairness found.

Default to Gremlin mode unless I say otherwise.
The full project structure, milestone definitions, and all team role definitions are in the project guide provided by your instructor.
```

---

## Starter Prompts

**Write the first acceptance test before any code (use at Milestone 2):**
```
I am the QA PIC. No code has been written yet.
Our team plans to solve [problem] using [algorithm/workflow].
The success metric is [metric]. The classical comparator is [algorithm].

Help me write the first acceptance test in plain English — no code.
For each item, give me:
1. A statement of what a correct result looks like
2. A statement of what a wrong result would look like
3. At least one boundary case we should be able to handle
4. At least one assumption in the plan that could be wrong and would invalidate the test

These will become the acceptance criteria that the Performance Optimization PIC
builds against. Make them precise enough to be unambiguous.
```

**Code review:**
```
I am the QA PIC reviewing this implementation: [code].
Act as a Gremlin: what inputs, edge cases, or assumptions could break this?
For each failure mode, also suggest how the Fixer would patch it.
Do not implement any patch without my approval.
```

**Benchmark fairness review:**
```
I am the QA PIC. Our team is comparing our quantum implementation
against this classical solution: [classical description].
Act as a skeptical reviewer: is this a fair comparison?
Is the classical algorithm we chose the right one, or is there
a stronger classical baseline we should be using?
Are we measuring both on the same inputs, the same metric, and
under the same constraints? What would a reviewer say is unfair
about our setup?
```

> **On "quantum advantage":** this term has a precise technical meaning — quantum solves a problem faster or better than the *best possible* classical algorithm, provably and scalably. Showing better performance on one test case at one problem size is *not* quantum advantage; it may be a promising result or a useful quantum benefit on that instance, but it is not the same claim. Flag any use of "quantum advantage" in the showcase or executive summary that doesn't meet this bar. "Our method outperformed the classical baseline at N=[X]" is an honest statement. "We demonstrated quantum advantage" almost certainly is not.

**Writing adversarial test cases:**
```
I am the QA PIC. Here is our implementation: [code] and our current test suite: [tests].
Generate 3 adversarial test cases — inputs specifically designed to expose failure modes
that the existing tests don't cover. For each, explain what assumption it's probing.
```

**CUDA-Q backend consistency check:**
```
I am the QA PIC. Our team ran the quantum implementation on [backend A]
and the classical benchmark on [backend B / CPU].
Are we comparing these fairly? Could the choice of cudaq.set_target()
affect our results in a way that flatters the quantum approach?
What should we control for when reporting the head-to-head comparison?
```

**Shot noise and statistical validity:**
```
I am the QA PIC. Our quantum results used shots_count=[N].
Is this enough shots to make our reported metric statistically meaningful?
How would the result distribution change at shots_count=[N/10] vs [N*10]?
What should the retrospective say about shot budget as a resource cost?
```

---

## Milestone Checklist

### Milestone 1 — Ramp Up
- [ ] Completed the tutorial notebook individually
- [ ] Logged the team's shared understanding after the kickoff discussion, including any open assumptions

### Milestone 2 — Research & Plan
- [ ] Reviewed the Project Lead's plan — flagged any gaps in success definition or workflow design
- [ ] First acceptance test written in plain English and included in the plan
- [ ] **Plan sign-off:** confirmed in the Plan Sign-off table in `deliverable-template.md` that acceptance criteria are clear enough to build against — no code written until the Project Lead, Performance Optimization PIC, and QA PIC have all signed off

### Milestone 3 — Build (Phase 1: CPU baseline)
- [ ] Nominal and boundary test cases written and passing
- [ ] At least one adversarial test case written
- [ ] Initial code review of the Performance Optimization PIC's implementation completed
- [ ] Sign off that CPU baseline tests pass and benchmark setup is fair before Performance Optimization PIC begins GPU optimization phase — record in the QA Pre-Optimization Sign-off table in `deliverable-template.md`

### Milestone 3 — Build (Phase 2: Optimized target)
- [ ] Benchmark fairness review written
- [ ] Adversarial review of final implementation completed
- [ ] One challenged assumption documented and resolved

### Milestone 4 — Showcase & Retrospective
- [ ] Reviewed the showcase for any claims that go beyond what the benchmark results support
- [ ] Individual retrospective paragraph submitted

---

## At Every Milestone, Ask Yourself

1. Do I understand what was built well enough to explain it without the agent?
2. Did the agent produce anything I accepted without verifying? Verify it now.
3. What decision in this milestone required human judgment that the agent could not have made?
4. Did I contribute to my teammates' work this milestone, not just my own deliverables?

---

*NVIDIA CUDA-Q Academic · [github.com/NVIDIA/cuda-q-academic](https://github.com/NVIDIA/cuda-q-academic)*

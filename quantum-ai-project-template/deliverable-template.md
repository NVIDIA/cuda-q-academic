# Project Deliverable Template
*CUDA-Q Academic Group Project*

Fill this in as a team across all four milestones. Each section maps to a milestone gate. Submit the completed document with your final repository.

---

## Team Information

| | |
| :---- | :---- |
| **Team members and roles** | Project Lead: <br> Performance Optimization PIC: <br> QA PIC: <br> Technical Marketing PIC: |
| **Project option** | *(A / B / C / D / E — or title if student-designed)* |
| **Project title** | |
| **Hardware / simulator used** | |

---

## Milestone 2 — Project Plan

*Complete before any implementation begins. **This section ends with a required Plan Sign-off — the Project Lead and the two PICs listed below must all complete the sign-off table before anyone writes code.***

### Problem Statement

> What problem is the team solving? Why is it hard classically?

[Your answer here]

### Algorithm and Workflow Design

> Which quantum algorithm(s) will you use, and why were they chosen over alternatives?
> Describe the end-to-end hybrid workflow: what does each component do and how do they connect?

**Algorithm(s) selected:**

**Why chosen over alternatives:**

**Hybrid workflow description** *(classical preprocessing → quantum kernel → post-processing)*:

### Classical Baseline Specification

> Which classical algorithm will you benchmark against? Why is it the right comparator — not a strawman?
> What results is it known to achieve on this class of problem?

**Classical comparator:**

**Why this is the right benchmark (not a strawman):**

**Known performance of this algorithm:**

### Resource Estimate

> Complete before full implementation. Fill in at the target problem size.

| Resource | Estimate | Scales as |
| :---- | :---- | :---- |
| Qubit count | | |
| Circuit depth | | |
| Gate complexity | | |
| Shot budget | | |

**Is this feasible on your available hardware/simulator?**

> Yes / No / Conditional — explain:

**Assumptions this estimate depends on:**

### Simulator Backend Selection

> Before you build, read the [CUDA-Q backends documentation](https://nvidia.github.io/cuda-quantum/latest/using/backends/backends.html) and the [Simulation 101 notebook](https://github.com/NVIDIA/cuda-q-academic/blob/main/simulation/01_simulation101.ipynb), then decide which backend is appropriate for each phase. Document your choice and the reasoning here — this is a planning decision, not a default.

| Phase | `cudaq.set_target()` value | Why this backend for this phase |
| :---- | :---- | :---- |
| Prototype (M1–early M3) | | |
| Optimized target (M3) | | |

**What is the estimated simulation limit** (maximum qubit count or circuit depth) for your chosen prototype backend at your target problem size?

### Definition of Success

> What metric will you use to evaluate your result? Why? What alternative did you consider and reject?

**Chosen metric:**

**Justification:**

**Alternative metric considered and rejected:**

**Why rejected:**

### Sub-task Breakdown

| Sub-task | Owner | Inputs needed from | Acceptance criteria |
| :---- | :---- | :---- | :---- |
| | | | |
| | | | |
| | | | |
| | | | |

### First Acceptance Test (plain English)

> Describe in plain English — no code — what a correct result looks like. Written by the QA PIC.

[QA PIC's acceptance test here]

### Plan Sign-off (required before any implementation begins)

*The Project Lead, Performance Optimization PIC, and QA PIC each confirm the plan is complete enough to build against. No code is written until this section is filled in.*

| PIC | Confirmed? | Notes / open questions |
| :---- | :---- | :---- |
| **Project Lead** — workflow design is agreed and decomposition is complete | | |
| **Performance Optimization PIC** — resource estimate is done and classical comparator is identified | | |
| **QA PIC** — first acceptance test is written, the success metric is clear enough to test against, and at least one alternative metric has been named and rejected in the Definition of Success section | | |
| **Technical Marketing PIC** — plain-English showcase framing drafted — has a one-paragraph description of the problem and what a successful result would look like for a non-specialist audience | | |

---

## Milestone 3 — Build Results

*Complete during and after the build phase. Ready to proceed when: the results table compares quantum vs. classical on the same inputs and metric.*

### QA Pre-Optimization Sign-off

*Completed by the QA PIC before the Performance Optimization PIC begins GPU optimization.*

| QA PIC sign-off | Confirmed? |
| :---- | :---- |
| CPU baseline tests pass, benchmark comparison is on equal terms, and optimization may begin | |

### Head-to-Head Benchmark Results

> Use the same inputs and the same metric for all three columns.

| | Quantum (unoptimized) | Classical | Quantum (optimized) |
| :---- | :---- | :---- | :---- |
| **[Metric name]** | | | |
| **Problem size tested** | | | |
| **CUDA-Q target / backend** | *(fill in — e.g. `qpp-cpu`)* | n/a | *(fill in — run `[t.name for t in cudaq.get_targets()]` to list what's available on your system)* |
| **Shots used** | | n/a | |
| **Wall-clock time** | | | |
| **Notes** | | | |

### Optimization Summary

> What bottleneck or inefficiency did you address? What strategy did you use? What was the measured result?

**Bottleneck identified:**

**Optimization strategy:**

**Measured result (before vs. after):**

**Honest assessment — where does quantum stand relative to classical at this problem size?**

### QA Benchmark Fairness Review

*Written by the QA PIC.*

> Are the classical and quantum implementations being compared on equal terms?
> Same input sizes, same metric definitions, same hardware constraints where possible?
> Is the classical algorithm the right comparator?

[QA PIC's fairness review here]

### QA Implementation Review

*Written by the QA PIC.*

> One paragraph minimum reviewing the Performance Optimization PIC's implementation.

[QA PIC's implementation review here]

### Challenged Assumption

*Documented by the QA PIC.*

> What assumption did you challenge, and how was it resolved?

**Assumption challenged:**

**How it was resolved:**

---

## Milestone 4 — Showcase & Retrospective

*Complete before the showcase. Ready to proceed when: the retrospective distinguishes between what the AI generated and what the team decided.*

### Executive Summary

*Written by the Technical Marketing PIC. One paragraph.*

> State what was demonstrated, at what scale, with what resource budget, and how it compared to the classical solution. Scope limitations included.

[Executive summary here]

### Individual Retrospectives

*One paragraph per team member. Each person writes their own — do not write these for each other.*

**Project Lead:**

> What did your Orchestrator agent contribute? What did it get wrong or miss? What decisions required human judgment that the agent could not have made?

[Project Lead's retrospective here]

---

**Performance Optimization PIC:**

> What did your Engineering Agent contribute? What did it get wrong or miss? What decisions required human judgment that the agent could not have made?

[Performance Optimization PIC's retrospective here]

---

**QA PIC:**

> What did your Adversarial Pair (Gremlin + Fixer) contribute? What did it get wrong or miss? What verification required human judgment that the agent could not have made?

[QA PIC's retrospective here]

---

**Technical Marketing PIC:**

> What did your Synthesis Agent contribute? What did it get wrong or miss? What communication decisions required human judgment that the agent could not have made?

[Technical Marketing PIC's retrospective here]

---

*NVIDIA CUDA-Q Academic · [github.com/NVIDIA/cuda-q-academic](https://github.com/NVIDIA/cuda-q-academic)*

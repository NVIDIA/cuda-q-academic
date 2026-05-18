# Role Card: Technical Marketing PIC
*CUDA-Q Academic Group Project*

---

## Your Mission

You translate what the team built into something a non-specialist audience can understand and evaluate — without overstating it. Quantum computing is a field where results are frequently oversold. Your job is the opposite: make sure every claim in the showcase is grounded in what was actually demonstrated, at what scale, with what resource budget, and how it compared to the classical solution.

A compelling showcase is one that is honest about scope. "We demonstrated X for problem size N, using Y qubits and Z shots, and our result compared to the classical baseline as follows" is more credible — and more useful to the field — than vague claims of quantum advantage.

You also own the retrospective, which is the team's honest record of what the AI agents contributed versus what required human judgment. This is not a formality. It's one of the most professionally transferable things you'll produce in this project.

---

## Your Deliverables Checklist

### Milestone 4 — Showcase & Retrospective
- [ ] **Showcase presentation** (5–10 minutes, accessible to non-specialists):
  - [ ] States what problem was tackled and why it's hard classically
  - [ ] Explains the quantum approach at a conceptual level
  - [ ] Reports results grounded in the team's resource estimates and benchmark results
  - [ ] Explicitly states what was *not* demonstrated (scope limitations)
  - [ ] Reviewed by the full team for technical accuracy before presenting
- [ ] **Executive summary** (one paragraph): what was demonstrated, at what scale, how it compared to the classical solution
- [ ] **Retrospective document** (individual contributions from every team member): what each AI agent contributed vs. what required human judgment

---

## What You Contribute to the Team

**During Milestones 1–3 (do not wait for M4):**
- [ ] After M1: draft a one-paragraph plain-English description of the problem and algorithm — this becomes the opening of your showcase. Circulate to teammates for accuracy
- [ ] After M2: draft the narrative arc of the showcase (what are we claiming, what would prove it, what would count as failure?) — get it agreed before the build starts so the team knows what story the results need to tell
- [ ] During M3: track the benchmark results as they develop. Flag any claims in team discussions that seem to overstate what the numbers show. Flag any use of "quantum advantage" — see the note below
- [ ] During M3: if results are negative or mixed, begin drafting the "null result" framing early — don't leave it to the last minute

**At Milestone 4:**
- [ ] Review the showcase for hype — flag any claims that go beyond what the benchmark results actually support
- [ ] Coordinate with the Performance Optimization PIC to confirm the resource estimates and benchmark numbers are the final, correct figures
- [ ] Coordinate with the QA PIC to confirm the benchmark comparison framing is fair before presenting
- [ ] Collect individual retrospective paragraphs from each team member — don't write these for them

> **On "quantum advantage":** this term has a specific technical meaning — quantum solves a problem faster or better than the *best possible* classical algorithm, provably and scalably. Showing better results on one benchmark at one problem size is not quantum advantage. It may be a genuine and interesting result, but call it what it is: "our implementation outperformed the classical baseline at N=[X], using Y qubits and Z shots." Flag any draft language that says or implies "quantum advantage" and replace it with a precise description of what was actually demonstrated.

---

## Your AI Agent: Synthesis Agent

**Give your agent CUDA-Q context** before your first session — paste relevant sections from the [CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) into your system prompt, focusing on what backends, shot counts, and target strings actually mean.

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
You are a Synthesis Agent supporting a technical communicator translating quantum computing
results for a non-specialist audience.

Your operating rules:
1. Never state more than the data supports. If I draft a claim, flag it if it goes beyond
   the team's actual results, problem sizes, or resource estimates.
2. When translating technical results, preserve precision — don't round away meaningful caveats.
3. When I ask you to visualize performance data, label axes clearly and include units.
4. For the retrospective, prompt me with: "What did the agent get right? What did it get wrong?
   What did it confidently produce that you had to correct? What did it refuse or fail to do
   that you had to do yourself?"
5. Do not draft the retrospective for me — ask me the questions and help me structure my answer.
The full project structure, milestone definitions, and all team role definitions are in the project guide provided by your instructor.
```

---

## Starter Prompts

**Draft the showcase narrative arc (use at Milestone 2, before build starts):**
```
I am the Technical Marketing PIC. Our team plans to solve [problem]
using [algorithm]. The success metric is [metric]. The classical
comparator is [classical algorithm].

Help me draft the narrative arc for the showcase:
- What claim are we setting out to test?
- What evidence would support it? What would count as a positive result?
- What would a negative or null result look like — and how would we present
  it honestly?
- What is the one thing a non-specialist audience needs to understand about
  our approach before they can evaluate our results?

Do not write the showcase itself — help me plan the story before the results exist.
```

**Executive summary:**
```
I am the Technical Marketing PIC. Here are our results: [results],
our resource estimates: [estimates], and our classical benchmark
comparison: [comparison].
Write a 3-sentence executive summary for someone who understands
optimization but not quantum computing.
Be precise about what we demonstrated: what problem size, what
resource budget, and how our result compared to the classical solution.
Flag any phrasing that overstates what we actually showed.
```

**Hype-check the showcase draft:**
```
Here is a draft of our showcase presentation: [draft].
Act as a skeptical audience member who knows classical computing well.
What claims are we making that go beyond what our results actually support?
Where are we implying more generality or advantage than we demonstrated?
```

**CUDA-Q context for your executive summary:**
```
I am the Technical Marketing PIC. Help me explain the following to a non-specialist:
- What cudaq.set_target('[backend]') means and why it matters for our results
- What shots_count=[N] means and why it's a resource cost, not just a setting
- Why we compared against a classical solution and what that comparison actually shows
Be precise. Flag any phrasing that implies general quantum advantage beyond
what we demonstrated at our specific problem size and backend.
```

**Retrospective prompting:**
```
I am writing my section of the project retrospective about my AI agent.
Ask me the questions I should answer, one at a time, and help me
structure my answers into a coherent paragraph.
Focus on: what the agent contributed, what it got wrong, what I had
to verify or correct, and what decisions it could not make for me.
```

---

## Milestone Checklist

### Milestone 1 — Ramp Up
- [ ] Completed the tutorial notebook individually
- [ ] Can explain what the algorithm does and what the classical approach is that it improves upon
- [ ] Drafted a plain-English description of the problem and shared with teammates for accuracy check

### Milestone 2 — Research & Plan
- [ ] Reviewed the Project Lead's plan — the success metric and classical comparator are clear enough to present to a non-specialist audience
- [ ] Drafted the showcase narrative arc: what are we claiming, what evidence would support it, what would count as a negative result?
- [ ] Confirmed the narrative with the team before build starts

### Milestone 3 — Build
- [ ] Tracked benchmark results as they developed — understand what the numbers mean
- [ ] Flagged any language in team discussions that overstated results or misused "quantum advantage"
- [ ] If results are negative or mixed, begun drafting the null-result framing

### Milestone 4 — Showcase & Retrospective
- [ ] Executive summary written and reviewed by team for accuracy
- [ ] Showcase presentation completed and reviewed by full team before presenting
- [ ] Collected retrospective paragraphs from all team members
- [ ] Individual retrospective paragraph submitted

---

## At Every Milestone, Ask Yourself

1. Do I understand what was built well enough to explain it without the agent?
2. Did the agent produce anything I accepted without verifying? Verify it now.
3. What decision in this milestone required human judgment that the agent could not have made?
4. Did I contribute to my teammates' work this milestone, not just my own deliverables?
5. Did the Synthesis Agent's framing get used without checking whether it overclaimed results or softened caveats? Re-read the agent's draft against the actual benchmark numbers — does every claim survive that comparison?

---

*NVIDIA CUDA-Q Academic · [github.com/NVIDIA/cuda-q-academic](https://github.com/NVIDIA/cuda-q-academic)*

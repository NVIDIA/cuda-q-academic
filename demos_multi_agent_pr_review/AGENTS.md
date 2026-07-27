# Paper-to-PR Title Workflow

This repository defines a workshop exercise where three specialized agents collaborate to turn a scientific paper into one press-style PR title.

The goal is convergence: start with tension between accurate-but-dull scientific language and catchy-but-potentially-hyped marketing language, then iterate toward a final title that is both scientifically faithful and bold enough for public communication.

The main chat agent acts as the quiet workflow runner. It keeps the workflow moving, records the dialogue, preserves context boundaries, sends the title to one reviewer at a time, and writes the final Markdown report. It does not need to appear as a character in the demo conversation.

## Agents

- PR Writer Agent: drafts and revises one press-style PR title. The PR Writer begins underinformed and never receives the full paper.
- Scientist Agent: reads the full paper and protects scientific accuracy. The Scientist is intentionally prone to accurate but dull technical language.
- Marketer Agent: reads the full paper and pushes for strong public language. The Marketer is intentionally prone to catchy but potentially exaggerated claims and treats adding a statistic or number to the title as non-negotiable.

## Required Inputs

- A paper PDF or extracted paper text supplied by the facilitator.
- A paper title.
- Optional target audience.
- Optional institution or outlet style.
- A run directory, usually `runs/<run_id>/`.

## Workflow Order

1. The workflow runner gives the paper title, optional target audience, and optional style context to the PR Writer Agent.
2. The PR Writer Agent creates the initial PR title.
3. The workflow runner sends the current title to the Scientist Agent.
4. If the Scientist rejects, the workflow runner sends only Scientist feedback to the PR Writer. Repeat Scientist review and PR revision until the Scientist approves.
5. After the Scientist approves, the workflow runner sends the current title to the Marketer Agent.
6. If the Marketer rejects, the workflow runner sends only Marketer feedback to the PR Writer. Repeat Marketer review and PR revision until the Marketer approves.
7. After the Marketer approves, the workflow runner sends the current title back to the Scientist Agent for a final accuracy check.
8. If the Scientist rejects after the Marketer changes, repeat Scientist review and PR revision until the Scientist approves, then return to the Marketer because the title changed again.
9. Stop only when the current title has approvals from both reviewers with no PR revision between those approvals.

## Round Limit

Default to ten PR Writer versions unless the human facilitator sets a different limit.

## One-Influencer Loop Rule

Only one reviewer influences the PR Writer at a time.

- During the Scientist phase, the PR Writer receives only Scientist feedback.
- During the Marketer phase, the PR Writer receives only Marketer feedback.
- After a Marketer-approved title changes, the Scientist must recheck it.
- If a Scientist-required fix changes a Marketer-approved title, the Marketer approval becomes stale and the Marketer must recheck it.
- The PR Writer must keep a `memory` list of prior reviewer comments and must not reintroduce the exact same mistake in later revisions.

## Statistic Pressure Rule

The Marketer must push to include a statistic or number in the title.

- The Marketer should treat a number as non-negotiable for appeal.
- The Marketer may initially use the statistic imprecisely or hype it too much.
- The PR Writer may use the statistic only if it does not violate memory or active reviewer feedback.
- The Scientist must check whether the statistic is sourced, framed, and labeled accurately.
- If a number is misleading as a percent, score, benchmark, or general accuracy claim, the Scientist must require a more precise title.

## Science-First Rule

Scientific accuracy always wins in the review order.

- The Marketer does not see or influence the title until the Scientist has approved a scientifically safe version.
- The Marketer may propose hyped language, but if that language later fails the Scientist recheck, the PR Writer must correct it before the workflow can finish.
- The final title should retain as much public appeal as possible while passing the Scientist's accuracy standard.

## Approval Condition

The workflow is complete only when the current title has both:

```yaml
scientist.approval: true
marketer.approval: true
```

Those approvals must apply to the same current title. If the PR Writer changes the title after either approval, that approval is stale and must be refreshed.

## Dialogue and Artifacts

The workflow runner must maintain these files:

- `runs/<run_id>/dialogue.jsonl`
- `runs/<run_id>/rounds/pr_writer_round_XX.yaml`
- `runs/<run_id>/rounds/scientist_round_XX.yaml`
- `runs/<run_id>/rounds/marketer_round_XX.yaml`
- `runs/<run_id>/final_report.md`

## Runner Rules

- Do not give the PR Writer Agent the full paper.
- Do not let the PR Writer Agent claim it read the paper.
- Do not ask the PR Writer Agent to invent paper-specific details.
- Do not ask the PR Writer Agent to combine Scientist and Marketer feedback in the same revision.
- Do not ask the Scientist Agent to make marketing or public-interest decisions.
- Do not ask the Marketer Agent to decide whether a scientific claim is true.
- Treat the Scientist Agent as the final authority on accuracy and misinterpretation risk.
- Treat the Marketer Agent as the final authority on appeal, readability, and audience interest, except where it conflicts with science.
- Preserve every round artifact. Never overwrite numbered round files.
- Record title changes explicitly as `old_title`, `new_title`, and `highlighted_title`.
- In `highlighted_title`, wrap only changed title words in Markdown bold markers.
- Final report must use `agents/final_report_template.md` as its structure.
- Final report must be plain Markdown, not HTML.
- Final report must include the full agent iteration record first.
- Final report must show the phase order and every PR title version individually.
- Final report must include the current full title every round, with changed title words highlighted in the new title.
- Final report must include the PR Writer memory so viewers can see prior mistakes are not repeated.

## Launch Prompt

Use this prompt in an agent chat to begin a run. The workflow is agent-driven; do not launch it through a script.

```text
Read AGENTS.md and run the Paper-to-PR Title Workflow.

Paper: papers/<paper_file>.pdf
Paper title: <paper title>
Run directory: runs/<run_id>/
Round limit: 10
Target audience: <optional audience>
Institution or outlet style: <optional style>

Create one press-style PR title.
Keep all intermediate YAML outputs and write the final Markdown report.
```

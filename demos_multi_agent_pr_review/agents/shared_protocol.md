# Shared Multi-Agent Protocol

## Task

The agents collaborate to turn a research paper into one press-style PR title.

The target is convergence: a title that keeps the Scientist's accuracy while retaining the Marketer's bold public hook and required statistic.

## Information Design

- PR Writer sees only the paper title in round 1.
- Scientist reads the full paper.
- Marketer reads the full paper.
- PR Writer revises using one active reviewer at a time, not direct paper access.
- PR Writer keeps a memory of prior reviewer comments so old mistakes are not reintroduced.

## Agent Tension

- Scientist tendency: accurate, cautious, specific, sometimes too technical or dull.
- Marketer tendency: vivid, catchy, accessible, statistic-driven, sometimes too hyped or broad.
- PR Writer goal: move one step at a time toward a title that is accurate, bold, and uses any statistic safely.

## Phase Structure

1. Scientist phase: Scientist reviews, PR Writer revises from Scientist only, repeat until Scientist approves.
2. Marketer phase: Marketer reviews, PR Writer revises from Marketer only, repeat until Marketer approves.
3. Scientist recheck phase: Scientist reviews the marketer-shaped title and statistic.
4. If the title changes in any phase, any older approval from the other reviewer becomes stale.
5. Stop only when both reviewers approve the same current title.

## Memory Rule

Each PR Writer output must include a `memory` list.

- Add important reviewer constraints to memory.
- Preserve memory across revisions.
- Do not reintroduce a phrase, statistic framing, or claim that memory marks as unsafe, dull, or already corrected.
- If a reviewer asks for a change that conflicts with memory, explain the conflict in `revision_notes`.

## Report Requirements

Save a Markdown report using `agents/final_report_template.md` as the structure.

The report should include:

- Paper title
- Run metadata
- Source availability note, including whether an arXiv source was found
- Full agent iteration record
- Final approval status and final approved title
- Title evolution table
- PR Writer memory log
- Science-marketing tension log
- Artifact index

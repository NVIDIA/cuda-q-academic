# Paper-to-PR Title Report

Run: `{{run_id}}`
Paper: {{paper_title}}
Target audience: {{target_audience}}
Style: {{style_context}}
Round limit: {{round_limit}}
Status: {{approval_status}}

## Source Availability

{{source_availability}}

## Final Approved Title

{{final_title}}

## Agent Iteration Record

Show the real workflow first: PR Writer draft, active reviewer feedback, PR Writer memory, revised title, approval state.

## Title Evolution

| Version | Active Reviewer | Previous Title | New Title | Changed Words | Memory Used |
| --- | --- | --- | --- | --- | --- |
| {{version}} | {{active_reviewer}} | {{old_title}} | {{new_title}} | {{changed_words}} | {{memory_used}} |

## PR Writer Memory Log

| Point Added | Memory Item | Why It Matters |
| --- | --- | --- |
| {{point_added}} | {{memory_item}} | {{why_it_matters}} |

## Science-Marketing Tension Log

| Moment | Marketer Pull | Scientist Boundary | Resolution |
| --- | --- | --- | --- |
| {{moment}} | {{marketer_pull}} | {{scientist_boundary}} | {{resolution}} |

## Artifact Index

| Artifact | Purpose |
| --- | --- |
| `dialogue.jsonl` | Machine-readable turn log |
| `rounds/pr_writer_round_XX.yaml` | PR title versions and memory |
| `rounds/scientist_round_XX.yaml` | Accuracy reviews |
| `rounds/marketer_round_XX.yaml` | Appeal reviews and statistic pressure |

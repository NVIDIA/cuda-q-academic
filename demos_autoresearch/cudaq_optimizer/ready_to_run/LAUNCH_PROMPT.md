# Launch prompt

```text
Run the complete two-agent study from this directory.

Read AGENTS.md completely before acting. Use one persistent Explorer proposal
subagent for even rounds 2–20 and one persistent Improver for odd rounds 3–19.
Subagents propose one round at a time and never evaluate; the coordinator alone
edits and runs evaluations.

Run exactly 20 rounds of qaoa_depth15. Round 1 must use the untouched COBYLA
baseline. Every round begins from the fixed seeded 30-parameter vector.

Each round has a hard budget of 300 counted cudaq.observe calls, including the
fixed initial evaluation as call 1. The evaluator must stop before call 301 and
score the best completed observation. Accepted-energy convergence may stop a
round early. Energy is primary; values within 1e-6 use convergence or early
completion, then elapsed time, fewer calls, and earlier round as tie-breakers.

Edit only research/qaoa_depth15/optimizer.py during research. Use only
results.tsv as benchmark-result evidence. Do not inspect traces, logs,
benchmark internals, references, tests, or earlier studies while proposing.

After round 20, restore the winning optimizer source without another
evaluation, write insights.md and figure_summary.txt, run summary and plot
generation, and pass verify_study.py --complete.
```

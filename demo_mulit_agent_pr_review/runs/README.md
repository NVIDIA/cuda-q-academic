# Runs

Each workflow run gets its own folder.

Recommended shape:

```text
runs/<run_id>/
  dialogue.jsonl
  final_report.md
  rounds/
    pr_writer_round_01.yaml
    scientist_round_01.yaml
    marketer_round_XX.yaml
```

The completed example is `runs/alphafold/`.

The report should show the approved title, every intermediate title, reviewer decisions, title changes, PR Writer memory, and the main science-marketing tension.

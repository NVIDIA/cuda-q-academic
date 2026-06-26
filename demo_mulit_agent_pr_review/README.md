# Paper-to-PR Title Exercise

This folder contains a small multi-agent workshop exercise. Three agents turn a scientific paper into one press-style PR title:

- `PR Writer`: drafts and revises the title.
- `Scientist`: protects accuracy and catches overclaims.
- `Marketer`: pushes for a stronger public-facing title and a concrete statistic.

The workflow is intentionally sequential. The PR Writer works with one reviewer at a time: Scientist first, then Marketer, then Scientist again if the Marketer-shaped title changes the science.

## View The Finished Example

The completed AlphaFold example is in:

```text
runs/alphafold/
```

Start with the report:

```text
runs/alphafold/final_report.md
```

The supporting artifacts are also kept:

- `dialogue.jsonl`: turn-by-turn workflow log
- `rounds/pr_writer_round_XX.yaml`: title drafts and PR Writer memory
- `rounds/scientist_round_XX.yaml`: accuracy reviews
- `rounds/marketer_round_XX.yaml`: appeal reviews and statistic pressure
- `papers/alphafold_2021_source_notes.md`: source notes for the AlphaFold paper

## Run Your Own Paper

1. Add your paper to `papers/`, or be ready to paste the paper text into the chat.
2. Pick a new run name, such as `my_paper_run`.
3. Create a matching run folder with a `rounds/` subfolder.
4. Start an agent chat from this folder and paste this prompt:

```text
Read AGENTS.md and run the Paper-to-PR Title Workflow.

Paper: papers/<your_paper_file>.pdf
Paper title: <paper title>
Run directory: runs/<your_run_name>/
Round limit: 10
Target audience: general science readers
Institution or outlet style: plain press office copy

Create one press-style PR title.
Keep all intermediate YAML outputs and write the final Markdown report.
```

If you paste paper text instead of using a PDF, replace the `Paper:` line with:

```text
Paper text: <paste or attach the paper text here>
```

## Files To Know

- `AGENTS.md`: main workflow instructions for the runner agent
- `agents/pr_writer/AGENTS.md`: PR Writer instructions
- `agents/scientist/AGENTS.md`: Scientist instructions
- `agents/marketer/AGENTS.md`: Marketer instructions
- `agents/shared_protocol.md`: shared rules for the three-agent workflow
- `agents/final_report_template.md`: report structure for new runs

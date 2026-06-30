# QEC Autoresearch Examples

This directory contains two self-contained versions of the CUDA-Q QEC
autoresearch exercise.

- [`completed_qec_autoresearch/`](completed_qec_autoresearch/) preserves a
  complete 15-round run so you can inspect its hypotheses, ledger, plots, and
  final decoder.
- [`ready_to_run_qec_autoresearch/`](ready_to_run_qec_autoresearch/) starts
  from the baseline decoder with empty notes and output, ready for a new run.

Enter the variant you want, start Codex there, and prompt:

```text
Read AGENTS.md and run autoresearch for N iterations.
```

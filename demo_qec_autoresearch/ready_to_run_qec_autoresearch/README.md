# QEC Autoresearch Exercise

This is a lean CUDA-Q QEC autoresearch exercise for improving a QLDPC decoder.
Start Codex from this directory and ask it to read `AGENTS.md` and run a chosen
number of autoresearch iterations.

The workflow is inspired by Andrej Karpathy's
[autoresearch](https://github.com/karpathy/autoresearch) repo: keep the harness
fixed, let the agent iterate on the research idea, and judge progress from
repeatable experiment output.

## Run With Codex

Start Codex from this exercise directory, then prompt the agent:

```text
Read AGENTS.md and run autoresearch for 5 iterations.
```

Replace `5` with the number of iterations you want. The agent uses `AGENTS.md`
as the control prompt, edits the decoder, runs the evaluator, and records
results in `output/`.

## Folder Layout

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | The full agent prompt and research protocol. |
| `decoders/qldpc_agent/decoder.py` | The editable decoder and main research target. |
| `decoders/qldpc_agent/NOTES.md` | The run log updated after each iteration. |
| `output/` | May be empty or may contain datasets, ledger rows, and plots from prior rounds. |
| `scripts/` | Fixed dataset, scoring, round-running, and plotting harness. |
| `docs/QLDPC_DECODER_SUMMARY.md` | Reference notes for decoder options and tuning knobs. |

If `output/` already contains a ledger, new rounds continue from that history;
otherwise the first round creates it.

There is no separate `autorun.md` or `AUTORESEARCH.md`; those instructions are
consolidated into `AGENTS.md`.

## Evaluator

Run one logical-error-rate iteration with:

```bash
python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30
```

When datasets are missing, the scripts download the five default CUDA-QX QLDPC
datasets into `output/data/`. Results are appended to:

- `output/ledger/experiments.jsonl`
- `output/plots/round_NNN.png`

Plots use `Autoresearch rounds` as the x-axis label. If any dataset exceeds the
decode-time cap, the entire round is omitted from numeric plot series and its
round column is marked as a cap violation.

To optimize decode time instead, provide an LER cap:

```bash
python scripts/run_round.py --rounds 1 --objective decode_time --ler-cap 0.25
```

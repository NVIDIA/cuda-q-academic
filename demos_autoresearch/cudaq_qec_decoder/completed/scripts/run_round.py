from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from decode_and_score import append_records, evaluate_dataset, load_records
from plot_ledger import plot_ledger
from qldpc_data import default_dataset_paths, ensure_default_datasets


ROOT = Path(__file__).resolve().parents[1]
QLDPC_LANE = "qldpc_agent"
QLDPC_DECODER = ROOT / "decoders" / QLDPC_LANE / "decoder.py"


def _run_decoder(
    dataset_path: str | Path,
    round_index: int,
    time_cap_seconds: float,
    decoder_path: str | Path,
    objective: str,
    ler_cap: float,
) -> dict[str, Any]:
    return evaluate_dataset(
        dataset_path=dataset_path,
        decoder_path=decoder_path,
        lane=QLDPC_LANE,
        round_index=round_index,
        time_cap_seconds=time_cap_seconds,
        objective=objective,
        ler_cap=ler_cap,
    )


def annotate_worst_case(records: list[dict[str, Any]], objective: str) -> list[dict[str, Any]]:
    if not records:
        return []
    worst_record = max(records, key=lambda record: float(record["score"]))
    round_status = "pass" if all(record["status"] == "pass" for record in records) else "fail"
    round_score = float(worst_record["score"])
    round_worst_ler = max(float(record["ler"]) for record in records)
    round_worst_decode_seconds = max(float(record["decode_seconds"]) for record in records)
    annotated: list[dict[str, Any]] = []
    for record in records:
        item = dict(record)
        item["round_status"] = round_status
        item["round_score"] = round_score
        item["round_worst_dataset"] = worst_record["dataset"]
        item["round_worst_ler"] = round_worst_ler
        item["round_worst_decode_seconds"] = round_worst_decode_seconds
        item["round_dataset_count"] = len(records)
        item["objective"] = objective
        annotated.append(item)
    return annotated


def run_one_round(
    *,
    round_index: int,
    time_cap_seconds: float,
    dataset_paths: list[str | Path],
    decoder_path: str | Path = QLDPC_DECODER,
    ledger_path: str | Path,
    plots_dir: str | Path,
    objective: str = "ler",
    ler_cap: float = 1.0,
) -> list[dict[str, Any]]:
    records = [
        _run_decoder(
            dataset_path=dataset_path,
            round_index=round_index,
            time_cap_seconds=time_cap_seconds,
            decoder_path=decoder_path,
            objective=objective,
            ler_cap=ler_cap,
        )
        for dataset_path in dataset_paths
    ]
    records = annotate_worst_case(records, objective)
    append_records(ledger_path, records)
    plot_ledger(ledger_path=ledger_path, plots_dir=plots_dir, round_index=round_index)
    return records


def next_round_index(ledger_path: str | Path) -> int:
    records = load_records(ledger_path)
    return max([int(record.get("round", 0)) for record in records] + [0]) + 1


def run_rounds(
    *,
    rounds: int,
    time_cap_seconds: float,
    dataset_paths: list[str | Path],
    decoder_path: str | Path = QLDPC_DECODER,
    ledger_path: str | Path,
    plots_dir: str | Path,
    objective: str = "ler",
    ler_cap: float = 1.0,
) -> None:
    start_round = next_round_index(ledger_path)
    for round_index in range(start_round, start_round + rounds):
        run_one_round(
            round_index=round_index,
            time_cap_seconds=time_cap_seconds,
            dataset_paths=dataset_paths,
            decoder_path=decoder_path,
            ledger_path=ledger_path,
            plots_dir=plots_dir,
            objective=objective,
            ler_cap=ler_cap,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QEC autoresearch rounds.")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--objective", choices=("ler", "decode_time"), default="ler")
    parser.add_argument("--time-cap-seconds", type=float, default=30.0)
    parser.add_argument("--ler-cap", type=float, default=1.0)
    parser.add_argument("--datasets", type=Path, nargs="*")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "output" / "data")
    parser.add_argument("--decoder", type=Path, default=QLDPC_DECODER)
    parser.add_argument("--no-download-missing", action="store_true")
    parser.add_argument("--ledger", type=Path, default=ROOT / "output" / "ledger" / "experiments.jsonl")
    parser.add_argument("--plots-dir", type=Path, default=ROOT / "output" / "plots")
    args = parser.parse_args()
    dataset_paths = args.datasets
    if not dataset_paths:
        if args.no_download_missing:
            dataset_paths = default_dataset_paths(args.data_dir)
        else:
            dataset_paths = ensure_default_datasets(args.data_dir)
    run_rounds(
        rounds=args.rounds,
        time_cap_seconds=args.time_cap_seconds,
        dataset_paths=dataset_paths,
        decoder_path=args.decoder,
        ledger_path=args.ledger,
        plots_dir=args.plots_dir,
        objective=args.objective,
        ler_cap=args.ler_cap,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

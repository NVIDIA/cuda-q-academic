from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DATASET_COLORS = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
)


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PlotData:
    datasets: list[str]
    plot_rounds: list[int]
    all_rounds: list[int]
    ler_points: list[tuple[int, float, str]]
    decode_time_points: list[tuple[int, float, str]]
    round_score_points: list[tuple[int, float]]
    excluded_rounds: list[int]
    excluded_labels: dict[int, str]


def load_records(path: str | Path) -> list[dict[str, Any]]:
    ledger = Path(path)
    if not ledger.exists():
        return []
    return [
        json.loads(line)
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _cap_label(records: list[dict[str, Any]]) -> str:
    caps = {
        float(record.get("time_cap_seconds", 30.0))
        for record in records
        if record.get("time_cap_seconds") is not None
    }
    cap = min(caps) if caps else 30.0
    return f"{cap:g}s cap violated"


def _violates_time_cap(record: dict[str, Any]) -> bool:
    cap = float(record.get("time_cap_seconds", 30.0))
    failure_reason = str(record.get("failure_reason", ""))
    return float(record.get("decode_seconds", 0.0)) > cap or "decode_timeout" in failure_reason


def prepare_plot_data(records: list[dict[str, Any]]) -> PlotData:
    datasets = sorted({str(record["dataset"]) for record in records})
    records_by_round: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        records_by_round.setdefault(int(record["round"]), []).append(record)

    excluded_labels = {
        round_id: _cap_label(round_records)
        for round_id, round_records in records_by_round.items()
        if any(_violates_time_cap(record) for record in round_records)
    }
    excluded_rounds = sorted(excluded_labels)
    excluded_set = set(excluded_rounds)
    plotted_records = [
        record for record in records if int(record["round"]) not in excluded_set
    ]

    round_score_points: list[tuple[int, float]] = []
    for round_id in sorted(records_by_round):
        if round_id in excluded_set:
            continue
        round_records = records_by_round[round_id]
        round_score_points.append((round_id, float(round_records[-1].get("round_score", 0.0))))

    return PlotData(
        datasets=datasets,
        plot_rounds=sorted({int(record["round"]) for record in plotted_records}),
        all_rounds=sorted(records_by_round),
        ler_points=[
            (int(record["round"]), float(record["ler"]), str(record["dataset"]))
            for record in plotted_records
        ],
        decode_time_points=[
            (int(record["round"]), float(record["decode_seconds"]), str(record["dataset"]))
            for record in plotted_records
        ],
        round_score_points=round_score_points,
        excluded_rounds=excluded_rounds,
        excluded_labels=excluded_labels,
    )


def _label_excluded_rounds(axes: Any, plot_data: PlotData) -> None:
    for axis in axes:
        for round_id in plot_data.excluded_rounds:
            axis.axvspan(round_id - 0.35, round_id + 0.35, color="#f4b6b6", alpha=0.25, zorder=0)
            axis.axvline(round_id, color="#b94a48", linestyle="--", linewidth=0.9, alpha=0.75)
            axis.text(
                round_id,
                0.98,
                plot_data.excluded_labels[round_id],
                transform=axis.get_xaxis_transform(),
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="#8a2d2b",
            )


def _plot_round_scores(axis: Any, points: list[tuple[int, float]]) -> None:
    if not points:
        return
    current_xs: list[int] = []
    current_ys: list[float] = []
    previous_round: int | None = None
    for round_id, score in points:
        if previous_round is not None and round_id != previous_round + 1:
            axis.plot(current_xs, current_ys, marker="o", color="#111111")
            current_xs = []
            current_ys = []
        current_xs.append(round_id)
        current_ys.append(score)
        previous_round = round_id
    if current_xs:
        axis.plot(current_xs, current_ys, marker="o", color="#111111")


def plot_ledger(
    *,
    ledger_path: str | Path,
    plots_dir: str | Path,
    round_index: int,
) -> Path:
    records = load_records(ledger_path)
    output = Path(plots_dir) / f"round_{round_index:03d}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        mpl_config = Path(os.environ.get("TMPDIR", "/tmp")) / "qec_autoresearch_matplotlib"
        mpl_config.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))
        import matplotlib.pyplot as plt
    except ImportError:
        output.write_text("matplotlib unavailable\n", encoding="utf-8")
        return output
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    if records:
        plot_data = prepare_plot_data(records)
        color_by_dataset = {
            dataset: DATASET_COLORS[index % len(DATASET_COLORS)]
            for index, dataset in enumerate(plot_data.datasets)
        }
        xs = [round_id for round_id, _, _ in plot_data.ler_points]
        lers = [ler for _, ler, _ in plot_data.ler_points]
        colors = [color_by_dataset.get(dataset, "#555555") for _, _, dataset in plot_data.ler_points]
        axes[0].scatter(xs, lers, c=colors)
        xs = [round_id for round_id, _, _ in plot_data.decode_time_points]
        times = [decode_time for _, decode_time, _ in plot_data.decode_time_points]
        colors = [
            color_by_dataset.get(dataset, "#555555")
            for _, _, dataset in plot_data.decode_time_points
        ]
        axes[1].scatter(xs, times, c=colors)
        _plot_round_scores(axes[2], plot_data.round_score_points)
        _label_excluded_rounds(axes, plot_data)
        for dataset, color in color_by_dataset.items():
            axes[0].scatter([], [], c=color, label=dataset)
        axes[0].legend(fontsize=7, loc="best")
        if plot_data.all_rounds:
            for axis in axes:
                axis.set_xticks(plot_data.all_rounds)
                axis.set_xlim(min(plot_data.all_rounds) - 0.6, max(plot_data.all_rounds) + 0.6)
    axes[0].set_title("Logical Error Rate")
    axes[0].set_xlabel("Autoresearch rounds")
    axes[0].set_ylabel("LER")
    axes[0].set_ylim(bottom=0)
    axes[1].set_title("Decode Time")
    axes[1].set_xlabel("Autoresearch rounds")
    axes[1].set_ylabel("Seconds")
    axes[1].set_ylim(bottom=0)
    axes[2].set_title("Worst-Case Round Score")
    axes[2].set_xlabel("Autoresearch rounds")
    axes[2].set_ylabel("Score")
    axes[2].set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(output, dpi=140)
    plt.close(fig)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot the QEC autoresearch ledger.")
    parser.add_argument("--ledger", type=Path, default=ROOT / "output" / "ledger" / "experiments.jsonl")
    parser.add_argument("--plots-dir", type=Path, default=ROOT / "output" / "plots")
    parser.add_argument("--round", type=int, default=1)
    args = parser.parse_args()
    print(plot_ledger(ledger_path=args.ledger, plots_dir=args.plots_dir, round_index=args.round))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

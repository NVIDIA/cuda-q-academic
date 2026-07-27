"""Plot each independent search with its own settings and findings."""

import csv
import os
from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter


CIRCUITS = {
    "nonlocal": "Nonlocal layers",
    "controlled": "Controlled gates",
}
COLORS = {
    "baseline": "#457b9d",
    "improvement": "#2a9d8f",
    "worse": "#d1495b",
}
SETTING_LABELS = {
    "precision": "Precision",
    "controlled_rank": "Controlled rank",
    "path_reuse": "Path reuse",
    "hyper_samples": "Hyper samples",
    "find_threads": "Find threads",
    "find_limit": "Find limit",
    "deterministic": "Deterministic",
    "scratch_percentage": "Scratch",
}


def read_rows(circuit):
    path = ROOT / "research" / circuit / "results.tsv"
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def complete_rows(rows):
    return [
        row
        for row in rows
        if row["valid"] == "yes"
        and row["runtime_s"]
        and row["status"] not in {"crash", "timeout"}
    ]


def best_row(rows):
    complete = complete_rows(rows)
    if not complete:
        return None
    return min(complete, key=lambda row: float(row["runtime_s"]))


def improvement_events(rows):
    events = []
    best = None
    for row in rows:
        if row["valid"] != "yes" or not row["runtime_s"]:
            continue
        runtime = float(row["runtime_s"])
        if best is not None and runtime < best:
            events.append(
                {
                    "round": int(row["round"]),
                    "change": row["change"],
                    "ratio": best / runtime,
                    "old": best,
                    "new": runtime,
                }
            )
        best = runtime if best is None else min(best, runtime)
    return sorted(events, key=lambda event: event["ratio"], reverse=True)


def display_setting(name, value):
    if name == "precision":
        return value.upper()
    if name in {"path_reuse", "find_limit", "deterministic"}:
        return "On" if value == "True" else "Off"
    if name == "scratch_percentage":
        return f"{value}%"
    return value


def research_summary(circuit, rows):
    complete = complete_rows(rows)
    if not complete:
        return "No valid research round has been recorded yet."
    baseline = complete[0]
    winner = best_row(rows)
    baseline_time = float(baseline["runtime_s"])
    best_time = float(winner["runtime_s"])
    timeout_count = sum(row["status"] == "timeout" for row in rows)
    timeout_text = (
        f"{timeout_count} timeout{'s' if timeout_count != 1 else ''}."
        if timeout_count
        else "No timeouts."
    )
    outcome = (
        f"Round {winner['round']} was fastest at {best_time:.3f}s: "
        f"{baseline_time / best_time:.2f}x faster than the "
        f"{baseline_time:.3f}s {baseline['precision'].upper()} baseline. "
        f"{len(complete)} of {len(rows)} rounds were valid. {timeout_text}"
    )
    summary_path = ROOT / "research" / circuit / "figure_summary.txt"
    if not summary_path.exists():
        return outcome
    authored_summary = " ".join(summary_path.read_text().split())
    return f"{outcome} {authored_summary}"


def add_runtime_plot(axis, title, rows):
    complete = complete_rows(rows)
    log_scale = False
    if complete:
        rounds = [int(row["round"]) for row in complete]
        runtimes = [float(row["runtime_s"]) for row in complete]
        point_colors = []
        for row in complete:
            if int(row["round"]) == 1:
                point_colors.append(COLORS["baseline"])
            elif row["status"] == "keep":
                point_colors.append(COLORS["improvement"])
            else:
                point_colors.append(COLORS["worse"])
        axis.plot(
            rounds,
            runtimes,
            color="#9aa0a6",
            linewidth=1.4,
            alpha=0.7,
            zorder=1,
        )
        axis.scatter(
            rounds,
            runtimes,
            c=point_colors,
            edgecolors="#333333",
            linewidths=0.45,
            s=42,
            zorder=2,
        )
        if max(runtimes) / min(runtimes) >= 8:
            log_scale = True
            axis.set_yscale("log")
            axis.yaxis.set_major_formatter(ScalarFormatter())

    timeouts = [row for row in rows if row["status"] == "timeout"]
    if timeouts:
        timeout_height = (
            max(float(row["runtime_s"]) for row in complete) * 1.08
            if complete
            else 1.0
        )
        axis.scatter(
            [int(row["round"]) for row in timeouts],
            [timeout_height for _ in timeouts],
            marker="x",
            color=COLORS["worse"],
            s=65,
            linewidths=2,
            zorder=3,
        )
        for row in timeouts:
            axis.annotate(
                f"{float(row['wall_s']):.0f}s timeout",
                (int(row["round"]), timeout_height),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                color=COLORS["worse"],
                fontsize=8,
            )

    axis.set(
        title=title + (" (log y)" if log_scale else ""),
        xlabel="Independent research round",
        ylabel="CUDA-Q observe time (seconds)",
    )
    if rows:
        last_round = max(int(row["round"]) for row in rows)
        ticks = sorted(set([1, last_round] + list(range(5, last_round + 1, 5))))
        axis.set_xticks(ticks)
    axis.grid(alpha=0.22)
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["baseline"],
            markeredgecolor="#333333",
            label="baseline",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["improvement"],
            markeredgecolor="#333333",
            label="new best",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["worse"],
            markeredgecolor="#333333",
            label="worse",
        ),
    ]
    if timeouts:
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker="x",
                color=COLORS["worse"],
                linestyle="none",
                markeredgewidth=2,
                label="timeout",
            )
        )
    axis.legend(handles=legend_handles, loc="best", fontsize=9)


def add_settings_table(axis, rows):
    axis.axis("off")
    axis.set_title("Best observed settings", fontsize=13, fontweight="bold", pad=8)
    winner = best_row(rows)
    if winner is None:
        axis.text(
            0.5,
            0.5,
            "No valid settings recorded yet.",
            ha="center",
            va="center",
        )
        return

    table_rows = [
        [label, display_setting(name, winner[name])]
        for name, label in SETTING_LABELS.items()
    ]
    table_rows.extend(
        [
            ["Best runtime", f"{float(winner['runtime_s']):.3f}s"],
            ["Best round", winner["round"]],
        ]
    )
    settings_table = axis.table(
        cellText=table_rows,
        colLabels=("Setting", "Best value"),
        cellLoc="center",
        colLoc="center",
        bbox=(0.08, 0.00, 0.84, 0.94),
    )
    settings_table.auto_set_font_size(False)
    settings_table.set_fontsize(9.5)
    for (row, column), cell in settings_table.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if row == 0:
            cell.set_facecolor("#e9ecef")
            cell.set_text_props(fontweight="bold")
        elif column == 0:
            cell.set_facecolor("#f7f7f7")
            cell.set_text_props(ha="left")


def add_research_notes(axis, circuit, rows):
    axis.axis("off")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.text(
        0.02,
        0.98,
        "Research summary",
        fontsize=13,
        fontweight="bold",
        va="top",
    )
    axis.text(
        0.02,
        0.84,
        textwrap.fill(research_summary(circuit, rows), width=66),
        fontsize=10,
        va="top",
        linespacing=1.3,
    )
    axis.text(
        0.02,
        0.48,
        "Main improvement rounds",
        fontsize=12,
        fontweight="bold",
        va="top",
    )
    events = improvement_events(rows)[:3]
    if not events:
        event_text = "No post-baseline improvement has been recorded yet."
    else:
        event_lines = []
        for index, event in enumerate(events, start=1):
            event_lines.append(
                textwrap.fill(
                    f"{index}. Round {event['round']} — "
                    f"{event['change'].replace(' -> ', ' → ')}: "
                    f"{event['ratio']:.2f}x faster "
                    f"({event['old']:.3f}s → {event['new']:.3f}s)",
                    width=64,
                    subsequent_indent="   ",
                )
            )
        event_text = "\n".join(event_lines)
    axis.text(
        0.03,
        0.37,
        event_text,
        fontsize=10,
        va="top",
        linespacing=1.4,
    )


def plot_results():
    all_rows = {circuit: read_rows(circuit) for circuit in CIRCUITS}
    if not any(all_rows.values()):
        return

    figure = plt.figure(figsize=(16, 15), layout="constrained")
    grid = figure.add_gridspec(
        3,
        2,
        height_ratios=(3.2, 2.7, 2.7),
        hspace=0.16,
        wspace=0.10,
    )

    for column, (circuit, title) in enumerate(CIRCUITS.items()):
        rows = all_rows[circuit]
        add_runtime_plot(figure.add_subplot(grid[0, column]), title, rows)
        add_settings_table(figure.add_subplot(grid[1, column]), rows)
        add_research_notes(figure.add_subplot(grid[2, column]), circuit, rows)

    figure.suptitle(
        "CUDA-Q exact TensorNet: two independent 30-round searches",
        fontsize=16,
        fontweight="bold",
    )
    figure.savefig(ROOT / "results.png", dpi=170)
    plt.close(figure)


if __name__ == "__main__":
    plot_results()
    print(ROOT / "results.png")

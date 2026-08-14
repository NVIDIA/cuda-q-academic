"""Plot lowest-energy outcomes and time-resolved energy trajectories."""

import csv
import json
from pathlib import Path

from summarize_results import valid_rows, winner


ROOT = Path(__file__).resolve().parent
CASES = ("qaoa_depth15",)
NVIDIA_GREEN = "#76B900"
NVIDIA_DARK = "#1A1A1A"
MUTED = "#8A8F98"


def read_rows(case):
    path = ROOT / "research" / case / "results.tsv"
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_trace(case, round_number):
    path = (
        ROOT
        / "research"
        / case
        / "traces"
        / f"round_{round_number:03d}.json"
    )
    if not path.exists():
        return None
    return json.loads(path.read_text())


def exact_energy(case):
    reference = json.loads((ROOT / "reference.json").read_text())
    return float(reference["cases"][case]["exact_energy"])


def new_best_rounds(rows):
    rounds = set()
    prefix = []
    for row in rows:
        prefix.append(row)
        leader = winner(prefix)
        if leader is row:
            rounds.add(int(row["round"]))
    return rounds


def winning_round(rows):
    best = winner(rows)
    return int(best["round"]) if best is not None else None


def plot_lowest_energy_by_round():
    rows = read_rows(CASES[0])
    if not rows:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    figure, axis = plt.subplots(figsize=(13.5, 7.2), constrained_layout=True)
    figure.patch.set_facecolor("#F4F5F7")
    axis.set_facecolor("#FFFFFF")
    improved = new_best_rounds(rows)
    winning = winning_round(rows)
    ground_energy = exact_energy(CASES[0])

    for row in rows:
        round_number = int(row["round"])
        if row.get("valid") != "yes" or not row.get("best_energy"):
            axis.scatter(
                round_number,
                0.0,
                marker="x",
                s=140,
                linewidth=2.5,
                color="#D62728",
                zorder=5,
            )
            continue
        energy = float(row["best_energy"])
        converged = row.get("converged") == "yes"
        color = NVIDIA_GREEN if round_number in improved else MUTED
        marker = "o" if converged else "X"
        axis.scatter(
            round_number,
            energy,
            marker=marker,
            s=120 if converged else 145,
            color=color,
            edgecolor=NVIDIA_DARK if round_number == winning else "white",
            linewidth=2.2 if round_number == winning else 0.9,
            zorder=6,
        )
        axis.annotate(
            f"{energy:.6f}",
            (round_number, energy),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color=NVIDIA_DARK if round_number in improved else "#626870",
        )

    valid = valid_rows(rows)
    axis.axhline(
        ground_energy,
        color="#A855F7",
        linewidth=1.8,
        linestyle="--",
        zorder=2,
        label=f"Exact ground energy ({ground_energy:.6f})",
    )
    axis.plot(
        [int(row["round"]) for row in valid],
        [float(row["best_energy"]) for row in valid],
        color="#C8CCD1",
        linewidth=1.1,
        zorder=1,
    )
    if winning is not None:
        best_row = next(row for row in rows if int(row["round"]) == winning)
        axis.annotate(
            "LOWEST ENERGY",
            (winning, float(best_row["best_energy"])),
            xytext=(0, -50),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color="#4D7A00",
            arrowprops={
                "arrowstyle": "->",
                "color": NVIDIA_GREEN,
                "lw": 1.8,
            },
        )

    axis.set_title(
        "Lowest QAOA energy observed within each 300-observe budget",
        fontsize=19,
        fontweight="bold",
        color=NVIDIA_DARK,
        pad=18,
    )
    axis.text(
        0.5,
        1.01,
        "Color shows whether the round set a new study best; marker shape "
        "shows accepted-energy convergence.",
        transform=axis.transAxes,
        ha="center",
        fontsize=11,
        color="#5F6368",
    )
    axis.set_xlabel("Autoresearch round", fontsize=12)
    axis.set_ylabel("Lowest observed energy (lower is better)", fontsize=12)
    axis.set_xticks(range(1, len(rows) + 1))
    axis.grid(axis="y", alpha=0.22)
    axis.spines[["top", "right"]].set_visible(False)
    legend = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=NVIDIA_GREEN,
            markeredgecolor="white",
            markersize=10,
            label="Converged + new best",
        ),
        Line2D(
            [0],
            [0],
            marker="X",
            color="none",
            markerfacecolor=NVIDIA_GREEN,
            markeredgecolor="white",
            markersize=10,
            label="Not converged + new best",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=MUTED,
            markeredgecolor="white",
            markersize=10,
            label="Converged, not a new best",
        ),
        Line2D(
            [0],
            [0],
            marker="X",
            color="none",
            markerfacecolor=MUTED,
            markeredgecolor="white",
            markersize=10,
            label="Not converged, not a new best",
        ),
        Line2D(
            [0],
            [0],
            color="#A855F7",
            linewidth=1.8,
            linestyle="--",
            label=f"Exact ground energy ({ground_energy:.6f})",
        ),
    ]
    axis.legend(handles=legend, loc="best", frameon=True)
    output = ROOT / "lowest_energy_by_round.png"
    figure.savefig(output, dpi=180)
    plt.close(figure)
    return output


def plot_energy_trajectories_3d():
    rows = read_rows(CASES[0])
    if not rows:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figure = plt.figure(figsize=(12, 8), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    improved = new_best_rounds(rows)
    winning = winning_round(rows)
    ground_energy = exact_energy(CASES[0])
    for row in rows:
        round_number = int(row["round"])
        result = read_trace(CASES[0], round_number)
        if result is None or not result.get("trace"):
            continue
        calls = np.asarray(
            [float(entry["call"]) for entry in result["trace"]]
        )
        energies = np.asarray(
            [float(entry["best_energy"]) for entry in result["trace"]]
        )
        rounds = np.full_like(calls, round_number, dtype=float)
        is_winner = round_number == winning
        color = (
            NVIDIA_GREEN
            if is_winner
            else "#B4E61D"
            if round_number in improved
            else MUTED
        )
        axis.plot(
            rounds,
            calls,
            energies,
            color=color,
            linewidth=3.2 if is_winner else 1.2,
            alpha=1.0 if is_winner else 0.65,
        )
    plane_rounds, plane_calls = np.meshgrid(
        np.asarray([1.0, float(len(rows))]),
        np.asarray([0.0, 300.0]),
    )
    plane_energies = np.full_like(plane_rounds, ground_energy)
    axis.plot_surface(
        plane_rounds,
        plane_calls,
        plane_energies,
        color="#A855F7",
        alpha=0.32,
        linewidth=0,
        shade=False,
    )
    axis.text(
        float(len(rows)),
        300.0,
        ground_energy,
        f"  exact {ground_energy:.6f}",
        color="#7E22CE",
        fontsize=9,
    )
    axis.set_title(
        "Depth-15 QAOA energy trajectories",
        fontsize=17,
        fontweight="bold",
        color=NVIDIA_DARK,
    )
    axis.set_xlabel("Autoresearch round")
    axis.set_ylabel("Counted cudaq.observe calls")
    axis.set_zlabel("Best observed energy")
    axis.set_ylim(0, 300)
    axis.view_init(elev=25, azim=-62)
    output = ROOT / "energy_trajectories_3d.png"
    figure.savefig(output, dpi=180)
    plt.close(figure)
    return output


def plot_results():
    outputs = (
        plot_lowest_energy_by_round(),
        plot_energy_trajectories_3d(),
    )
    if any(outputs):
        from build_demo_widget import build_widget

        build_widget()
    return outputs


if __name__ == "__main__":
    plot_results()

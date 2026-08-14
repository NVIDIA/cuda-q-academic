"""Write mechanical summaries for the observe-budgeted energy study."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASES = ("qaoa_depth15",)
ENERGY_TIE_TOLERANCE = 1.0e-6


def read_rows(case):
    path = ROOT / "research" / case / "results.tsv"
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def valid_rows(rows):
    return [
        row
        for row in rows
        if row.get("valid") == "yes" and row.get("best_energy")
    ]


def winner(rows):
    candidates = valid_rows(rows)
    if not candidates:
        return None
    minimum_energy = min(float(row["best_energy"]) for row in candidates)
    close = [
        row
        for row in candidates
        if float(row["best_energy"])
        <= minimum_energy + ENERGY_TIE_TOLERANCE
    ]

    def preferred_completion(row):
        converged = row.get("converged") in ("yes", True)
        try:
            calls = int(row.get("calls_used"))
            max_calls = int(row.get("max_calls"))
        except (TypeError, ValueError):
            calls = max_calls = 0
        finished_early = (
            row.get("status") in ("converged", "not_converged")
            and max_calls > 0
            and calls < max_calls
        )
        return converged or finished_early

    def optional_number(row, field):
        try:
            return float(row.get(field))
        except (TypeError, ValueError):
            return float("inf")

    return min(
        close,
        key=lambda row: (
            not preferred_completion(row),
            optional_number(row, "evaluator_elapsed_s"),
            optional_number(row, "calls_used"),
            int(row["round"]),
        ),
    )


def case_summary(case, rows):
    valid = valid_rows(rows)
    best = winner(rows)
    converged = [row for row in valid if row.get("converged") == "yes"]
    capped = [row for row in valid if row.get("status") == "call_cap"]
    lines = [
        f"# {case} observe-budgeted optimizer autoresearch",
        "",
        f"- Recorded rounds: {len(rows)}",
        f"- Valid energy results: {len(valid)}",
        f"- Accepted-energy converged rounds: {len(converged)}",
        f"- Observe-capped, non-converged rounds: {len(capped)}",
    ]
    if best is not None:
        lines.append(
            f"- Lowest observed energy: {float(best['best_energy']):.12g} "
            f"(round {best['round']})"
        )
    lines.extend(
        [
            "",
            "## Round results",
            "",
            "| Round | Optimizer | Lowest energy | Elapsed s | Calls | "
            "Converged | New leader | Status |",
            "| ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        energy = (
            f"{float(row['best_energy']):.9f}"
            if row.get("best_energy")
            else "—"
        )
        elapsed = (
            f"{float(row['evaluator_elapsed_s']):.3f}"
            if row.get("evaluator_elapsed_s")
            else "—"
        )
        calls = row.get("calls_used") or "—"
        lines.append(
            f"| {row['round']} | {row['optimizer_label']} | {energy} | "
            f"{elapsed} | {calls} | {row.get('converged', 'no')} | "
            f"{row.get('improved_best_so_far', 'no')} | "
            f"{row['status']} |"
        )
    if best is not None:
        lines.extend(
            [
                "",
                "## Winning implementation",
                "",
                f"Round {best['round']} (`{best['optimizer_label']}`) "
                f"won under the energy and close-tie rules with energy "
                f"{float(best['best_energy']):.12g}, in "
                f"{float(best['evaluator_elapsed_s']):.3f} seconds using "
                f"{best['calls_used']} counted circuit evaluations. "
                f"Accepted-energy convergence: "
                f"{best.get('converged', 'no')}.",
                "",
                f"Optimizer source SHA-256: "
                f"`{best['optimizer_source_sha256']}`.",
            ]
        )
    insights = ROOT / "research" / case / "insights.md"
    if insights.exists():
        lines.extend(
            [
                "",
                "## Researcher interpretation",
                "",
                insights.read_text().strip(),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_summaries():
    all_rows = {case: read_rows(case) for case in CASES}
    if not any(all_rows.values()):
        return None
    combined = [
        "# CUDA-Q depth-15 QAOA observe-budgeted optimizer autoresearch",
        "",
        "Each round receives the same seeded depth-fifteen starting point and a "
        "hard budget of 300 counted observes. Energy differences within 1e-6 "
        "use convergence/early completion and elapsed time as tie-breakers.",
        "",
        "| Case | Rounds | Winning optimizer | Lowest energy | "
        "Elapsed s | Converged |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for case in CASES:
        rows = all_rows[case]
        if rows:
            summary = case_summary(case, rows)
            (ROOT / "research" / case / "summary.md").write_text(summary)
        best = winner(rows)
        if best is None:
            combined.append(f"| {case} | {len(rows)} | — | — | — | — |")
        else:
            combined.append(
                f"| {case} | {len(rows)} | {best['optimizer_label']} | "
                f"{float(best['best_energy']):.9f} | "
                f"{float(best['evaluator_elapsed_s']):.3f} | "
                f"{best.get('converged', 'no')} |"
            )
    combined.extend(
        [
            "",
            "See `lowest_energy_by_round.png`, "
            "`energy_trajectories_3d.png`, and "
            "`energy_trajectories_3d.html` for study visualizations.",
        ]
    )
    output = ROOT / "summary.md"
    output.write_text("\n".join(combined) + "\n")
    return output


if __name__ == "__main__":
    write_summaries()

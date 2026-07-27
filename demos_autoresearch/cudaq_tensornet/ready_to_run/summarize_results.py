"""Generate one evidence-backed summary for each independent researcher."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CIRCUITS = {
    "nonlocal": "Nonlocal layers",
    "controlled": "Controlled gates",
}
SETTING_NAMES = (
    "precision",
    "controlled_rank",
    "path_reuse",
    "hyper_samples",
    "find_threads",
    "find_limit",
    "deterministic",
    "scratch_percentage",
)


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


def insight_body(path):
    lines = path.read_text().strip().splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


def researcher_summary(circuit, title, rows):
    lines = [
        f"# {title} researcher summary",
        "",
        "This report is regenerated from this circuit's ledger only.",
        "",
    ]
    complete = complete_rows(rows)
    if not complete:
        lines.append("No valid complete round has been recorded yet.")
        return "\n".join(lines) + "\n"

    baseline = complete[0]
    best = min(complete, key=lambda row: float(row["runtime_s"]))
    speedup = float(baseline["runtime_s"]) / float(best["runtime_s"])
    lines.extend(
        [
            "## Outcome",
            "",
            f"Round {best['round']} is best at **{float(best['runtime_s']):.3f}s**, "
            f"a **{speedup:.2f}x speedup** over the "
            f"{float(baseline['runtime_s']):.3f}s baseline.",
            "",
            "Best settings:",
            "",
        ]
    )
    for name in SETTING_NAMES:
        lines.append(f"- `{name}`: `{best[name]}`")

    lines.extend(
        [
            "",
            "## Evidence-backed learnings",
            "",
        ]
    )
    for row in rows[1:]:
        lines.append(
            f"- Round {row['round']} — **{row['change']}**: "
            f"{row['observation']} Hypothesis: {row['hypothesis']}"
        )
    if len(rows) == 1:
        lines.append("- Only the baseline has run so far.")

    lines.extend(
        [
            "",
            "## Decision trail",
            "",
            "| Round | Change | Reasoning | Result | Next-round reasoning |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in rows:
        result = (
            f"{row['runtime_s']}s; {row['status']}. {row['observation']}"
            if row["runtime_s"]
            else f"{row['status']} at {row['wall_s']}s. {row['observation']}"
        )
        cells = [
            row["round"],
            row["change"],
            row["reasoning_for_change"],
            result,
            row["next_round_reasoning"],
        ]
        lines.append(
            "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"
        )

    interpretation = ROOT / "research" / circuit / "insights.md"
    if interpretation.exists():
        lines.extend(
            [
                "",
                "## Researcher interpretation",
                "",
                insight_body(interpretation),
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_summaries():
    overview = [
        "# Two independent exact-tensornet searches",
        "",
        "Each researcher optimizes one fixed circuit and sees only its own ledger. "
        "GPU evaluations are serialized for comparable timing.",
        "",
        "| Circuit | Rounds | Baseline | Best | Speedup | Detailed summary |",
        "|---|---:|---:|---:|---:|---|",
    ]
    interpretations = []
    best_by_circuit = {}
    for circuit, title in CIRCUITS.items():
        rows = read_rows(circuit)
        text = researcher_summary(circuit, title, rows)
        directory = ROOT / "research" / circuit
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "summary.md").write_text(text)
        complete = complete_rows(rows)
        if complete:
            baseline = float(complete[0]["runtime_s"])
            best_row = min(complete, key=lambda row: float(row["runtime_s"]))
            best = float(best_row["runtime_s"])
            best_by_circuit[circuit] = best_row
            overview.append(
                f"| {title} | {len(rows)} | {baseline:.3f}s | {best:.3f}s | "
                f"{baseline / best:.2f}x | "
                f"[open](research/{circuit}/summary.md) |"
            )
        else:
            overview.append(
                f"| {title} | {len(rows)} | — | — | — | "
                f"[open](research/{circuit}/summary.md) |"
            )
        insights = directory / "insights.md"
        if insights.exists():
            interpretations.extend(
                [
                    "",
                    f"## {title}: researcher interpretation",
                    "",
                    insight_body(insights),
                ]
            )
    if len(best_by_circuit) == len(CIRCUITS):
        overview.extend(
            [
                "",
                "## Final best settings",
                "",
                "| Setting | Nonlocal | Controlled gates |",
                "|---|---:|---:|",
            ]
        )
        for setting in SETTING_NAMES:
            overview.append(
                f"| `{setting}` | `{best_by_circuit['nonlocal'][setting]}` | "
                f"`{best_by_circuit['controlled'][setting]}` |"
            )
        overview.extend(
            [
                f"| Best runtime | "
                f"`{float(best_by_circuit['nonlocal']['runtime_s']):.3f}s` | "
                f"`{float(best_by_circuit['controlled']['runtime_s']):.3f}s` |",
                f"| Best round | `{best_by_circuit['nonlocal']['round']}` | "
                f"`{best_by_circuit['controlled']['round']}` |",
                "",
                "## Why path reuse can be slower",
                "",
                "CUDA-Q reuses the contraction **path** (the planned order), "
                "not previously contracted intermediate tensors. Its reuse "
                "implementation prepares one all-qubit operator topology and "
                "executes it for each Pauli term. That saves repeated path "
                "finding, but it prevents term-specific light-cone "
                "simplification for sparse observables.",
                "",
                "The nonlocal observable has only one Pauli-product term, so "
                "there is no second term over which to amortize reuse. The "
                "controlled observable has six sparse one-qubit Z terms; each "
                "can benefit from a small, term-specific causal cone. In both "
                "cases the lost simplification and reuse machinery cost more "
                "than the path-finding work saved.",
            ]
        )
    overview.extend(interpretations)
    overview.append("")
    (ROOT / "summary.md").write_text("\n".join(overview))


if __name__ == "__main__":
    write_summaries()
    print(ROOT / "summary.md")

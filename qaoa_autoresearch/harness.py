import argparse
import importlib
import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
import sys
from types import ModuleType
from typing import List, Tuple

import cudaq
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WORK_DIR = ROOT
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from hamiltonian import (
    approx_ratio_from_energy,
    build_maxcut_hamiltonian,
    emin_from_optimal_cut,
    read_maxcut_instance,
    read_maxcut_solution,
)
import candidate_kernel as _candidate_kernel_module
from candidate_kernel import candidate_superkernel


LEDGER_PATH = WORK_DIR / "ledger.md"
CANDIDATE_KERNEL_PATH = WORK_DIR / "candidate_kernel.py"
BASELINE_PATH = WORK_DIR / "baseline_result.json"
BEST_PATH = WORK_DIR / "best_result.json"
REPORTS_DIR = WORK_DIR / "reports"

INSTANCE = "instances/mc_008_003_000.txt"
SOLUTION = "instances/mc_008_003_000.sol"
QUBITS = 8
PARAMETER_COUNT = 6
BASELINE_LAYER_COUNT = 3
DEFAULT_MAX_ITERATIONS = 40
PASS_BAND_FRACTION = 0.05


@dataclass
class EvalResult:
    expectation: float
    approx_ratio: float
    gate_score: int
    single_qubit_gates: int
    two_qubit_gates: int
    objective: float
    success: bool
    nfev: int


@cudaq.kernel
def main_kernel(angles: List[float]):
    qubits = cudaq.qvector(QUBITS)
    h(qubits)
    candidate_superkernel(qubits, angles)


@cudaq.kernel
def baseline_qaoa_kernel(angles: List[float]):
    qubits = cudaq.qvector(QUBITS)
    h(qubits)

    for layer in range(BASELINE_LAYER_COUNT):
        gamma = angles[2 * layer]
        beta = angles[2 * layer + 1]

        x.ctrl(qubits[0], qubits[1])
        rz(2.0 * gamma, qubits[1])
        x.ctrl(qubits[0], qubits[1])

        x.ctrl(qubits[0], qubits[7])
        rz(2.0 * gamma, qubits[7])
        x.ctrl(qubits[0], qubits[7])

        x.ctrl(qubits[0], qubits[6])
        rz(2.0 * gamma, qubits[6])
        x.ctrl(qubits[0], qubits[6])

        x.ctrl(qubits[1], qubits[7])
        rz(2.0 * gamma, qubits[7])
        x.ctrl(qubits[1], qubits[7])

        x.ctrl(qubits[1], qubits[3])
        rz(2.0 * gamma, qubits[3])
        x.ctrl(qubits[1], qubits[3])

        x.ctrl(qubits[7], qubits[2])
        rz(2.0 * gamma, qubits[2])
        x.ctrl(qubits[7], qubits[2])

        x.ctrl(qubits[2], qubits[4])
        rz(2.0 * gamma, qubits[4])
        x.ctrl(qubits[2], qubits[4])

        x.ctrl(qubits[2], qubits[5])
        rz(2.0 * gamma, qubits[5])
        x.ctrl(qubits[2], qubits[5])

        x.ctrl(qubits[4], qubits[3])
        rz(2.0 * gamma, qubits[3])
        x.ctrl(qubits[4], qubits[3])

        x.ctrl(qubits[4], qubits[5])
        rz(2.0 * gamma, qubits[5])
        x.ctrl(qubits[4], qubits[5])

        x.ctrl(qubits[3], qubits[6])
        rz(2.0 * gamma, qubits[6])
        x.ctrl(qubits[3], qubits[6])

        x.ctrl(qubits[6], qubits[5])
        rz(2.0 * gamma, qubits[5])
        x.ctrl(qubits[6], qubits[5])

        for qubit_index in range(8):
            rx(2.0 * beta, qubits[qubit_index])


def _configure_target() -> str:
    if cudaq.num_available_gpus() > 0 and cudaq.has_target("nvidia"):
        cudaq.set_target("nvidia")
        return "nvidia"
    cudaq.set_target("qpp-cpu")
    return "qpp-cpu"


def _load_candidate_module() -> ModuleType:
    global _candidate_kernel_module, candidate_superkernel
    _candidate_kernel_module = importlib.reload(_candidate_kernel_module)
    candidate_superkernel = _candidate_kernel_module.candidate_superkernel
    return _candidate_kernel_module


def _parameter_count(candidate: ModuleType) -> int:
    parameter_count = int(candidate.PARAMETER_COUNT)
    if parameter_count != PARAMETER_COUNT:
        raise ValueError(f"candidate PARAMETER_COUNT must be exactly {PARAMETER_COUNT}")
    return parameter_count


def _initial_parameters(candidate: ModuleType) -> np.ndarray:
    return np.zeros(_parameter_count(candidate), dtype=float)


def _gate_counts_for_kernel(kernel, parameter_count: int) -> Tuple[int, int]:
    angles = [0.0] * parameter_count
    qir = cudaq.translate(kernel, angles, format="qir")

    direct_gate_calls = re.findall(r"call void @__quantum__qis__([A-Za-z0-9_]+)\(", qir)
    one_qubit_count = len(direct_gate_calls) - QUBITS
    if one_qubit_count < 0:
        raise ValueError("CUDA-Q gate trace did not include the fixed main_kernel superposition")

    controlled_invocations = re.findall(
        r"@generalizedInvokeWithRotationsControlsTargets\([^\n]*@__quantum__qis__[A-Za-z0-9_]+__ctl",
        qir,
    )
    two_qubit_count = len(controlled_invocations)
    return one_qubit_count, two_qubit_count


def _gate_counts(candidate: ModuleType) -> Tuple[int, int]:
    return _gate_counts_for_kernel(main_kernel, _parameter_count(candidate))


def _gate_score(single_count: int, two_count: int) -> int:
    return single_count + 10 * two_count


def _pass_threshold(baseline_ratio: float) -> float:
    return round(float(baseline_ratio * (1.0 - PASS_BAND_FRACTION)), 12)


def _is_passing(approx_ratio: float, baseline_ratio: float) -> bool:
    return approx_ratio >= _pass_threshold(baseline_ratio)


def _objective(approx_ratio: float, gate_score: int, baseline_ratio: float) -> float:
    target_ratio = _pass_threshold(baseline_ratio)
    if approx_ratio >= target_ratio:
        return float(gate_score)
    # Heavy penalty when below the baseline band so search prioritizes quality first.
    return float(1_000_000.0 + (target_ratio - approx_ratio) * 100_000.0 + gate_score)


def _evaluate_kernel(kernel, parameter_count: int, max_iterations: int = DEFAULT_MAX_ITERATIONS) -> EvalResult:
    instance_path = ROOT / INSTANCE
    solution_path = ROOT / SOLUTION
    instance = read_maxcut_instance(instance_path)
    solution = read_maxcut_solution(solution_path, expected_nodes=instance.nodes)
    hamiltonian = build_maxcut_hamiltonian(instance.edges)
    if QUBITS != instance.nodes:
        raise ValueError("harness QUBITS must match instance node count")

    start = np.zeros(parameter_count, dtype=float)

    def cost(params):
        angles = [float(x) for x in params[:parameter_count]]
        expectation = cudaq.observe(
            kernel,
            hamiltonian,
            angles,
        ).expectation()
        return float(expectation)

    result = minimize(
        cost,
        start,
        method="COBYLA",
        options={"maxiter": max_iterations, "rhobeg": 0.5, "tol": 1e-6},
    )
    final_energy = float(cost(result.x))
    emin = emin_from_optimal_cut(solution.objective)
    ratio = approx_ratio_from_energy(final_energy, emin)
    single_count, two_count = _gate_counts_for_kernel(kernel, parameter_count)
    score = _gate_score(single_count, two_count)
    return EvalResult(
        expectation=final_energy,
        approx_ratio=ratio,
        gate_score=score,
        single_qubit_gates=single_count,
        two_qubit_gates=two_count,
        objective=0.0,
        success=bool(result.success),
        nfev=int(result.nfev),
    )


def evaluate_candidate(max_iterations: int = DEFAULT_MAX_ITERATIONS, seed: int = 13) -> EvalResult:
    candidate = _load_candidate_module()
    result = _evaluate_kernel(main_kernel, _parameter_count(candidate), max_iterations=max_iterations)
    baseline_ratio = _load_baseline_ratio()
    result.objective = _objective(result.approx_ratio, result.gate_score, baseline_ratio)
    return result


def evaluate_baseline(max_iterations: int = DEFAULT_MAX_ITERATIONS) -> EvalResult:
    result = _evaluate_kernel(baseline_qaoa_kernel, PARAMETER_COUNT, max_iterations=max_iterations)
    result.objective = float(result.gate_score)
    return result


def _next_round() -> int:
    lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    data_lines = [line for line in lines if line.startswith("| ") and not line.startswith("| round ") and not line.startswith("|---")]
    return len(data_lines) + 1


def _load_baseline_ratio() -> float:
    if not BASELINE_PATH.exists():
        raise ValueError("No baseline result found. Run `harness.py baseline` before candidate evals.")
    payload = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return float(payload["baseline_ratio"])


def _append_ledger(
    round_id: int,
    change: str,
    note: str,
    result: EvalResult,
    baseline_ratio: float,
    keep: str,
):
    pass_status = "green" if _is_passing(result.approx_ratio, baseline_ratio) else "red"
    row = (
        f"| {round_id} | {change} | {note} | "
        f"{result.approx_ratio:.6f} | {baseline_ratio:.6f} | {_pass_threshold(baseline_ratio):.6f} | "
        f"{result.gate_score} | {result.objective:.3f} | {pass_status} | {keep} |"
    )
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(row + "\n")


def _read_ledger_rows() -> List[dict]:
    lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    rows: List[dict] = []
    for line in lines:
        if not line.startswith("| "):
            continue
        if line.startswith("| round ") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 10:
            continue
        rows.append(
            {
                "round": int(parts[0]),
                "change": parts[1],
                "note": parts[2],
                "approx_ratio": float(parts[3]),
                "baseline_ratio": float(parts[4]),
                "pass_threshold": float(parts[5]),
                "gate_score": float(parts[6]),
                "objective": float(parts[7]),
                "pass": parts[8],
                "keep": parts[9],
            }
        )
    return rows


def _row_pass_color(row: dict) -> str:
    return "green" if float(row["approx_ratio"]) >= float(row["pass_threshold"]) else "red"


def _best_candidate_row(rows: List[dict]) -> dict:
    candidate_rows = [row for row in rows if int(row["round"]) != 1 and row["keep"] == "yes"]
    if not candidate_rows:
        candidate_rows = [row for row in rows if int(row["round"]) != 1]
    if not candidate_rows:
        raise ValueError("No candidate rows found. Run at least one eval round first.")
    return min(candidate_rows, key=lambda row: (float(row["objective"]), -float(row["approx_ratio"])))


def _write_ansatz_comparison(rows: List[dict]) -> Path:
    baseline_row = rows[0]
    candidate_row = _best_candidate_row(rows)
    out_path = REPORTS_DIR / "ansatz_comparison.md"

    baseline_single, baseline_two = _gate_counts_for_kernel(baseline_qaoa_kernel, PARAMETER_COUNT)
    candidate_single, candidate_two = _gate_counts_for_kernel(main_kernel, PARAMETER_COUNT)
    passing_rows = [
        row for row in rows
        if int(row["round"]) != int(baseline_row["round"]) and _row_pass_color(row) == "green"
    ]
    passing_score_rows = []
    for score in sorted({float(row["gate_score"]) for row in passing_rows}, reverse=True):
        rows_at_score = [row for row in passing_rows if float(row["gate_score"]) == score]
        passing_score_rows.append(
            max(rows_at_score, key=lambda row: (float(row["approx_ratio"]), -int(row["round"])))
        )
    passing_table_rows = "\n".join(
        "| "
        f"{row['round']} | {row['change']} | {row['approx_ratio']:.6f} | "
        f"{row['approx_ratio'] - baseline_row['approx_ratio']:.6f} | "
        f"{row['gate_score']:.0f} | {baseline_row['gate_score'] - row['gate_score']:.0f} | "
        f"{row['keep']} |"
        for row in passing_score_rows
    )

    report = f"""# Ansatz Comparison

Instance: `{INSTANCE}`

## Baseline vs Best Candidate

| ansatz | round | approx_ratio | gate_score | single_qubit_gates | two_qubit_gates |
|---|---:|---:|---:|---:|---:|
| fixed 3-layer QAOA baseline | {baseline_row["round"]} | {baseline_row["approx_ratio"]:.6f} | {baseline_row["gate_score"]:.0f} | {baseline_single} | {baseline_two} |
| best custom 6-parameter candidate | {candidate_row["round"]} | {candidate_row["approx_ratio"]:.6f} | {candidate_row["gate_score"]:.0f} | {candidate_single} | {candidate_two} |

Baseline ratio: `{baseline_row["baseline_ratio"]:.6f}`
Passing threshold: `{baseline_row["pass_threshold"]:.6f}`

## Passing Custom Runs

| representative_run | change | best_approx_ratio_at_score | ratio_delta_vs_baseline | gate_score | gate_score_saved_vs_baseline | keep |
|---:|---|---:|---:|---:|---:|---|
{passing_table_rows}

## How The Best Candidate Differs

The QAOA baseline uses three repeated layers. Each layer applies a cost block on all 12 graph edges, then applies an RX mixer on all 8 qubits. That gives the baseline higher quality, but also a gate score of `{baseline_row["gate_score"]:.0f}`.

The best custom candidate is a single graph-aware layer with 6 total parameters. It keeps 9 of the 12 edge cost blocks and drops the `0-7`, `2-5`, and `4-5` edge blocks found during the pruning search. Its cost angles are shared by graph regions, and its RX mixer angles are also grouped by node region. This keeps it inside the 95% baseline band while reducing the score by `{baseline_row["gate_score"] - candidate_row["gate_score"]:.0f}` gate-score points.
"""
    out_path.write_text(report, encoding="utf-8")
    return out_path


def _label_annotations(rows: List[dict]) -> List[tuple[dict, str, tuple[int, int]]]:
    point_counts = {}
    first_rows = {}

    for row in rows:
        key = (row["gate_score"], row["approx_ratio"])
        point_counts[key] = point_counts.get(key, 0) + 1
        first_rows.setdefault(key, row)

    annotations = []
    for row in rows:
        key = (row["gate_score"], row["approx_ratio"])
        if first_rows[key] is not row:
            continue
        label = str(row["round"])
        if point_counts[key] > 1:
            label += "*"
        annotations.append((row, label, (6, 6)))

    return annotations


def generate_report():
    rows = _read_ledger_rows()
    if not rows:
        raise ValueError("No ledger data found. Run at least one eval round first.")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "ratio_vs_gate_score.png"

    x = [row["gate_score"] for row in rows]
    y = [row["approx_ratio"] for row in rows]
    colors = [_row_pass_color(row) for row in rows]
    baseline_ratio = rows[-1]["baseline_ratio"]
    pass_threshold = _pass_threshold(baseline_ratio)
    upper_band = baseline_ratio * (1.0 + PASS_BAND_FRACTION)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(x, y, c=colors, s=42)
    ax.axhspan(pass_threshold, upper_band, color="green", alpha=0.08, label="+/- 5% baseline band")
    ax.axhline(baseline_ratio, linestyle="-", linewidth=1.2, label="baseline ratio")
    ax.axhline(pass_threshold, linestyle="--", linewidth=1.5, label="passing threshold")

    for row, label, label_offset in _label_annotations(rows):
        ax.annotate(
            label,
            (row["gate_score"], row["approx_ratio"]),
            textcoords="offset points",
            xytext=label_offset,
            fontsize=8,
        )

    ax.text(
        0.99,
        0.02,
        "* multiple runs produced this result",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
    )
    ax.set_title("AutoResearch Progress: Approximation Ratio vs Gate Score")
    ax.set_xlabel("Gate score (1*single + 10*two-qubit)")
    ax.set_ylabel("Approximation ratio")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=170)
    plt.close(fig)
    comparison_path = _write_ansatz_comparison(rows)
    print(f"Report written: {out_path}")
    print(f"Ansatz comparison written: {comparison_path}")


def list_instances():
    instances_dir = ROOT / "instances"
    txt_paths = sorted(instances_dir.glob("mc_*.txt"))
    if not txt_paths:
        raise ValueError(f"No real QED-C instance files found in {instances_dir}")
    print("Available real instances:")
    for txt_path in txt_paths:
        stem = txt_path.stem
        sol_path = txt_path.with_suffix(".sol")
        has_solution = sol_path.exists()
        print(f"  {stem}: txt={txt_path.name}, sol={sol_path.name if has_solution else 'MISSING'}")


def _result_payload(result: EvalResult, baseline_ratio: float, target: str) -> dict:
    return {
        "target": target,
        "approx_ratio": result.approx_ratio,
        "baseline_ratio": baseline_ratio,
        "pass_threshold": _pass_threshold(baseline_ratio),
        "passes_baseline_band": _is_passing(result.approx_ratio, baseline_ratio),
        "expectation": result.expectation,
        "gate_score": result.gate_score,
        "single_qubit_gates": result.single_qubit_gates,
        "two_qubit_gates": result.two_qubit_gates,
        "objective": result.objective,
        "success": result.success,
        "nfev": result.nfev,
    }


def baseline_round(note: str, change: str, max_iterations: int):
    target = _configure_target()
    result = evaluate_baseline(max_iterations=max_iterations)
    baseline_ratio = result.approx_ratio
    payload = _result_payload(result, baseline_ratio, target)

    BASELINE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    BEST_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    round_id = _next_round()
    _append_ledger(round_id, change, note, result, baseline_ratio, keep="yes")

    print(json.dumps(payload, indent=2))
    print("keep=yes")


def eval_round(note: str, change: str, max_iterations: int):
    target = _configure_target()
    baseline_ratio = _load_baseline_ratio()
    result = evaluate_candidate(max_iterations=max_iterations)

    best = None
    if BEST_PATH.exists():
        best = json.loads(BEST_PATH.read_text(encoding="utf-8"))

    keep = "yes"
    if best is not None:
        prev_obj = float(best["objective"])
        if result.objective > prev_obj + 1e-12:
            keep = "no"
        elif abs(result.objective - prev_obj) <= 1e-12 and result.approx_ratio < float(best["approx_ratio"]) - 1e-12:
            keep = "no"

    payload = _result_payload(result, baseline_ratio, target)

    if keep == "yes":
        BEST_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    round_id = _next_round()
    _append_ledger(round_id, change, note, result, baseline_ratio, keep)

    print(json.dumps(payload, indent=2))
    print(f"keep={keep}")


def main():
    parser = argparse.ArgumentParser(description="Simple MaxCut autoresearch harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-instances", help="List available real QED-C MaxCut instances")

    baseline_parser = sub.add_parser("baseline", help="Evaluate built-in 3-layer QAOA baseline")
    baseline_parser.add_argument("--note", default="fixed 3-layer QAOA baseline", help="Why this baseline was run")
    baseline_parser.add_argument("--change", default="baseline 3-layer qaoa kernel", help="Baseline description")
    baseline_parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help="Optimizer iteration budget",
    )

    eval_parser = sub.add_parser("eval", help="Evaluate current candidate circuit")
    eval_parser.add_argument("--note", default="n/a", help="Why this change was proposed")
    eval_parser.add_argument("--change", default="manual edit", help="Single change description")
    eval_parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help="Optimizer iteration budget",
    )
    sub.add_parser("report", help="Generate 2D plot report from ledger")

    args = parser.parse_args()
    if args.cmd == "list-instances":
        list_instances()
        return
    if args.cmd == "baseline":
        baseline_round(note=args.note, change=args.change, max_iterations=args.max_iterations)
        return
    if args.cmd == "eval":
        eval_round(note=args.note, change=args.change, max_iterations=args.max_iterations)
        return
    if args.cmd == "report":
        generate_report()
        return
    raise ValueError(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()

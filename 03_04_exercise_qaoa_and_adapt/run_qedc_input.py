"""Load a QED-C MaxCut input and run the notebook-style ADAPT-QAOA script.

Examples:

    python run_qedc_input.py --list
    python run_qedc_input.py mc_004_003_000
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "maxcut_instances"
DEFAULT_QEDC_INSTANCE = "mc_008_005_000"


class QedcInputError(ValueError):
    pass


@dataclass(frozen=True)
class QedcMaxCutProblem:
    name: str
    qubits_num: int
    edges: list[tuple[int, int]]
    optimal_cut: int | None = None


def list_qedc_instances(data_dir: str | Path = DEFAULT_DATA_DIR) -> list[str]:
    return sorted(path.stem for path in Path(data_dir).glob("*.txt"))


def load_qedc_maxcut(name: str, data_dir: str | Path = DEFAULT_DATA_DIR) -> QedcMaxCutProblem:
    instance_path = Path(data_dir) / f"{name}.txt"
    if not instance_path.exists():
        raise QedcInputError(f"QED-C MaxCut input not found: {instance_path}")

    lines = [line.strip() for line in instance_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    qubits_num = int(lines[0])
    edges = [tuple(map(int, line.split())) for line in lines[1:]]

    solution_path = instance_path.with_suffix(".sol")
    optimal_cut = None
    if solution_path.exists():
        solution_lines = [
            line.strip() for line in solution_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        optimal_cut = int(solution_lines[0])

    return QedcMaxCutProblem(name, qubits_num, edges, optimal_cut)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ADAPT-QAOA on a QED-C MaxCut input.")
    parser.add_argument("instance", nargs="?", default=DEFAULT_QEDC_INSTANCE)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--list", action="store_true", help="List available QED-C inputs and exit")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        for name in list_qedc_instances(args.data_dir):
            print(name)
        return 0

    problem = load_qedc_maxcut(args.instance, args.data_dir)
    from adapt_qaoa import RunSettings, run_adapt_qaoa

    result = run_adapt_qaoa(
        problem.qubits_num,
        problem.edges,
        optimal_cut=problem.optimal_cut,
        name=problem.name,
        settings=RunSettings(),
    )
    print(f"{result['name']}: sampled cut {result['sampled_cut']}/{result['optimal_cut']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

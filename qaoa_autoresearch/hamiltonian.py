from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import cudaq


Edge = Tuple[int, int]


@dataclass(frozen=True)
class MaxCutInstance:
    name: str
    nodes: int
    edges: List[Edge]
    path: Path


@dataclass(frozen=True)
class MaxCutSolution:
    name: str
    objective: int
    bitstring: List[int]
    path: Path


def _read_nonempty_lines(path: Path) -> List[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {path}") from exc

    return [line.strip() for line in lines if line.strip()]


def read_maxcut_instance(path: str | Path) -> MaxCutInstance:
    """Read a QED-C MaxCut `.txt` instance file."""
    instance_path = Path(path)
    lines = _read_nonempty_lines(instance_path)
    if not lines:
        raise ValueError(f"{instance_path} is missing a node count")

    try:
        nodes = int(lines[0])
    except ValueError as exc:
        raise ValueError(f"{instance_path} has an invalid node count") from exc

    edges: List[Edge] = []
    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"{instance_path}:{line_number} has an invalid edge")
        try:
            u, v = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError(f"{instance_path}:{line_number} has an invalid edge") from exc
        if not (0 <= u < nodes and 0 <= v < nodes):
            raise ValueError(f"{instance_path}:{line_number} edge references missing node")
        edges.append((u, v))

    return MaxCutInstance(instance_path.stem, nodes, edges, instance_path)


def read_maxcut_solution(path: str | Path, expected_nodes: int | None = None) -> MaxCutSolution:
    """Read a QED-C MaxCut `.sol` solution file."""
    solution_path = Path(path)
    lines = _read_nonempty_lines(solution_path)
    if not lines:
        raise ValueError(f"{solution_path} is missing an objective value")

    try:
        objective = int(lines[0])
    except ValueError as exc:
        raise ValueError(f"{solution_path} has an invalid objective value") from exc

    if len(lines) < 2:
        raise ValueError(f"{solution_path} is missing a solution bitstring")

    try:
        bitstring = [int(value) for value in lines[1].split()]
    except ValueError as exc:
        raise ValueError(f"{solution_path} has an invalid solution bitstring") from exc

    if any(value not in (0, 1) for value in bitstring):
        raise ValueError(f"{solution_path} solution bitstring must contain only 0 or 1")
    if expected_nodes is not None and len(bitstring) != expected_nodes:
        raise ValueError(f"{solution_path} solution length does not match node count")

    return MaxCutSolution(solution_path.stem, objective, bitstring, solution_path)


def evaluate_cut(bitstring: Sequence[int] | str, edges: Iterable[Edge]) -> int:
    """Return the number of edges whose endpoints are assigned different values."""
    bits = [int(bit) for bit in bitstring] if isinstance(bitstring, str) else list(bitstring)
    return sum(1 for u, v in edges if bits[u] != bits[v])


def bitstring_energy(bitstring: Sequence[int] | str, edges: Iterable[Edge]) -> float:
    """Energy convention for the MaxCut Hamiltonian: lower is better."""
    return -float(evaluate_cut(bitstring, edges))


def emin_from_optimal_cut(optimal_cut: int) -> float:
    return -float(optimal_cut)


def approx_ratio_from_energy(expectation: float, emin: float) -> float:
    if emin == 0.0:
        raise ValueError("E_min must be non-zero for approximation ratio")
    return float(expectation / emin)


def compare_sampled_to_solution(
    sampled_bitstring: Sequence[int] | str,
    edges: Sequence[Edge],
    solution: MaxCutSolution,
) -> dict:
    sampled_cut = evaluate_cut(sampled_bitstring, edges)
    return {
        "sampled_cut": sampled_cut,
        "optimal_cut": solution.objective,
        "opt_gap": solution.objective - sampled_cut,
        "matches_optimal_cut": sampled_cut == solution.objective,
    }


def build_maxcut_hamiltonian(edges: Iterable[Edge]):
    """Build H_p = -1/2 sum((1 - Z_i Z_j)) for unweighted MaxCut."""
    hamiltonian = 0.0
    for u, v in edges:
        hamiltonian += 0.5 * (cudaq.spin.z(u) * cudaq.spin.z(v) - cudaq.spin.i(u) * cudaq.spin.i(v))
    return hamiltonian


def build_spin_hamiltonian():
    """Return the original toy Hamiltonian kept for backwards compatibility."""
    return cudaq.spin.z(0) + cudaq.spin.z(1) + cudaq.spin.z(2)

"""Fixed fifteen-layer QAOA workload. Do not edit during autoresearch."""

import hashlib
import itertools
import json

import cudaq
from cudaq import spin
import numpy as np


CASES = ("qaoa_depth15",)
CASE_NAME = CASES[0]
QUBIT_COUNT = 6
LAYER_COUNT = 15
PARAMETER_COUNT = 2 * LAYER_COUNT
INITIAL_PARAMETER_SEED = 20_260_729

# Exact copy of GRAPHS["small"] from
# ../03_04_qaoa_and_adapt_qaoa/workshop_graphs.py.
WEIGHTED_EDGES = (
    (0, 1, 0.288),
    (0, 2, 0.630),
    (0, 3, 0.639),
    (0, 4, 0.449),
    (0, 5, 0.347),
    (1, 2, 0.266),
    (1, 3, 0.545),
    (1, 4, 0.535),
    (1, 5, 0.268),
    (2, 3, 0.429),
    (2, 4, 0.841),
    (2, 5, 0.713),
    (3, 4, 0.987),
    (3, 5, 0.896),
    (4, 5, 0.724),
)
EDGES = tuple((source, target) for source, target, _ in WEIGHTED_EDGES)
EDGE_WEIGHTS = tuple(weight for _, _, weight in WEIGHTED_EDGES)
EDGE_SOURCES = tuple(source for source, _ in EDGES)
EDGE_TARGETS = tuple(target for _, target in EDGES)


@cudaq.kernel
def qaoa_depth15_kernel(
    qubit_count: int,
    layer_count: int,
    edge_sources: list[int],
    edge_targets: list[int],
    edge_weights: list[float],
    parameters: list[float],
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)

    for layer in range(layer_count):
        gamma = parameters[layer]
        beta = parameters[layer + layer_count]

        for edge in range(len(edge_sources)):
            source = edge_sources[edge]
            target = edge_targets[edge]
            x.ctrl(qubits[source], qubits[target])
            rz(2.0 * gamma * edge_weights[edge], qubits[target])
            x.ctrl(qubits[source], qubits[target])

        for qubit in range(qubit_count):
            rx(2.0 * beta, qubits[qubit])


def maxcut_hamiltonian():
    hamiltonian = 0.0
    for (source, target), weight in zip(EDGES, EDGE_WEIGHTS):
        hamiltonian += 0.5 * weight * (
            spin.z(source) * spin.z(target)
            - spin.i(source) * spin.i(target)
        )
    return hamiltonian


def exact_ground_energy():
    best = 0.0
    for bits in itertools.product((0, 1), repeat=QUBIT_COUNT):
        energy = -sum(
            weight
            for source, target, weight in WEIGHTED_EDGES
            if bits[source] != bits[target]
        )
        best = min(best, energy)
    return round(best, 12)


def _seeded_initial_parameters():
    generator = np.random.default_rng(INITIAL_PARAMETER_SEED)
    base_gamma = np.linspace(0.18, 0.32, LAYER_COUNT)
    base_beta = np.linspace(-0.34, -0.14, LAYER_COUNT)
    perturbation = generator.normal(
        0.0,
        0.025,
        size=PARAMETER_COUNT,
    )
    return np.concatenate((base_gamma, base_beta)) + perturbation


def initial_parameters(case):
    if case != CASE_NAME:
        raise KeyError(f"unknown case: {case}")
    return _seeded_initial_parameters().copy()


def _stable_vector_sha256(vector):
    encoded = json.dumps(
        [float(value) for value in vector],
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def initial_parameters_sha256(case):
    return _stable_vector_sha256(initial_parameters(case))


def case_specification(case):
    if case != CASE_NAME:
        raise KeyError(f"unknown case: {case}")
    return {
        "name": CASE_NAME,
        "source_workshop_graph": (
            "03_04_qaoa_and_adapt_qaoa/workshop_graphs.py:GRAPHS['small']"
        ),
        "qubits": QUBIT_COUNT,
        "layers": LAYER_COUNT,
        "parameter_count": PARAMETER_COUNT,
        "parameter_order": "gamma[0:15], beta[0:15]",
        "edge_count": len(WEIGHTED_EDGES),
        "weighted_edges": [list(edge) for edge in WEIGHTED_EDGES],
        "initial_parameter_seed": INITIAL_PARAMETER_SEED,
        "initial_parameters": initial_parameters(case).tolist(),
        "initial_parameters_sha256": initial_parameters_sha256(case),
        "exact_energy": exact_ground_energy(),
    }


def benchmark_signature():
    encoded = json.dumps(
        case_specification(CASE_NAME),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def energy(case, parameters):
    if case != CASE_NAME:
        raise KeyError(f"unknown case: {case}")
    vector = np.asarray(parameters, dtype=float)
    if vector.shape != (PARAMETER_COUNT,):
        raise ValueError(
            f"{case} expects {PARAMETER_COUNT} parameters, got {vector.shape}"
        )
    return float(
        cudaq.observe(
            qaoa_depth15_kernel,
            maxcut_hamiltonian(),
            QUBIT_COUNT,
            LAYER_COUNT,
            list(EDGE_SOURCES),
            list(EDGE_TARGETS),
            list(EDGE_WEIGHTS),
            vector.tolist(),
        ).expectation()
    )

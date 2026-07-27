"""Two fixed exact-tensor-network workloads. Do not edit during research."""

import hashlib
import json
import random

import cudaq
from cudaq import spin


@cudaq.kernel
def nonlocal_layers(
    qubit_count: int,
    layer_count: int,
    pair_sources: list[int],
    pair_targets: list[int],
    angles: list[float],
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)
    pairs_per_layer = qubit_count // 2
    for layer in range(layer_count):
        for qubit in range(qubit_count):
            ry(angles[layer * qubit_count + qubit], qubits[qubit])
        for pair in range(pairs_per_layer):
            index = layer * pairs_per_layer + pair
            source = pair_sources[index]
            target = pair_targets[index]
            x.ctrl(qubits[source], qubits[target])
            rz(0.19 + 0.027 * layer, qubits[target])
            x.ctrl(qubits[source], qubits[target])


@cudaq.kernel
def controlled_layers(
    qubit_count: int,
    gate_count: int,
    control_a: list[int],
    control_b: list[int],
    control_c: list[int],
    targets: list[int],
    angles: list[float],
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)
    for gate in range(gate_count):
        ry.ctrl(
            angles[gate],
            qubits[control_a[gate]],
            qubits[control_b[gate]],
            qubits[control_c[gate]],
            qubits[targets[gate]],
        )
        x.ctrl(
            qubits[targets[gate]],
            qubits[(targets[gate] + 7) % qubit_count],
        )


def nonlocal_problem():
    qubit_count, layer_count = 30, 5
    generator = random.Random(20260723)
    sources, targets = [], []
    for _ in range(layer_count):
        permutation = list(range(qubit_count))
        generator.shuffle(permutation)
        sources.extend(permutation[0::2])
        targets.extend(permutation[1::2])
    angles = [
        0.11 + 0.019 * ((7 * layer + 5 * qubit + 2) % 19)
        for layer in range(layer_count)
        for qubit in range(qubit_count)
    ]
    observable = (
        spin.x(0)
        * spin.z(3)
        * spin.y(7)
        * spin.x(11)
        * spin.z(16)
        * spin.y(21)
    )
    arguments = (
        qubit_count,
        layer_count,
        sources,
        targets,
        angles,
    )
    specification = {
        "qubits": qubit_count,
        "layers": layer_count,
        "pair_sources": sources,
        "pair_targets": targets,
        "angles": angles,
        "observable": "X0 Z3 Y7 X11 Z16 Y21",
    }
    return nonlocal_layers, observable, arguments, specification


def controlled_problem():
    # This circuit is intentionally smaller than the 30-qubit workload.
    # Its job is to isolate the controlled-tensor expansion trade-off without
    # turning every research round into a long stress test.
    qubit_count, gate_count = 21, 28
    controls_a, controls_b, controls_c, targets, angles = [], [], [], [], []
    for gate in range(gate_count):
        target = (5 * gate + 3) % qubit_count
        candidates = [
            (target + offset) % qubit_count for offset in (1, 6, 13)
        ]
        controls_a.append(candidates[0])
        controls_b.append(candidates[1])
        controls_c.append(candidates[2])
        targets.append(target)
        angles.append(0.13 + 0.023 * (gate % 17))
    observable_qubits = list(range(0, qubit_count, 4))
    observable = 0.0
    for qubit in observable_qubits:
        observable += spin.z(qubit)
    arguments = (
        qubit_count,
        gate_count,
        controls_a,
        controls_b,
        controls_c,
        targets,
        angles,
    )
    specification = {
        "qubits": qubit_count,
        "gate_count": gate_count,
        "control_a": controls_a,
        "control_b": controls_b,
        "control_c": controls_c,
        "targets": targets,
        "angles": angles,
        "observable_qubits": observable_qubits,
    }
    return controlled_layers, observable, arguments, specification


PROBLEM_BUILDERS = {
    "nonlocal": nonlocal_problem,
    "controlled": controlled_problem,
}
CIRCUIT_ORDER = tuple(PROBLEM_BUILDERS)


def benchmark_signature():
    specification = {
        name: builder()[3] for name, builder in PROBLEM_BUILDERS.items()
    }
    encoded = json.dumps(
        specification, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def run_circuit(name):
    kernel, observable, arguments, _ = PROBLEM_BUILDERS[name]()
    return cudaq.observe(kernel, observable, *arguments).expectation()

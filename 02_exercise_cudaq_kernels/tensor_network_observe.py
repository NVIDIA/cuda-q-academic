import os
import time


# CUDA-Q reads these simulator settings when it is imported.
os.environ["CUDAQ_TENSORNET_OBSERVE_CONTRACT_PATH_REUSE"] = "TRUE"
os.environ["CUDAQ_TENSORNET_NUM_HYPER_SAMPLES"] = "32" #Then try "32".
os.environ["CUDAQ_TENSORNET_FIND_LIMIT"] = "FALSE"
os.environ["CUDAQ_TIMING_TAGS"] = "9"

import cudaq
from cudaq import spin


@cudaq.kernel
def qaoa_layer(
    qubit_count: int,
    edge_sources: list[int],
    edge_targets: list[int],
    gamma: float,
    beta: float,
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)

    for edge in range(len(edge_sources)):
        source = edge_sources[edge]
        target = edge_targets[edge]
        x.ctrl(qubits[source], qubits[target])
        rz(2.0 * gamma, qubits[target])
        x.ctrl(qubits[source], qubits[target])

    for qubit in range(qubit_count):
        rx(2.0 * beta, qubits[qubit])


rows = 3
columns = 4
qubit_count = rows * columns

edge_sources = []
edge_targets = []
for row in range(rows):
    for column in range(columns):
        qubit = row * columns + column
        if column + 1 < columns:
            edge_sources.append(qubit)
            edge_targets.append(qubit + 1)
        if row + 1 < rows:
            edge_sources.append(qubit)
            edge_targets.append(qubit + columns)
        if (
            row + 1 < rows
            and column + 1 < columns
            and (row + column) % 2 == 0
        ):
            edge_sources.append(qubit)
            edge_targets.append(qubit + columns + 1)

observable = 0.0
for source, target in zip(edge_sources, edge_targets):
    observable += spin.z(source) * spin.z(target)

cudaq.set_target("tensornet", option="fp32")

for gamma, beta in [(0.20, 0.15), (0.31, 0.22)]:
    start = time.perf_counter()
    value = cudaq.observe(
        qaoa_layer,
        observable,
        qubit_count,
        edge_sources,
        edge_targets,
        gamma,
        beta,
    ).expectation()
    elapsed = time.perf_counter() - start
    print(f"gamma={gamma:.2f}, beta={beta:.2f}: {value:.6f} ({elapsed:.2f} s)")

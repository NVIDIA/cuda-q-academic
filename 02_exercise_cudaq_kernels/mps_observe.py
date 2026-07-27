import os
import time


# CUDA-Q reads these simulator settings when it is imported.
os.environ["CUDAQ_MPS_MAX_BOND"] = "16"  # Try "8", "32", and "64".
os.environ["CUDAQ_MPS_ABS_CUTOFF"] = "1e-6"
os.environ["CUDAQ_MPS_RELATIVE_CUTOFF"] = "1e-6"

import cudaq
from cudaq import spin


@cudaq.kernel
def qaoa_chain(
    qubit_count: int,
    gammas: list[float],
    betas: list[float],
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)

    for layer in range(len(gammas)):
        for qubit in range(qubit_count - 1):
            x.ctrl(qubits[qubit], qubits[qubit + 1])
            rz(2.0 * gammas[layer], qubits[qubit + 1])
            x.ctrl(qubits[qubit], qubits[qubit + 1])

        for qubit in range(qubit_count):
            rx(2.0 * betas[layer], qubits[qubit])


run_statevector = True
qubit_count = 24 if run_statevector else 64
layer_count = 12

observable = 0.0
for qubit in range(qubit_count - 1):
    observable += spin.z(qubit) * spin.z(qubit + 1)

gammas = [0.16 + 0.015 * (layer % 5) for layer in range(layer_count)]
betas = [0.11 + 0.02 * ((2 * layer + 1) % 5) for layer in range(layer_count)]

reference_value = None
if run_statevector:
    cudaq.set_target("nvidia", option="fp32")
    start = time.perf_counter()
    reference_value = cudaq.observe(
        qaoa_chain,
        observable,
        qubit_count,
        gammas,
        betas,
    ).expectation()
    elapsed = time.perf_counter() - start
    print(f"state vector: {reference_value:.6f} ({elapsed:.2f} s)")

cudaq.set_target("tensornet-mps", option="fp32")
start = time.perf_counter()
mps_value = cudaq.observe(
    qaoa_chain,
    observable,
    qubit_count,
    gammas,
    betas,
).expectation()
elapsed = time.perf_counter() - start
print(f"MPS: {mps_value:.6f} ({elapsed:.2f} s)")

if reference_value is not None:
    absolute_error = abs(mps_value - reference_value)
    percentage_error = 100.0 * absolute_error / abs(reference_value)
    print(f"error: {absolute_error:.6f} ({percentage_error:.2f}%)")

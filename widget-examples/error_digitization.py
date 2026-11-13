# pip install cudaq
import cudaq
import numpy as np
from collections import Counter


@cudaq.kernel
def rx_error(theta: float, error_qubit: int):
    data = cudaq.qvector(3)  # error-free state |000>
    rx(theta, data[error_qubit])  # continuous Rx(theta) error


# Error angle theta and the qubit it hits: change them and re-run.
# Qubits are numbered 0, 1, 2 here (the widget's qubits 1, 2, 3).
theta = np.radians(30)
error_qubit = 0

state = cudaq.get_state(rx_error, theta, error_qubit)
print(state)
# cos^2(theta/2): changes smoothly with theta
print("Fidelity with |000> =", abs(state[0]) ** 2)

@cudaq.kernel
def repetition_code(theta: float, error_qubit: int) -> list[int]:
    data = cudaq.qvector(3)
    ancilla = cudaq.qvector(2)
    rx(theta, data[error_qubit])

    # Stabilizer checks: ancilla 0 measures Z1Z2, ancilla 1 measures Z2Z3 (1 means -1)
    h(ancilla)
    z.ctrl(data[0], ancilla[0])
    z.ctrl(data[1], ancilla[0])
    z.ctrl(data[1], ancilla[1])
    z.ctrl(data[2], ancilla[1])
    h(ancilla)
    s0 = mz(ancilla[0])
    s1 = mz(ancilla[1])

    # Correction from the syndrome lookup table
    if s0 and s1:
        x(data[1])
    elif s0:
        x(data[0])
    elif s1:
        x(data[2])

    d0 = mz(data[0])
    d1 = mz(data[1])
    d2 = mz(data[2])
    return [s0, s1, d0, d1, d2]


results = cudaq.run(repetition_code, theta, error_qubit, shots_count=1000)
syndromes = Counter((r[0], r[1]) for r in results)
# only (0, 0) or the error qubit's syndrome
print("Syndromes:", syndromes)
print(
    "P(error detected) =",
    1 - syndromes[(0, 0)] / 1000,
    "  sin^2(theta/2) =",
    np.sin(theta / 2) ** 2,
)
# always (0, 0, 0)
print("Data after correction:", Counter((r[2], r[3], r[4]) for r in results))

# Each shot follows one branch: no error, or a full flip that gets corrected.
for result in results[:5]:
    print("syndrome", (result[0], result[1]), "-> data after correction",
          (result[2], result[3], result[4]))

# pip install cudaq
import cudaq
import numpy as np

phase = 0.625  # the phase to find: 0.101 in binary (1/2 + 0/4 + 1/8)
n_bits = 3  # counting qubits = bits of precision


@cudaq.kernel
def qft(qubits: cudaq.qview):
    n = len(qubits)
    for i in range(n):
        h(qubits[i])
        for j in range(i + 1, n):
            r1.ctrl(2 * np.pi / 2 ** (j - i + 1), qubits[j], qubits[i])

    for i in range(n // 2):
        swap(qubits[i], qubits[n - 1 - i])


@cudaq.kernel
def phase_estimation(theta: float, n: int):
    counting = cudaq.qvector(n)
    target = cudaq.qubit()
    # |1> is an eigenstate of r1, with eigenvalue e^(2*pi*i*theta)
    x(target)
    h(counting)  # Hadamard on every counting qubit
    # counting qubit i applies the gate 2^(n-1-i) times
    for i in range(n):
        r1.ctrl(2 * np.pi * theta * 2 ** (n - 1 - i), counting[i], target)

    cudaq.adjoint(qft, counting)  # the inverse QFT turns the phases into bits
    mz(counting)

results = cudaq.sample(phase_estimation, phase, n_bits, shots_count=1000)
bits = results.most_probable()  # e.g. '101', written b1 b2 b3

estimate = sum(int(b) / 2 ** (k + 1) for k, b in enumerate(bits))
terms = " + ".join(f"{b}/{2**(k + 1)}" for k, b in enumerate(bits))
print(f"Measured bits: 0.{bits} in binary")
print(f"             = {terms} = {estimate}")
print(f"Hidden phase:  {phase}")

# Match the widget: five bits estimating the target 0.3.
phase, n_bits = 0.3, 5
results = cudaq.sample(phase_estimation, phase, n_bits, shots_count=1000)
bits = results.most_probable()
estimate = sum(int(b) / 2 ** (k + 1) for k, b in enumerate(bits))
print(f"Widget target {phase}: 0.{bits} = {estimate}")

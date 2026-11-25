# pip install cudaq
import cudaq
import numpy as np


@cudaq.kernel
def qft_column(bits: list[int]):
    n = len(bits)
    qubits = cudaq.qvector(n)
    # prepare |j>, written q0 q1 q2 (q0 = most significant bit)
    for i in range(n):
        if bits[i] == 1:
            x(qubits[i])

    # QFT: Hadamards and controlled phase rotations...
    for i in range(n):
        h(qubits[i])
        for k in range(i + 1, n):
            r1.ctrl(2 * np.pi / 2 ** (k - i + 1), qubits[k], qubits[i])

    for i in range(n // 2):  # ...then reverse the qubit order
        swap(qubits[i], qubits[n - 1 - i])


def to_bits(value, n):  # e.g. to_bits(1, 3) -> [0, 0, 1]
    return [int(b) for b in format(value, f"0{n}b")]


n, j = 3, 1  # 3 qubits, so N = 8; try any j from 0 to 7
N = 2**n
print(cudaq.draw(qft_column, to_bits(j, n)))

state = cudaq.get_state(qft_column, to_bits(j, n))

for k in range(N):
    amp = state.amplitude(to_bits(k, n))
    # Convert the amplitude phase angle into a power of ω, from 0 to N-1.
    power = round(np.angle(amp) / (2 * np.pi) * N) % N
    print(
        f"|{k}>: size = {abs(amp):.3f}, phase = ω^{power}   (j*k mod {N} = {j * k % N})"
    )

# pip install cudaq-qec
import cudaq
import cudaq_qec as qec
import numpy as np

# Each row lists the data blocks included in one parity check.
H = np.array(
    [
        [1, 0, 0, 1, 0, 1, 1],
        [0, 1, 0, 1, 1, 0, 1],
        [0, 0, 1, 0, 1, 1, 1],
    ],
    dtype=np.uint8,
)


@cudaq.kernel
def outer_checks(checks: list[int], error_qubit: int, phase_error: bool) -> list[bool]:
    q = cudaq.qvector(8)  # seven data blocks and one reusable ancilla
    if phase_error:
        z(q[error_qubit])
    else:
        x(q[error_qubit])

    syndrome = [False, False, False]
    # Reuse a reset ancilla to measure each parity independently.
    for row in range(3):
        reset(q[7])
        for data in range(7):
            if checks[7 * row + data]:
                x.ctrl(q[data], q[7])
        syndrome[row] = mz(q[7])
    return syndrome


# data index 0–6; change the location or X/Z error
error_qubit, phase_error = 3, False
syndrome = cudaq.run(
    outer_checks, H.flatten().tolist(), error_qubit, phase_error, shots_count=1
)[0]

# Decode the three measured parity bits into suggested bit flips.
decoder = qec.get_decoder("single_error_lut", H)
correction = decoder.decode([float(bit) for bit in syndrome]).result

print("Outer syndrome:", [int(bit) for bit in syndrome])
print("Data qubits to flip:", np.flatnonzero(np.round(correction)))

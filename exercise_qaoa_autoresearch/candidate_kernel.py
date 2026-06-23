from typing import List

import cudaq


PARAMETER_COUNT = 6


@cudaq.kernel
def candidate_superkernel(qubits: cudaq.qview, angles: List[float]):
    x.ctrl(qubits[0], qubits[1])
    rz(2.0 * angles[0], qubits[1])
    x.ctrl(qubits[0], qubits[1])

    x.ctrl(qubits[0], qubits[6])
    rz(2.0 * angles[0], qubits[6])
    x.ctrl(qubits[0], qubits[6])

    x.ctrl(qubits[1], qubits[7])
    rz(2.0 * angles[0], qubits[7])
    x.ctrl(qubits[1], qubits[7])

    x.ctrl(qubits[1], qubits[3])
    rz(2.0 * angles[2], qubits[3])
    x.ctrl(qubits[1], qubits[3])

    x.ctrl(qubits[7], qubits[2])
    rz(2.0 * angles[2], qubits[2])
    x.ctrl(qubits[7], qubits[2])

    x.ctrl(qubits[2], qubits[4])
    rz(2.0 * angles[1], qubits[4])
    x.ctrl(qubits[2], qubits[4])

    x.ctrl(qubits[4], qubits[3])
    rz(2.0 * angles[2], qubits[3])
    x.ctrl(qubits[4], qubits[3])

    x.ctrl(qubits[3], qubits[6])
    rz(2.0 * angles[2], qubits[6])
    x.ctrl(qubits[3], qubits[6])

    x.ctrl(qubits[6], qubits[5])
    rz(2.0 * angles[1], qubits[5])
    x.ctrl(qubits[6], qubits[5])

    rx(2.0 * angles[3], qubits[0])
    rx(2.0 * angles[3], qubits[1])
    rx(2.0 * angles[4], qubits[2])
    rx(2.0 * angles[5], qubits[3])
    rx(2.0 * angles[4], qubits[4])
    rx(2.0 * angles[4], qubits[5])
    rx(2.0 * angles[5], qubits[6])
    rx(2.0 * angles[3], qubits[7])

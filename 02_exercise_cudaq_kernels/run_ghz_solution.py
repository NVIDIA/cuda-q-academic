import cudaq


@cudaq.kernel
def resets_until_111() -> int:
    qubits = cudaq.qvector(3)
    resets = 0
    prepared = False

    while not prepared:
        h(qubits[0])
        x.ctrl(qubits[0], qubits[1])
        x.ctrl(qubits[1], qubits[2])

        bit_0 = mz(qubits[0])
        bit_1 = mz(qubits[1])
        bit_2 = mz(qubits[2])
        prepared = bit_0 and bit_1 and bit_2

        if not prepared:
            reset(qubits)
            resets += 1

    return resets


results = cudaq.run(resets_until_111, shots_count=10)
print(results)

import cudaq


@cudaq.kernel
def resets_until_111() -> #TODO add retunr variable type:
    qubits = cudaq.qvector(3)
    resets = 0
    prepared = False

    while not prepared:
        h(qubits[0])
        x.ctrl(qubits[0], qubits[1])
        x.ctrl(qubits[1], qubits[2])

````````#TODO measure individual qubits
        #TODO determine "pepared"/  =1 if |111> was prepared

        if not prepared:
            reset(qubits)
            resets += 1

    return resets


results = cudaq.run(resets_until_111, shots_count=10)
print(results)

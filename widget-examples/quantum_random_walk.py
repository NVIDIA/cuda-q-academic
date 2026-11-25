# pip install cudaq
import cudaq


@cudaq.kernel
def INC(qubits: cudaq.qview):  # position x -> x + 1
    x.ctrl([qubits[3], qubits[2], qubits[1]], qubits[0])
    x.ctrl([qubits[3], qubits[2]], qubits[1])
    x.ctrl(qubits[3], qubits[2])
    x(qubits[3])


@cudaq.kernel
def DEC(qubits: cudaq.qview):  # position x -> x - 1 (INC in reverse)
    x(qubits[3])
    x.ctrl(qubits[3], qubits[2])
    x.ctrl([qubits[3], qubits[2]], qubits[1])
    x.ctrl([qubits[3], qubits[2], qubits[1]], qubits[0])


@cudaq.kernel
def quantum_walk(start_coin: int, steps: int):
    walker = cudaq.qvector(4)  # positions 0 to 15
    coin = cudaq.qubit()
    x(walker[0])  # start at 8, the widget's position 0
    if start_coin == 1:
        x(coin)
    for i in range(steps):
        h(coin)  # flip the coin
        cudaq.control(INC, coin, walker)  # coin |1>: step right

        # Temporarily flip the coin to control the left step on |0>.
        x(coin)
        cudaq.control(DEC, coin, walker)  # coin |0>: step left
        x(coin)

    mz(walker)


# Initial coin state (0 or 1) and steps (1 to 5, as in the widget).
start_coin = 1
steps = 5
assert (
    start_coin in (0, 1) and 1 <= steps <= 5
), "Use coin 0 or 1 and 1–5 steps; the position register is finite."
print(cudaq.draw(quantum_walk, start_coin, 1))  # one step of the circuit

counts = cudaq.sample(quantum_walk, start_coin, steps)
for bits in sorted(counts, key=lambda b: int(b, 2)):
    print(f"position {int(bits, 2) - 8:+d}: {counts.probability(bits):.3f}")

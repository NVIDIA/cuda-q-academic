# pip install cudaq
import cudaq
import math


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
def split_step_walk(steps: int, theta_left: float, theta_right: float):
    walker = cudaq.qvector(4)  # positions 0 to 15
    coins = cudaq.qvector(2 * steps)  # a fresh coin for every flip
    x(walker[0])  # register value 8 = the widget's center position 4
    for i in range(steps):
        ry(theta_left, coins[2 * i])  # part 1: |1> with probability p_left
        # ... move left, otherwise stay
        cudaq.control(DEC, coins[2 * i], walker)

        ry(theta_right, coins[2 * i + 1])  # part 2: |1> with probability p_right
        # ... move right, otherwise stay
        cudaq.control(INC, coins[2 * i + 1], walker)

    mz(walker)


# Steps (1 to 4) and the widget's two probability sliders (0 to 1).
steps = 4
p_left, p_right = 0.5, 0.5
assert 1 <= steps <= 4, "Use 1–4 steps; the position register is finite."
assert 0 <= p_left <= 1 and 0 <= p_right <= 1, "Probabilities must be between 0 and 1."

# ry(theta) gives |1> with probability sin^2(theta/2)
theta_left = 2 * math.asin(math.sqrt(p_left))
theta_right = 2 * math.asin(math.sqrt(p_right))

counts = cudaq.sample(split_step_walk, steps, theta_left, theta_right)
for bits in sorted(counts, key=lambda b: int(b, 2)):
    print(f"position {int(bits, 2) - 4}: {counts.probability(bits):.3f}")

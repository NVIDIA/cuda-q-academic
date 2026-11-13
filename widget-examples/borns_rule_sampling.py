# pip install cudaq qutip matplotlib
import cudaq
import numpy as np


@cudaq.kernel
def qubit_state(theta: float, phi: float):
    qubit = cudaq.qubit()  # starts in |0>
    ry(theta, qubit)  # θ sets the measurement odds: P(0) = cos²(θ/2)
    r1(phi, qubit)  # φ sets the relative phase; probabilities don't change


# Change these to any angles (in radians) and re-run.
# Try phi at a few values: the arrow spins around the z-axis, but P(0) and P(1)
# don't change. Only theta affects the measurement odds.
theta, phi = np.pi / 3, np.pi / 4

# Born's rule: P(x) = |amplitude of x|^2
state = cudaq.get_state(qubit_state, theta, phi)
for bit in ('0', '1'):
    amp = state.amplitude(bit)
    print(f"|{bit}>: amplitude = {amp:.3f}, P = {abs(amp)**2:.3f}")

cudaq.show(cudaq.add_to_bloch_sphere(state))

print(f"Born's rule predicts P(0) = {abs(state.amplitude('0'))**2:.3f}\n")

# Each shot returns 0 or 1. More shots generally improve the probability estimates.
for shots in (1, 10, 1000):
    results = cudaq.sample(qubit_state, theta, phi, shots_count=shots)
    zeros, ones = results.count('0'), results.count('1')
    print(
        f"{shots:>4} shots: {zeros:>4} zeros, {ones:>4} ones"
        f"  ->  sampled P(0) = {zeros / shots:.3f}"
    )

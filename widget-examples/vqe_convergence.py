# pip install cudaq
import cudaq
import numpy as np
from cudaq import spin

hamiltonian = spin.z(0)  # H = Z, the same Hamiltonian as the widget


@cudaq.kernel
def ansatz(angles: list[float]):
    qubit = cudaq.qvector(1)  # starts in |0>
    ry(angles[0], qubit[0])  # one parameter for the optimizer to tune


# <H> for a few angles: for this ansatz the energy is cos(theta)
for theta in (0.0, np.pi / 2, np.pi):
    energy = cudaq.observe(ansatz, hamiltonian, [theta]).expectation()
    print(f"theta = {theta:.3f}  ->  <H> = {energy:+.3f}")

# Each step: the QPU (here a simulator) measures <H>, the optimizer suggests the next
# theta
history = []


def cost(angles):
    energy = cudaq.observe(ansatz, hamiltonian, angles).expectation()
    history.append(energy)
    print(f"step {len(history):>2}: theta = {angles[0]:+.3f}  ->  <H> = {energy:+.4f}")
    return energy


optimizer = cudaq.optimizers.COBYLA()
optimizer.initial_parameters = [0.5]  # starting guess for theta
# increase to allow more optimization steps
optimizer.max_iterations = 20

energy, angles = optimizer.optimize(dimensions=1, function=cost)
print(f"\nLowest energy found: {energy:.4f} at theta = {angles[0]:.3f}")
print("Exact answer: -1 at theta = ±pi (the state |1>)")

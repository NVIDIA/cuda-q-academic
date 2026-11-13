# pip install cudaq qutip matplotlib
import cudaq
import numpy as np


# 1. Put built-in gates into a circuit
# CUDA-Q's single-qubit gates (x, y, z, h, s, t, ...) are ready to use.
# Each line adds one gate; gates are applied top to bottom.
@cudaq.kernel
def circuit():
    qubit = cudaq.qubit()  # starts in |0>
    h(qubit)
    s(qubit)
    t(qubit)


print(cudaq.draw(circuit))  # the circuit so far

# 2. Define your own gate from a matrix and add it to the circuit
# The matrix must be unitary (U times its conjugate transpose = identity),
# like every quantum gate.
# Here: square root of X, a half bit-flip (applying it twice equals x).
sqrt_x_matrix = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])
cudaq.register_operation("sqrt_x", sqrt_x_matrix)


@cudaq.kernel
def circuit_with_custom_gate():
    qubit = cudaq.qubit()  # starts in |0>
    h(qubit)
    s(qubit)
    t(qubit)
    sqrt_x(qubit)  # custom gates are used just like built-in ones

# 3. Visualize the circuit and show its output state on the Bloch sphere
print(cudaq.draw(circuit_with_custom_gate))
state = cudaq.get_state(circuit_with_custom_gate)
cudaq.show(cudaq.add_to_bloch_sphere(state))

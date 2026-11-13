# pip install cudaq qutip matplotlib
import cudaq
import numpy as np


@cudaq.kernel
def rotations(theta_x: float, theta_y: float, theta_z: float):
    qubit = cudaq.qubit()  # starts in |0>
    rx(theta_x, qubit)
    ry(theta_y, qubit)
    rz(theta_z, qubit)


# Rotation angles in radians (π/2 = 90°); try any values
theta_x, theta_y, theta_z = np.pi / 2, np.pi / 4, np.pi / 3

print(cudaq.draw(rotations, theta_x, theta_y, theta_z))
state = cudaq.get_state(rotations, theta_x, theta_y, theta_z)
cudaq.show(cudaq.add_to_bloch_sphere(state))

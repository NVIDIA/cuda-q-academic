# pip install cudaq
import cudaq
from cudaq import spin
import numpy as np


@cudaq.kernel
def clifford_chain():  # Ex 1
    q = cudaq.qvector(3)
    h(q[0])
    x.ctrl(q[0], q[1])
    s(q[1])
    x.ctrl(q[1], q[2])
    h(q[2])


@cudaq.kernel
def varying_rotations(theta0: float, theta1: float):  # Ex 2
    q = cudaq.qvector(3)
    rx(theta0, q[0])
    x.ctrl(q[0], q[1])
    rx(theta1, q[1])
    x.ctrl(q[1], q[2])

# The widget's initial observable on Q0 Q1 Q2: change the Paulis (spin.x, spin.y,
# spin.z) and re-run.
observable = spin.x(0) * spin.x(1) * spin.y(2)

print("Ex 1:", cudaq.observe(clifford_chain, observable).expectation())
print(
    "Ex 2:",
    cudaq.observe(varying_rotations, observable, np.pi / 4, np.pi / 8).expectation(),
)

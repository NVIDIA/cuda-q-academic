# pip install cudaq
import cudaq
from cudaq import spin


@cudaq.kernel
def qaoa_triangle(alpha: float, beta: float):
    qubits = cudaq.qvector(3)  # one qubit per node
    h(qubits)  # all 8 colorings equally likely
    for i in range(3):  # cost layer: exp(-i alpha * cut), matching the widget
        x.ctrl(qubits[i], qubits[(i + 1) % 3])
        rz(-alpha, qubits[(i + 1) % 3])
        x.ctrl(qubits[i], qubits[(i + 1) % 3])

    rx(2.0 * beta, qubits)  # mixer layer


# Cost angle alpha and mixer angle beta: change them and re-run.
# At (0, 0) the qubits stay in an equal superposition of all 8 colorings.
alpha, beta = -0.6, 1.26
print(cudaq.draw(qaoa_triangle, alpha, beta))

counts = cudaq.sample(qaoa_triangle, alpha, beta)
# 000 and 111 cut no edges; every other coloring cuts 2 of the 3 (the max cut)
print(counts)

# Max Cut Hamiltonian: H = 1/2 * sum_edges (Z_u Z_v - 1).
# Its expectation is the energy badge; -2 is the triangle's minimum.
hamiltonian = -1.5 + 0.5 * (
    spin.z(0) * spin.z(1) + spin.z(1) * spin.z(2) + spin.z(2) * spin.z(0)
)
print("<H> =", cudaq.observe(qaoa_triangle, hamiltonian, alpha, beta).expectation())

# The widget's P(Good Cut): the fraction of shots that are a maximum cut
print("P(good cut) =", 1 - counts.probability('000') - counts.probability('111'))

# pip install cudaq==0.15.1 cudaq-algorithms==0.1.0 pyscf
import cudaq
import cudaq_algorithms as algorithms
import numpy as np
from pyscf import gto, scf

# H2 in the STO-3G basis (4 qubits), its qubit Hamiltonian, and the operator pool
mean_field = scf.RHF(
    gto.M(atom="H 0 0 0; H 0 0 0.7474", basis="sto-3g", verbose=0)
).run()
one_body, two_body, nuclear_energy = algorithms.chemistry.from_pyscf(mean_field)
H = algorithms.chemistry.qubit_hamiltonian(
    one_body, two_body, scalar_offset=nuclear_energy
)
pool = algorithms.stateprep.make_uccgsd_operator_pool(4)


@cudaq.kernel
def ansatz(theta: float, words: list[cudaq.pauli_word], coefficients: list[float]):
    q = cudaq.qvector(4)
    x(q[0])  # Hartree-Fock state |1100>: 2 electrons
    x(q[1])
    # exp(i theta A) for the chosen operator A
    for k in range(len(words)):
        exp_pauli(theta * coefficients[k], q, words[k])


# Gradient of each pool operator A at the Hartree-Fock state: the expectation of i[H, A]
gradients = [
    cudaq.observe(ansatz, 1j * (H * A - A * H), 0.0, [], []).expectation() for A in pool
]

# Choose the operator with the largest gradient magnitude.
best = pool[int(np.argmax(np.abs(gradients)))]

# Express the selected operator as Pauli words and their weights.
words = [cudaq.pauli_word(term.get_pauli_word(4)) for term in best]
coefficients = [term.evaluate_coefficient().real for term in best]

# the numbers beside the widget's A_n
print("Gradient of each pool operator:", np.round(np.abs(gradients), 3))

# Optimize the selected excitation angle.
energy, theta = cudaq.optimizers.COBYLA().optimize(
    1, lambda t: cudaq.observe(ansatz, H, t[0], words, coefficients).expectation()
)
print(
    "Energy: Hartree-Fock",
    cudaq.observe(ansatz, H, 0.0, [], []).expectation(),
    "-> after one ADAPT step",
    energy,
)


@cudaq.kernel
# standard VQE: every excitation in the circuit from the start
def uccsd(thetas: list[float]):
    q = cudaq.qvector(4)
    x(q[0])
    x(q[1])
    algorithms.stateprep.uccsd(q, thetas, 2, 0)


n = algorithms.stateprep.get_num_uccsd_parameters(4, 2)

vqe_energy, _ = cudaq.optimizers.COBYLA().optimize(
    n, lambda t: cudaq.observe(uccsd, H, list(t)).expectation()
)
print(
    f"Standard VQE: {n} parameters -> {vqe_energy:.6f}   ADAPT-VQE: 1 parameter -> {energy:.6f}"
)

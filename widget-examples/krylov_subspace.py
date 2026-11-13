# pip install cudaq==0.15.1 cudaq-algorithms==0.1.0 pyscf
import cudaq
import cudaq_algorithms as algorithms
import numpy as np
from cudaq_algorithms import trotter
from pyscf import gto, scf

# H2 in the 6-31G basis: 8 qubits, as in the lesson
mean_field = scf.RHF(gto.M(atom="H 0 0 0; H 0 0 0.7474", basis="631g", verbose=0)).run()
one_body, two_body, nuclear_energy = algorithms.chemistry.from_pyscf(mean_field)
H = algorithms.chemistry.qubit_hamiltonian(
    one_body, two_body, scalar_offset=nuclear_energy
)


@cudaq.kernel
def hartree_fock(qubits: cudaq.qview):  # 2 electrons in the lowest spin orbitals
    x(qubits[0])
    x(qubits[1])


evolution = trotter.Trotter(H)
# time step between Krylov states: change it and re-run
dt = 0.5

# Form six Krylov vectors by evolving the reference state.
states = [
    np.array(
        cudaq.get_state(
            evolution.kernel(time=k * dt, steps=k + 1, state_prep=hartree_fock)
        )
    )
    for k in range(6)
]

# Project H into growing, orthonormal Krylov subspaces.
H_matrix = np.array(H.to_matrix())
for m in range(1, 7):  # subspace size, the widget's slider
    s, U = np.linalg.eigh(
        np.conj(np.column_stack(states[:m])).T @ np.column_stack(states[:m])
    )
    # orthonormal subspace basis
    basis = np.column_stack(states[:m]) @ U[:, s > 1e-8] / np.sqrt(s[s > 1e-8])
    print(
        f"subspace size {m}: E = {np.linalg.eigvalsh(basis.conj().T @ H_matrix @ basis).min():.6f}"
    )

print("exact:", np.linalg.eigvalsh(H_matrix).min())

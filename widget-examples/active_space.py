# pip install cudaq==0.15.1 cudaq-algorithms==0.1.0 pyscf
import cudaq
import cudaq_algorithms as algorithms
from pyscf import gto, scf, mcscf, ao2mo

# NH3 in the 6-31G basis, as in the widget (geometry from the QM/MM lesson)
geometry = (
    "N 0.000 0.000 0.000; H -0.114 -0.009 0.990; "
    "H -0.437 -0.825 -0.358; H 0.942 -0.010 -0.222"
)
# Compute reference orbitals with restricted Hartree-Fock.
mf = scf.RHF(gto.M(atom=geometry, basis="631g", verbose=0)).run()

for i, (energy, electrons) in enumerate(zip(mf.mo_energy, mf.mo_occ)):
    print(f"orbital {i:2d}: {energy:8.3f} Ha, {int(electrons)} electrons")

# The widget's default active space: 4 electrons in 4 orbitals around the HOMO-LUMO gap.
# Change it and re-run.
n_electrons, n_orbitals = 4, 4

cas = mcscf.CASCI(mf, n_orbitals, n_electrons)
# core orbitals are frozen into e_core and h1
h1, e_core = cas.get_h1eff()
h2 = ao2mo.restore(1, cas.get_h2eff(), n_orbitals)  # active-space (pq|rs) integrals
# Jordan-Wigner qubit Hamiltonian
H = algorithms.chemistry.qubit_hamiltonian(h1, h2, scalar_offset=e_core)


@cudaq.kernel
def hartree_fock(n_qubits: int, n_electrons: int):
    q = cudaq.qvector(n_qubits)
    for i in range(n_electrons):
        # fill the lowest spin orbitals (spin up/down interleaved)
        x(q[i])


# Each spatial orbital needs two spin-orbital qubits.
n_qubits = 2 * n_orbitals
print("Qubits:", n_qubits, " Hamiltonian terms:", H.term_count)
print(
    "Hartree-Fock energy, CUDA-Q:",
    cudaq.observe(hartree_fock, H, n_qubits, n_electrons).expectation(),
)
print("Hartree-Fock energy, PySCF: ", mf.e_tot)

# A bigger active space recovers more correlation energy, but needs more qubits
for n_e, n_o in [(2, 2), (4, 4), (6, 6), (8, 8)]:
    energy = mcscf.CASCI(mf, n_o, n_e).run().e_tot
    print(
        f"({n_e}e, {n_o}o): {2 * n_o:2d} qubits, correlation energy {energy - mf.e_tot:.4f} Ha"
    )

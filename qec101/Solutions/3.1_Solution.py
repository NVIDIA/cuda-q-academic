import cudaq
import numpy as np

cudaq.set_target("density-matrix-cpu")

@cudaq.kernel
def test():
    reg = cudaq.qvector(3)
    h(reg)

print("State vector:")
print(cudaq.get_state(test))

# get density matrix
rho = np.array(cudaq.get_state(test))

# Compute Trace
print("\\nTrace(rho) =", np.trace(rho))

# Check Hermitian
print("Hermitian?", np.allclose(rho, rho.conj().T, atol=1e-12))

# Check positive semi-definite
eigs, _ = np.linalg.eig(rho)
eigs[np.abs(eigs) < 1e-12] = 0
print("Eigenvalues:", eigs)
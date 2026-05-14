import cudaq
from aux_files.qmmm.qchem.uccsd import get_uccsd_op, uccsd_circuit
from aux_files.qmmm.qchem.uccsd import uccsd_circuit_double, uccsd_circuit_single

import numpy as np
from scipy.optimize import minimize

cudaq.set_target("nvidia", option='fp64')


def uccsd_circuit_vqe(spin_mult,
                      only_singles,
                      only_doubles,
                      qubits_num,
                      electron_count,
                      optimize,
                      theta,
                      hamiltonian,
                      method='BFGS',
                      vqe_tol=1e-3,
                      verbose=False):
    """
    Generate the UCCSD circuit for VQE.
    
    Parameters:
    - spin_`mult`: Spin multiplicity of the system.
    - only_singles: If True, only single excitations are included.
    - only_doubles: If True, only double excitations are included.
    - qubits_`num`: Number of qubits in the system.
    - electron_count: Number of electrons in the system.
    - theta: Initial parameters for the circuit.
    - hamiltonian: Hamiltonian of the system.
    """

    # Get the UCCSD pool
    if not only_singles and not only_doubles:
        word_single, word_double, coef_single, coef_double = get_uccsd_op(
            electron_count,
            qubits_num,
            spin_mult=0,
            only_singles=False,
            only_doubles=False)
        if verbose:
            print(f"word_single: {word_single}")
            print(f"word_double: {word_double}")
            print(f"coef_single: {coef_single}")
            print(f"coef_double: {coef_double}")

    elif only_singles and not only_doubles:
        word_single, coef_single = get_uccsd_op(electron_count,
                                                qubits_num,
                                                spin_mult=0,
                                                only_singles=True,
                                                only_doubles=False)

        if verbose:
            print(f"word_single: {word_single}")
            print(f"coef_single: {coef_single}")

    elif only_doubles and not only_singles:
        word_double, coef_double = get_uccsd_op(electron_count,
                                                qubits_num,
                                                spin_mult=0,
                                                only_singles=False,
                                                only_doubles=True)

        if verbose:
            print(f"word_double: {word_double}")
            print(f"coef_double: {coef_double}")
    else:
        raise ValueError("Invalid option for only_singles and only_doubles")

    # Get the UCCSD circuit (singles and doubles excitation are included)
    @cudaq.kernel
    def uccsd_kernel(qubits_num: int, electron_count: int, theta: list[float],
                     word_single: list[cudaq.pauli_word],
                     word_double: list[cudaq.pauli_word],
                     coef_single: list[float], coef_double: list[float]):
        """
        UCCSD kernel
        """
        # `Prepare the statefrom qchem.uccsd import get_uccsd_op, uccsd_circuit, uccsd_parameter_size`

        qubits = cudaq.qvector(qubits_num)

        # Initialize the qubits
        for i in range(electron_count):
            x(qubits[i])

        # Apply the UCCSD circuit
        uccsd_circuit(qubits, theta, word_single, coef_single, word_double,
                      coef_double)

    # Get the UCCSD circuit (only doubles excitations are included)
    @cudaq.kernel
    def uccsd_double_kernel(qubits_num: int, electron_count: int,
                            theta: list[float],
                            word_double: list[cudaq.pauli_word],
                            coef_double: list[float]):
        """
        UCCSD kernel
        """
        # Prepare the state
        qubits = cudaq.qvector(qubits_num)

        # Initialize the qubits
        for i in range(electron_count):
            x(qubits[i])

        # Apply the UCCSD circuit
        uccsd_circuit_double(qubits, theta, word_double, coef_double)

    # Get the UCCSD circuit (only singles excitations are included)
    @cudaq.kernel
    def uccsd_single_kernel(qubits_num: int, electron_count: int,
                            theta: list[float],
                            word_single: list[cudaq.pauli_word],
                            coef_single: list[float]):
        """
        UCCSD kernel
        """
        # Prepare the state
        qubits = cudaq.qvector(qubits_num)

        # Initialize the qubits
        for i in range(electron_count):
            x(qubits[i])

        # Apply the UCCSD circuit
        uccsd_circuit_single(qubits, theta, word_single, coef_single)

    def cost(theta):

        theta = theta.tolist()

        if not only_singles and not only_doubles:
            energy = cudaq.observe(uccsd_kernel, hamiltonian, qubits_num,
                                   electron_count, theta, word_single,
                                   word_double, coef_single,
                                   coef_double).expectation()


        elif only_singles and not only_doubles:
            energy = cudaq.observe(uccsd_single_kernel, hamiltonian, qubits_num,
                                   electron_count, theta, word_single,
                                   coef_single).expectation()

        elif only_doubles and not only_singles:
            energy = cudaq.observe(uccsd_double_kernel, hamiltonian, qubits_num,
                                   electron_count, theta, word_double,
                                   coef_double).expectation()

        else:
            raise ValueError("Invalid option for only_singles and only_doubles")

        return energy

    # TEMPORARY (cuda-quantum 0.14.x): central-difference gradient that
    # evaluates all 2N perturbed parameter vectors in a single broadcasted
    # cudaq.observe call instead of 2N separate calls. Works around a
    # per-call dispatch regression introduced in cuda-quantum 0.14.0
    # (~50 ms/call vs <1 ms in 0.13.0); without it, scipy's default
    # jac='3-point' fires hundreds of observe calls per L-BFGS-B iteration
    # and the optimizer takes tens of minutes. Remove once the upstream
    # dispatch regression is fixed.
    def batched_gradient(theta_np):
        h = 1e-6
        n_params = len(theta_np)
        # batch shape: (2*n_params, n_params); row 2i = theta + h*e_i, row 2i+1 = theta - h*e_i
        batch = np.tile(theta_np, (2 * n_params, 1)).astype(np.float64)
        for i in range(n_params):
            batch[2 * i, i]     += h
            batch[2 * i + 1, i] -= h
        Nb = 2 * n_params
        if not only_singles and not only_doubles:
            results = cudaq.observe(
                uccsd_kernel, hamiltonian,
                [qubits_num] * Nb, [electron_count] * Nb, batch,
                [word_single] * Nb, [word_double] * Nb,
                [coef_single] * Nb, [coef_double] * Nb)
        elif only_singles and not only_doubles:
            results = cudaq.observe(
                uccsd_single_kernel, hamiltonian,
                [qubits_num] * Nb, [electron_count] * Nb, batch,
                [word_single] * Nb, [coef_single] * Nb)
        else:  # only_doubles
            results = cudaq.observe(
                uccsd_double_kernel, hamiltonian,
                [qubits_num] * Nb, [electron_count] * Nb, batch,
                [word_double] * Nb, [coef_double] * Nb)
        expvals = np.array([r.expectation() for r in results])
        return (expvals[0::2] - expvals[1::2]) / (2 * h)

    if optimize:
        if method == 'L-BFGS-B':
            result_vqe = minimize(cost,
                                  theta,
                                  method='L-BFGS-B',
                                  jac=batched_gradient,
                                  tol=vqe_tol)
            print('Optimizer exited successfully: ',
                  result_vqe.success,
                  flush=True)
        elif method == 'BFGS':
            result_vqe = minimize(cost,
                                  theta,
                                  method='BFGS',
                                  jac=batched_gradient,
                                  options={'gtol': 1e-5})
            print('Optimizer exited successfully: ',
                  result_vqe.success,
                  flush=True)
        elif method == 'COBYLA':
            result_vqe = minimize(cost,
                                  theta,
                                  method='COBYLA',
                                  options={
                                      'rhobeg': 1.0,
                                      'maxiter': 20000,
                                      'disp': False,
                                      'tol': vqe_tol
                                  })
        else:
            raise ValueError(
                "Invalid optimization method. Use 'L-BFGS-B', 'BFGS', or 'COBYLA'."
            )

        total_energy = result_vqe.fun

        if verbose:
            print(f"Total energy: {total_energy:.10f} Hartree")
        # Print the optimized parameters: first n are singles, then doubles.
        if verbose:
            print(f"optimized parameters: {result_vqe.x}")

        return (result_vqe.fun, result_vqe.x, result_vqe.success, np.array(cudaq.get_state(uccsd_kernel, qubits_num,
                                   electron_count,result_vqe.x, word_single,
                                   word_double, coef_single,
                                   coef_double)))

    else:
        total_energy = cudaq.observe(uccsd_kernel, hamiltonian, qubits_num,
                                   electron_count, theta, word_single,
                                   word_double, coef_single,
                                   coef_double).expectation()
        if verbose:
            print(f"Total energy: {total_energy:.10f} Hartree")

            print(np.array(cudaq.get_state(uccsd_kernel, qubits_num,
                                   electron_count,theta, word_single,
                                   word_double, coef_single,
                                   coef_double)))

            print(cudaq.get_state(uccsd_kernel, qubits_num,
                                   electron_count,theta, word_single,
                                   word_double, coef_single,
                                   coef_double))

        return (total_energy, theta, True, np.array(cudaq.get_state(uccsd_kernel, qubits_num,
                                   electron_count,theta, word_single,
                                   word_double, coef_single,
                                   coef_double)) )
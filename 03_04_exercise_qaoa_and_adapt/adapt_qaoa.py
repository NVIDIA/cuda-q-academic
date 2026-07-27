import random

import cudaq
import numpy as np
from cudaq import spin
from scipy.optimize import minimize

from workshop_graphs import EDGE_WEIGHTS, EDGES, NUM_QUBITS


# 1. LOAD THE SELECTED WORKSHOP GRAPH
INITIAL_GAMMA = 0.01
GRADIENT_THRESHOLD = 1e-3
ENERGY_THRESHOLD = 1e-7
RANDOM_SEED = 42
SAMPLE_SHOTS = 5000


# 2. BUILD THE WEIGHTED MAX-CUT HAMILTONIAN
def maxcut_hamiltonian(edges, edge_weights):
    hamiltonian = 0
    for (source, target), weight in zip(edges, edge_weights):
        hamiltonian += 0.5 * weight * (
            spin.z(source) * spin.z(target)
            - spin.i(source) * spin.i(target)
        )
    return hamiltonian


def term_coefficients(hamiltonian):
    return [
        term.evaluate_coefficient()
        for term in hamiltonian
    ]


def term_words(hamiltonian, qubit_count):
    return [
        term.get_pauli_word(qubit_count)
        for term in hamiltonian
    ]


# 3. BUILD THE ADAPT-QAOA MIXER POOL
def qaoa_mixer(qubit_count):
    operator = spin.x(0)
    for qubit in range(1, qubit_count):
        operator += spin.x(qubit)
    return [operator]


def qaoa_single_x(qubit_count):
    return [
        cudaq.SpinOperator(spin.x(qubit))
        for qubit in range(qubit_count)
    ]


def qaoa_double_operators(qubit_count):
    pool = []
    for first in range(qubit_count - 1):
        for second in range(first + 1, qubit_count):
            first_x = cudaq.SpinOperator(spin.x(first))
            first_y = cudaq.SpinOperator(spin.y(first))
            first_z = cudaq.SpinOperator(spin.z(first))
            second_x = cudaq.SpinOperator(spin.x(second))
            second_y = cudaq.SpinOperator(spin.y(second))
            second_z = cudaq.SpinOperator(spin.z(second))
            pool.append(first_x * second_x)
            pool.append(first_y * second_y)
            pool.append(first_y * second_z)
            pool.append(first_z * second_y)
    return pool


def mixer_pool(qubit_count):
    return (
        qaoa_single_x(qubit_count)
        + qaoa_mixer(qubit_count)
        + qaoa_double_operators(qubit_count)
    )


def commutators(pool, hamiltonian):
    return [
        hamiltonian * operator - operator * hamiltonian
        for operator in pool
    ]


# 4. BUILD THE ADAPT-QAOA QUANTUM KERNELS
@cudaq.kernel
def initial_state(qubit_count: int):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)


@cudaq.kernel
def gradient_state(
    state: cudaq.State,
    hamiltonian_words: list[cudaq.pauli_word],
    hamiltonian_coefficients: list[complex],
    initial_gamma: float,
):
    qubits = cudaq.qvector(state)
    for term in range(len(hamiltonian_coefficients)):
        exp_pauli(
            initial_gamma * hamiltonian_coefficients[term].real,
            qubits,
            hamiltonian_words[term],
        )


@cudaq.kernel
def adapt_qaoa_kernel(
    qubit_count: int,
    hamiltonian_words: list[cudaq.pauli_word],
    hamiltonian_coefficients: list[complex],
    selected_mixers: list[list[cudaq.pauli_word]],
    gamma: list[float],
    beta: list[float],
    layer_count: int,
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)

    for layer in range(layer_count):
        for term in range(len(hamiltonian_coefficients)):
            exp_pauli(
                gamma[layer] * hamiltonian_coefficients[term].real,
                qubits,
                hamiltonian_words[term],
            )

        for mixer_word in selected_mixers[layer]:
            exp_pauli(beta[layer], qubits, mixer_word)


# 5. GROW AND OPTIMIZE THE ADAPT-QAOA CIRCUIT
def solve_adapt_qaoa():
    hamiltonian = maxcut_hamiltonian(EDGES, EDGE_WEIGHTS)
    hamiltonian_coefficients = term_coefficients(hamiltonian)
    hamiltonian_words = term_words(hamiltonian, NUM_QUBITS)

    pool = mixer_pool(NUM_QUBITS)
    gradient_operators = commutators(pool, hamiltonian)
    state = cudaq.get_state(initial_state, NUM_QUBITS)

    gamma = []
    beta = []
    selected_mixers = []
    previous_energy = 0.0
    final_energy = previous_energy
    step = 1

    while True:
        print("Step:", step)

        gradient_vector = []
        for operator in gradient_operators:
            gradient = cudaq.observe(
                gradient_state,
                -1j * operator,
                state,
                hamiltonian_words,
                hamiltonian_coefficients,
                INITIAL_GAMMA,
            ).expectation()
            gradient_vector.append(gradient)

        gradient_norm = np.linalg.norm(np.array(gradient_vector))
        print("Gradient norm:", gradient_norm)

        if gradient_norm <= GRADIENT_THRESHOLD:
            break

        maximum_gradient = np.max(np.abs(gradient_vector))
        candidates = [
            pool[index]
            for index, gradient in enumerate(gradient_vector)
            if np.abs(gradient) >= maximum_gradient
        ]

        random.seed(RANDOM_SEED)
        selected_operator = random.choice(candidates)
        selected_mixers.append(
            [
                term.get_pauli_word(NUM_QUBITS)
                for term in selected_operator
            ]
        )

        gamma.append(INITIAL_GAMMA)
        beta.append(0.0)
        layer_count = len(selected_mixers)
        initial_parameters = gamma + beta

        def objective(parameters):
            parameter_list = parameters.tolist()
            current_gamma = parameter_list[:layer_count]
            current_beta = parameter_list[layer_count:]
            return cudaq.observe(
                adapt_qaoa_kernel,
                hamiltonian,
                NUM_QUBITS,
                hamiltonian_words,
                hamiltonian_coefficients,
                selected_mixers,
                current_gamma,
                current_beta,
                layer_count,
            ).expectation()

        result = minimize(
            objective,
            initial_parameters,
            method="BFGS",
            jac="2-point",
            tol=1e-5,
        )

        final_energy = result.fun
        energy_change = abs(final_energy - previous_energy)
        previous_energy = final_energy

        optimized_parameters = result.x.tolist()
        gamma = optimized_parameters[:layer_count]
        beta = optimized_parameters[layer_count:]

        print("Optimized energy:", final_energy)
        print("Energy change:", energy_change)

        if energy_change <= ENERGY_THRESHOLD:
            break

        state = cudaq.get_state(
            adapt_qaoa_kernel,
            NUM_QUBITS,
            hamiltonian_words,
            hamiltonian_coefficients,
            selected_mixers,
            gamma,
            beta,
            layer_count,
        )
        step += 1

    print("Selected mixers:", selected_mixers)
    print("Number of layers:", len(selected_mixers))
    print("Final energy:", final_energy)
    return final_energy, gamma, beta, selected_mixers


def set_simulator_target():
    """Use the ADAPT-QAOA tutorial's double-precision simulator setup."""
    if cudaq.num_available_gpus() > 0 and cudaq.has_target("nvidia"):
        cudaq.set_target("nvidia", option="fp64")
    else:
        print("NVIDIA GPU unavailable; using qpp-cpu instead.")
        cudaq.set_target("qpp-cpu")


# 6. SAMPLE THE BEST CIRCUIT
def main():
    set_simulator_target()
    best_energy, gamma, beta, selected_mixers = solve_adapt_qaoa()

    hamiltonian = maxcut_hamiltonian(EDGES, EDGE_WEIGHTS)
    hamiltonian_coefficients = term_coefficients(hamiltonian)
    hamiltonian_words = term_words(hamiltonian, NUM_QUBITS)

    counts = cudaq.sample(
        adapt_qaoa_kernel,
        NUM_QUBITS,
        hamiltonian_words,
        hamiltonian_coefficients,
        selected_mixers,
        gamma,
        beta,
        len(selected_mixers),
        shots_count=SAMPLE_SHOTS,
    )
    best_bitstring = max(counts.items(), key=lambda item: item[1])[0]

    print("Best gamma parameters:", gamma)
    print("Best beta parameters:", beta)
    print("Estimated maximum cut:", -best_energy)
    print("Most frequent bitstring:", best_bitstring)
    print("Sample counts:", counts)


if __name__ == "__main__":
    main()

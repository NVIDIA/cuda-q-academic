import cudaq
from cudaq import spin
from scipy.optimize import minimize

from workshop_graphs import EDGE_WEIGHTS, EDGES, NUM_QUBITS


# 1. LOAD THE SELECTED WORKSHOP GRAPH
EDGE_SOURCES = [source for source, _ in EDGES]
EDGE_TARGETS = [target for _, target in EDGES]
LAYER_COUNT = 1

INITIAL_GAMMA = 0.01
INITIAL_BETA = 0.0
INITIAL_PARAMETERS = (
    [INITIAL_GAMMA] * LAYER_COUNT + [INITIAL_BETA] * LAYER_COUNT
)
SAMPLE_SHOTS = 5000


# 2. BUILD THE QAOA QUANTUM KERNEL
@cudaq.kernel
def qaoa(
    qubit_count: int,
    layer_count: int,
    edge_sources: list[int],
    edge_targets: list[int],
    edge_weights: list[float],
    parameters: list[float],
):
    qubits = cudaq.qvector(qubit_count)
    h(qubits)  # Start in an equal superposition of every bitstring.

    for layer in range(layer_count):
        gamma = parameters[layer]
        beta = parameters[layer + layer_count]

        # Cost step: encode every graph edge.
        for edge in range(len(edge_sources)):
            source = edge_sources[edge]
            target = edge_targets[edge]
            x.ctrl(qubits[source], qubits[target])
            rz(2.0 * gamma * edge_weights[edge], qubits[target])
            x.ctrl(qubits[source], qubits[target])

        # Mixer step: allow the state to explore other cuts.
        for qubit in range(qubit_count):
            rx(2.0 * beta, qubits[qubit])


# 3. TURN THE GRAPH INTO A MAX-CUT HAMILTONIAN
def maxcut_hamiltonian(edges, edge_weights):
    hamiltonian = 0
    for (source, target), weight in zip(edges, edge_weights):
        hamiltonian += 0.5 * weight * (
            spin.z(source) * spin.z(target)
            - spin.i(source) * spin.i(target)
        )
    return hamiltonian


# 4. OPTIMIZE THE QAOA PARAMETERS
def solve_qaoa():
    hamiltonian = maxcut_hamiltonian(EDGES, EDGE_WEIGHTS)

    def objective(parameters):
        return cudaq.observe(
            qaoa,
            hamiltonian,
            NUM_QUBITS,
            LAYER_COUNT,
            EDGE_SOURCES,
            EDGE_TARGETS,
            EDGE_WEIGHTS,
            parameters,
        ).expectation()

    result = minimize(
        objective,
        INITIAL_PARAMETERS.copy(),
        method="BFGS",
        jac="2-point",
        tol=1e-5,
    )
    return result.fun, result.x.tolist()


def set_simulator_target():
    """Use the ADAPT-QAOA tutorial's double-precision simulator setup."""
    if cudaq.num_available_gpus() > 0 and cudaq.has_target("nvidia"):
        cudaq.set_target("nvidia", option="fp64")
    else:
        print("NVIDIA GPU unavailable; using qpp-cpu instead.")
        cudaq.set_target("qpp-cpu")


# 5. SAMPLE THE BEST CIRCUIT
def main():
    set_simulator_target()
    best_energy, best_parameters = solve_qaoa()

    counts = cudaq.sample(
        qaoa,
        NUM_QUBITS,
        LAYER_COUNT,
        EDGE_SOURCES,
        EDGE_TARGETS,
        EDGE_WEIGHTS,
        best_parameters,
        shots_count=SAMPLE_SHOTS,
    )
    best_bitstring = max(counts.items(), key=lambda item: item[1])[0]

    print("Best parameters:", best_parameters)
    print("Estimated maximum cut:", -best_energy)
    print("Most frequent bitstring:", best_bitstring)
    print("Sample counts:", counts)


if __name__ == "__main__":
    main()

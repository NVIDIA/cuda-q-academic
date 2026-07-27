import cudaq_solvers
import networkx as nx

from qaoa_maxcut import (
    INITIAL_BETA,
    INITIAL_GAMMA,
    LAYER_COUNT,
    set_simulator_target,
)
from workshop_graphs import NUM_QUBITS, WEIGHTED_EDGES


def build_graph():
    graph = nx.Graph()
    graph.add_nodes_from(range(NUM_QUBITS))
    graph.add_weighted_edges_from(WEIGHTED_EDGES)
    return graph


def solve_qaoa():
    """Solve the same graph with the high-level CUDA-Q Solvers QAOA."""
    hamiltonian = cudaq_solvers.get_maxcut_hamiltonian(build_graph())
    parameter_count = cudaq_solvers.get_num_qaoa_parameters(
        hamiltonian, LAYER_COUNT
    )
    initial_parameters = [INITIAL_GAMMA, INITIAL_BETA] * LAYER_COUNT
    assert len(initial_parameters) == parameter_count

    # With no shots argument, optimization uses exact expectation values.
    return cudaq_solvers.qaoa(
        hamiltonian,
        LAYER_COUNT,
        initial_parameters,
        # The high-level API cannot accept SciPy BFGS, and its
        # L-BFGS path cannot receive the required gradient here.
        optimizer="cobyla",
    )


def main():
    set_simulator_target()
    result = solve_qaoa()
    best_bitstring = max(
        result.optimal_config.items(), key=lambda item: item[1]
    )[0]

    print("Best parameters:", result.optimal_parameters)
    print("Estimated maximum cut:", -result.optimal_value)
    print("Most frequent bitstring:", best_bitstring)
    print("Sample counts:", result.optimal_config)


if __name__ == "__main__":
    main()

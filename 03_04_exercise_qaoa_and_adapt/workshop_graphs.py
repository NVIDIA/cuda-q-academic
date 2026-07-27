"""Graph inputs shared by the workshop QAOA examples."""


GRAPHS = {
    "small": (
        6,
        [
            (0, 1, 0.288),
            (0, 2, 0.630),
            (0, 3, 0.639),
            (0, 4, 0.449),
            (0, 5, 0.347),
            (1, 2, 0.266),
            (1, 3, 0.545),
            (1, 4, 0.535),
            (1, 5, 0.268),
            (2, 3, 0.429),
            (2, 4, 0.841),
            (2, 5, 0.713),
            (3, 4, 0.987),
            (3, 5, 0.896),
            (4, 5, 0.724),
        ],
    ),
    "large": (
        16,
        [
            (4, 9, 1.0),
            (4, 0, 1.0),
            (4, 7, 1.0),
            (9, 3, 1.0),
            (9, 2, 1.0),
            (5, 13, 1.0),
            (5, 11, 1.0),
            (5, 14, 1.0),
            (13, 3, 1.0),
            (13, 7, 1.0),
            (3, 1, 1.0),
            (0, 2, 1.0),
            (0, 15, 1.0),
            (2, 1, 1.0),
            (1, 6, 1.0),
            (6, 8, 1.0),
            (6, 14, 1.0),
            (10, 15, 1.0),
            (10, 11, 1.0),
            (10, 8, 1.0),
            (15, 12, 1.0),
            (8, 11, 1.0),
            (14, 12, 1.0),
            (7, 12, 1.0),
        ],
    ),
}


# Change this to "large" to run the 16-qubit graph.
SELECTED_GRAPH = "small"

NUM_QUBITS, WEIGHTED_EDGES = GRAPHS[SELECTED_GRAPH]
EDGES = [(source, target) for source, target, _ in WEIGHTED_EDGES]
EDGE_WEIGHTS = [weight for _, _, weight in WEIGHTED_EDGES]

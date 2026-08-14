"""Fixed round-one COBYLA baseline for the depth-fifteen call-budget study."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "COBYLA rhobeg=1.0 baseline"

RATIONALE = (
    "Preserve the prior study's first-round optimizer settings exactly: "
    "COBYLA with rhobeg 1.0, tolerance 1e-7, and zero constraint tolerance. "
    "This supplies a stable depth-fifteen, 300-observe baseline before "
    "adaptive optimizer research begins."
)

HYPOTHESIS = (
    "The unchanged broad-trust-region COBYLA configuration will either "
    "converge or consume the 300-observe budget and establish an energy that "
    "later optimizer families can improve."
)


def optimize(
    objective,
    initial_parameters,
    initial_energy,
    max_calls,
    seed,
    accepted,
):
    del initial_energy, seed
    result = minimize(
        objective,
        np.asarray(initial_parameters, dtype=float).copy(),
        method="COBYLA",
        options={
            "maxiter": max(1, int(max_calls) - 1),
            "rhobeg": 1.0,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

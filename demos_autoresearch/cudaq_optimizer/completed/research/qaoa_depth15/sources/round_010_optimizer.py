"""Continuous Powell search in a layer-mode subspace, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D mode Powell 120 calls + COBYLA rhobeg=0.20"

RATIONALE = (
    "Round 9's restored 120-call five-mode search followed by COBYLA with "
    "rhobeg 0.20 produced the current best energy of -5.6445201952248611 and "
    "converged at call 170. Round 7 showed that simply appending finer "
    "fixed-radius sweeps was counterproductive, while Round 8 showed that "
    "abandoning the smooth global geometry for local layer-pair models was "
    "substantially worse. Preserve the successful five-mode subspace but "
    "optimize its ten gamma/beta coefficients jointly and continuously with a "
    "120-call Powell phase, then retain Round 9's full-space COBYLA polish."
)

HYPOTHESIS = (
    "Continuous Powell line minimization and direction replacement in the "
    "ten-dimensional mode space will observe an energy below Round 9's "
    "-5.6445201952248611. The subsequent COBYLA phase will reach "
    "accepted-iterate convergence before call 240 and before the 300-call cap."
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
    initial = np.asarray(initial_parameters, dtype=float).copy()
    optimizer_calls = 0
    optimizer_limit = max(0, int(max_calls) - 1)
    layers = np.arange(15, dtype=float)
    basis = np.zeros((initial.size, 10), dtype=float)
    for mode_index in range(5):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        mode /= np.linalg.norm(mode)
        basis[:15, mode_index] = mode
        basis[15:, mode_index + 5] = mode

    evaluated = set()
    last_reported = None
    last_report_calls = 0

    def mapped_parameters(coefficients):
        return initial + basis @ np.asarray(coefficients, dtype=float)

    def reduced_objective(coefficients):
        nonlocal optimizer_calls
        parameters = mapped_parameters(coefficients)
        energy = float(objective(parameters))
        optimizer_calls += 1
        evaluated.add(np.asarray(parameters, dtype=float).tobytes())
        return energy

    def powell_accepted(coefficients):
        nonlocal last_reported, last_report_calls
        parameters = mapped_parameters(coefficients)
        accepted(parameters)
        last_reported = np.asarray(coefficients, dtype=float).copy()
        last_report_calls = optimizer_calls

    phase_limit = min(120, optimizer_limit)
    if phase_limit > 0:
        directions = np.diag(np.asarray([1.0] * 5 + [0.5] * 5))
        result = minimize(
            reduced_objective,
            np.zeros(10, dtype=float),
            method="Powell",
            callback=powell_accepted,
            options={
                "maxfev": phase_limit,
                "maxiter": 1000,
                "xtol": 1e-4,
                "ftol": 1e-7,
                "direc": directions,
            },
        )
        coefficients = np.asarray(result.x, dtype=float)
        parameters = mapped_parameters(coefficients)
        distinct = (
            last_reported is None
            or not np.array_equal(coefficients, last_reported)
        )
        if (
            distinct
            and optimizer_calls > last_report_calls
            and parameters.tobytes() in evaluated
        ):
            accepted(parameters)
    else:
        parameters = initial

    remaining_calls = max(0, optimizer_limit - optimizer_calls)
    if remaining_calls == 0:
        return parameters

    result = minimize(
        objective,
        parameters,
        method="COBYLA",
        options={
            "maxiter": remaining_calls,
            "rhobeg": 0.20,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

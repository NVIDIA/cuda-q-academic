"""Continuous Powell search in a layer-mode subspace, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D mode Powell 160 calls + COBYLA rhobeg=0.20"

RATIONALE = (
    "Round 10's 120-call continuous Powell search in the ten-dimensional "
    "layer-mode space followed by COBYLA with rhobeg 0.20 is the current "
    "winner: it converged without a time cap at call 165 and observed "
    "-5.6781517593401682, improving Round 9 by 0.0336315641153071 while using "
    "five fewer calls. Preserve its basis, directions, tolerances, reporting, "
    "and full-space polish, but extend only the Powell allowance from 120 to "
    "160 calls. This uses 40 of the 135 calls Round 10 left unused while still "
    "reserving up to 139 calls for COBYLA, about 95 more than Round 10 used "
    "after its reduced-space phase."
)

HYPOTHESIS = (
    "The additional 40 continuous 10D Powell evaluations will observe an "
    "energy below Round 10's -5.6781517593401682, and the unchanged full-space "
    "COBYLA polish will reach accepted-iterate convergence before the "
    "300-call cap. Unless Powell terminates before its enlarged allowance or "
    "convergence fires during the extended reduced-space phase, Round 11 will "
    "use more than Round 10's 165 counted calls and fewer than 260 calls."
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

    phase_limit = min(160, optimizer_limit)
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

"""Continuous Powell search in a layer-mode subspace, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D Powell 180 + modes 5-6 residual 48 + COBYLA 0.20"

RATIONALE = (
    "Round 14's 180-call 10D Powell phase, 40-call modes-5-and-6 residual "
    "search, and COBYLA polish is the current winner: it converged without a "
    "time cap at call 259 and observed -5.6877750169297148, improving Round 13 "
    "by 0.0034246249782992 while leaving 41 calls unused. Preserve that "
    "complete winning trajectory and add one finer residual sweep at gamma "
    "radius 0.07 and beta radius 0.035. This controlled eight-call extension "
    "continues the established geometric radius schedule and still leaves up "
    "to 71 calls for COBYLA, about 33 more than Round 14 used after residual "
    "search."
)

HYPOTHESIS = (
    "The additional fine modes-5-and-6 residual sweep will observe an energy "
    "below Round 14's -5.6877750169297148, and the unchanged full-space COBYLA "
    "polish will reach accepted-iterate convergence before the 300-call cap. "
    "Unless convergence fires during the added residual sweep, Round 15 will "
    "use more than Round 14's 259 counted calls and fewer than 290 calls."
)


def optimize(
    objective,
    initial_parameters,
    initial_energy,
    max_calls,
    seed,
    accepted,
):
    del seed
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

    evaluated = {}
    last_reported = None
    last_report_calls = 0

    def mapped_parameters(coefficients):
        return initial + basis @ np.asarray(coefficients, dtype=float)

    def reduced_objective(coefficients):
        nonlocal optimizer_calls
        parameters = mapped_parameters(coefficients)
        energy = float(objective(parameters))
        optimizer_calls += 1
        evaluated[np.asarray(parameters, dtype=float).tobytes()] = energy
        return energy

    def powell_accepted(coefficients):
        nonlocal last_reported, last_report_calls
        parameters = mapped_parameters(coefficients)
        accepted(parameters)
        last_reported = np.asarray(coefficients, dtype=float).copy()
        last_report_calls = optimizer_calls

    phase_limit = min(180, optimizer_limit)
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

    incumbent_energy = evaluated.get(
        parameters.tobytes(),
        float(initial_energy),
    )
    residual_modes = {}
    for mode_index in (5, 6):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        residual_modes[mode_index] = mode / np.linalg.norm(mode)
    gamma_radii = (0.40, 0.28, 0.20, 0.14, 0.10, 0.07)
    beta_radii = (0.20, 0.14, 0.10, 0.07, 0.05, 0.035)
    residual_limit = min(optimizer_calls + 48, optimizer_limit)

    for sweep in range(6):
        mode_indices = (5, 6) if sweep % 2 == 0 else (6, 5)
        spaces = ("gamma", "beta") if sweep % 2 == 0 else ("beta", "gamma")
        for mode_index in mode_indices:
            for space in spaces:
                if optimizer_calls + 2 > residual_limit:
                    break
                direction = np.zeros_like(parameters)
                if space == "gamma":
                    direction[:15] = residual_modes[mode_index]
                    radius = gamma_radii[sweep]
                else:
                    direction[15:] = residual_modes[mode_index]
                    radius = beta_radii[sweep]
                plus = parameters + radius * direction
                minus = parameters - radius * direction
                plus_energy = float(objective(plus))
                minus_energy = float(objective(minus))
                optimizer_calls += 2
                if min(plus_energy, minus_energy) < incumbent_energy:
                    if plus_energy < minus_energy:
                        parameters = plus
                        incumbent_energy = plus_energy
                    else:
                        parameters = minus
                        incumbent_energy = minus_energy
                    accepted(parameters)

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

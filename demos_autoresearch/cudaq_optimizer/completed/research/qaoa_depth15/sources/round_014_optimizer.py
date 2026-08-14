"""Continuous Powell search in a layer-mode subspace, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D Powell 180 + modes 5-6 residual 40 + COBYLA 0.20"

RATIONALE = (
    "Increasing 10D Powell from 120 to 160 calls improved the best energy by "
    "0.0051485854989544, while increasing it from 160 to 180 calls gained only "
    "0.0010500471122930, indicating diminishing returns inside modes 0-4. "
    "Round 12 showed that replacing Powell with population search was "
    "ineffective, and Round 8 showed that unrestricted layer-local models were "
    "too disruptive. Preserve Round 13's winning 180-call Powell trajectory, "
    "then spend 40 calls selectively releasing the adjacent cosine modes 5 "
    "and 6 before retaining the successful COBYLA polish."
)

HYPOTHESIS = (
    "The modes-5-and-6 residual phase will expose a medium-frequency "
    "correction unavailable to Round 13 and produce a lowest energy below "
    "-5.6843503919514156 after full-space polishing. If Powell consumes its "
    "full allowance and accepted-iterate convergence does not fire during "
    "residual search, COBYLA will begin at call 221 and the round will "
    "converge before call 280 without reaching the observe cap."
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
    gamma_radii = (0.40, 0.28, 0.20, 0.14, 0.10)
    beta_radii = (0.20, 0.14, 0.10, 0.07, 0.05)
    residual_limit = min(optimizer_calls + 40, optimizer_limit)

    for sweep in range(5):
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

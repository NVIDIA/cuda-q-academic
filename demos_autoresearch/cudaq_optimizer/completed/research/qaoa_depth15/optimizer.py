"""Powell and medium-frequency residual search followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D Powell 180 + modes 5-6 residual 48 + COBYLA 0.25"

RATIONALE = (
    "Round 15 remains the study winner at -5.7121058506678075. It was valid "
    "and not time-capped, but did not converge before exhausting all 300 "
    "observations. Rounds 16 and 18 changed the finishing or basin-search "
    "family and regressed by 0.0114433063999835 and 0.0291214455224597, while "
    "Round 17's smaller COBYLA radius of 0.12 converged early at call 268 and "
    "regressed by 0.0190777382643503. Restore Round 15's exact 180-call Powell "
    "and 48-call residual basin-selection trajectory, then tune only COBYLA's "
    "initial radius upward from 0.20 to 0.25 so its fixed 71-call allowance "
    "can take modestly broader full-space steps before local contraction."
)

HYPOTHESIS = (
    "The exact Round 15 basin-selection trajectory followed by COBYLA with "
    "rhobeg 0.25 will observe an energy below -5.7121058506678075 within the "
    "300-call budget. Unless the accepted-iterate diagnostic fires during "
    "polishing, Round 19 will again use and score all 300 observations as a "
    "valid call-cap result without reaching the time cap."
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
            "rhobeg": 0.25,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

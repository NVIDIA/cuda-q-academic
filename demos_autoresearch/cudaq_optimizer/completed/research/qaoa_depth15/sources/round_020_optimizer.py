"""Powell and medium-frequency residual search followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Powell180 + residual48 + bounded 14D L-BFGS-B"

RATIONALE = (
    "Round 19's larger-radius COBYLA improved the call-capped Round 15 result "
    "by 0.0020851841956908, confirming that the preserved Powell-plus-residual "
    "basin still contains useful descent directions. Round 16 showed that "
    "spending 60 calls on one full-space diagonal-curvature estimate was too "
    "inflexible, while Round 18 showed that replacing the successful "
    "basin-selection path was harmful. Preserve Round 19's exact 228-call "
    "basin trajectory, then use the final 71 calls for several bounded "
    "quasi-Newton updates over modes 0-6, allowing learned cross-mode curvature "
    "without reopening all 30 coordinates."
)

HYPOTHESIS = (
    "The bounded 14D L-BFGS-B correction will observe an energy below Round "
    "19's -5.7141910348634983. Unless accepted-iterate convergence fires "
    "first, numerical-gradient evaluation and line search will use and score "
    "call 300, producing a valid call_cap result without reaching the time cap."
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

    correction_basis = np.zeros((initial.size, 14), dtype=float)
    for mode_index in range(7):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        mode /= np.linalg.norm(mode)
        correction_basis[:15, mode_index] = mode
        correction_basis[15:, mode_index + 7] = mode
    basin_parameters = parameters.copy()
    correction_evaluated = {}
    correction_best_energy = incumbent_energy
    correction_best_parameters = basin_parameters.copy()
    correction_last_reported = None
    correction_last_report_calls = optimizer_calls

    def correction_parameters(coefficients):
        return (
            basin_parameters
            + correction_basis @ np.asarray(coefficients, dtype=float)
        )

    def correction_objective(coefficients):
        nonlocal optimizer_calls
        nonlocal correction_best_energy, correction_best_parameters
        full_parameters = correction_parameters(coefficients)
        energy = float(objective(full_parameters))
        optimizer_calls += 1
        correction_evaluated[full_parameters.tobytes()] = energy
        if energy < correction_best_energy:
            correction_best_energy = energy
            correction_best_parameters = full_parameters.copy()
        return energy

    def correction_accepted(coefficients):
        nonlocal correction_last_reported, correction_last_report_calls
        full_parameters = correction_parameters(coefficients)
        accepted(full_parameters)
        correction_last_reported = np.asarray(coefficients, dtype=float).copy()
        correction_last_report_calls = optimizer_calls

    bounds = [(-0.30, 0.30)] * 7 + [(-0.15, 0.15)] * 7
    result = minimize(
        correction_objective,
        np.zeros(14, dtype=float),
        method="L-BFGS-B",
        jac=None,
        bounds=bounds,
        callback=correction_accepted,
        options={
            "maxfun": remaining_calls,
            "maxiter": 20,
            "maxcor": 7,
            "maxls": 4,
            "ftol": 1e-12,
            "gtol": 1e-6,
            "eps": 1e-4,
        },
    )
    result_coefficients = np.asarray(result.x, dtype=float)
    result_parameters = correction_parameters(result_coefficients)
    distinct = (
        correction_last_reported is None
        or not np.array_equal(result_coefficients, correction_last_reported)
    )
    result_energy = correction_evaluated.get(result_parameters.tobytes())
    if (
        distinct
        and result_energy is not None
        and result_energy < incumbent_energy
        and optimizer_calls > correction_last_report_calls
    ):
        accepted(result_parameters)
    if correction_best_energy < incumbent_energy:
        return correction_best_parameters
    return result_parameters

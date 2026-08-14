"""Continuous Powell search in a layer-mode subspace, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Powell180 + residual48 + full diagonal-Newton line search"

RATIONALE = (
    "Round 15's 180-call Powell phase and 48-call modes-5-and-6 residual "
    "search produced the current winner, improving Round 14 by "
    "0.0243308337380927, but its COBYLA polish remained active until the exact "
    "300-call cap and did not converge. Preserve the successful basin-selection "
    "trajectory and use the final 71 calls to measure every full-space "
    "coordinate symmetrically, construct a curvature-scaled descent direction, "
    "and test that direction at multiple lengths. This concentrates the "
    "remaining budget into one information-rich full-gradient correction "
    "rather than another call-capped COBYLA trajectory."
)

HYPOTHESIS = (
    "The central-difference diagonal-Newton line search will observe an energy "
    "below Round 15's -5.7121058506678075. Unless an earlier accepted report "
    "triggers convergence, the optimizer will intentionally use and score call "
    "300, producing another valid call_cap result without reaching the time cap."
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
    if remaining_calls < 2:
        return parameters

    base_parameters = parameters.copy()
    radii = np.asarray([0.02] * 15 + [0.01] * 15)
    plus_energies = []
    minus_energies = []
    coordinate_results = []
    for coordinate, radius in enumerate(radii):
        if optimizer_calls + 2 > optimizer_limit:
            break
        plus = base_parameters.copy()
        minus = base_parameters.copy()
        plus[coordinate] += radius
        minus[coordinate] -= radius
        plus_energy = float(objective(plus))
        minus_energy = float(objective(minus))
        optimizer_calls += 2
        plus_energies.append(plus_energy)
        minus_energies.append(minus_energy)
        coordinate_results.extend(
            ((plus_energy, plus), (minus_energy, minus))
        )

    if len(plus_energies) != base_parameters.size:
        if coordinate_results:
            best_energy, best_parameters = min(
                coordinate_results,
                key=lambda item: item[0],
            )
            if best_energy < incumbent_energy:
                accepted(best_parameters)
                return np.asarray(best_parameters, dtype=float)
        return parameters

    plus_energies = np.asarray(plus_energies)
    minus_energies = np.asarray(minus_energies)
    gradient = (plus_energies - minus_energies) / (2.0 * radii)
    curvature = (
        plus_energies + minus_energies - 2.0 * incumbent_energy
    ) / (radii * radii)
    step = -gradient / np.maximum(np.abs(curvature), 0.05)
    multipliers = (0.0625, 0.125, 0.25, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0)
    line_results = []
    for multiplier in multipliers:
        if optimizer_calls >= optimizer_limit:
            break
        displacement = multiplier * step
        displacement[:15] = np.clip(displacement[:15], -0.30, 0.30)
        displacement[15:] = np.clip(displacement[15:], -0.15, 0.15)
        candidate = base_parameters + displacement
        candidate_energy = float(objective(candidate))
        optimizer_calls += 1
        line_results.append((candidate_energy, candidate, multiplier))

    all_results = coordinate_results + [
        (energy, candidate) for energy, candidate, _ in line_results
    ]
    if all_results:
        best_energy, best_parameters = min(
            all_results,
            key=lambda item: item[0],
        )
        if best_energy < incumbent_energy:
            parameters = np.asarray(best_parameters, dtype=float).copy()
            incumbent_energy = float(best_energy)
            accepted(parameters)

    if optimizer_calls < optimizer_limit and len(line_results) >= 2:
        best_line_index = min(
            range(len(line_results)),
            key=lambda index: line_results[index][0],
        )
        if best_line_index == 0:
            neighbor_index = 1
        elif best_line_index == len(line_results) - 1:
            neighbor_index = best_line_index - 1
        else:
            left = line_results[best_line_index - 1]
            right = line_results[best_line_index + 1]
            neighbor_index = (
                best_line_index - 1 if left[0] < right[0] else best_line_index + 1
            )
        refined_multiplier = 0.5 * (
            line_results[best_line_index][2]
            + line_results[neighbor_index][2]
        )
        displacement = refined_multiplier * step
        displacement[:15] = np.clip(displacement[:15], -0.30, 0.30)
        displacement[15:] = np.clip(displacement[15:], -0.15, 0.15)
        refined = base_parameters + displacement
        refined_energy = float(objective(refined))
        if refined_energy < incumbent_energy:
            accepted(refined)
            return np.asarray(refined, dtype=float)

    return parameters

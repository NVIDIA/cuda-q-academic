"""Joint adaptive simplex search in 14 layer modes, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Joint 14D adaptive Nelder-Mead 228 + COBYLA 0.20"

RATIONALE = (
    "Round 15's inclusion of a finer modes-5-and-6 sweep produced a large "
    "0.0243308337380927 improvement, suggesting that medium-frequency degrees "
    "of freedom materially affect the winning basin. Round 16 showed that a "
    "diagonal full-space curvature model was insufficient, while Round 17 "
    "showed that reducing COBYLA's radius to 0.12 prematurely converged in a "
    "worse basin. Jointly optimize modes 0-6 with an adaptive 14D Nelder-Mead "
    "simplex for the same 228-call basin-selection budget, then retain Round "
    "15's productive full-space COBYLA radius of 0.20."
)

HYPOTHESIS = (
    "Joint simplex moves coupling low and medium layer modes will observe a "
    "basin that, after COBYLA polishing, yields an energy below Round 15's "
    "-5.7121058506678075. Unless accepted-iterate convergence fires earlier, "
    "the productive 0.20-radius polish will again use and score call 300, "
    "producing a valid call_cap result without reaching the time cap."
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
    basis = np.zeros((initial.size, 14), dtype=float)
    for mode_index in range(7):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        mode /= np.linalg.norm(mode)
        basis[:15, mode_index] = mode
        basis[15:, mode_index + 7] = mode

    phase_best_energy = float(initial_energy)
    phase_best_parameters = initial.copy()
    reported_best_energy = float(initial_energy)
    last_report_calls = 0

    def mapped_parameters(coefficients):
        return initial + basis @ np.asarray(coefficients, dtype=float)

    def reduced_objective(coefficients):
        nonlocal optimizer_calls, phase_best_energy, phase_best_parameters
        parameters = mapped_parameters(coefficients)
        energy = float(objective(parameters))
        optimizer_calls += 1
        if energy < phase_best_energy:
            phase_best_energy = energy
            phase_best_parameters = parameters.copy()
        return energy

    def simplex_accepted(coefficients):
        del coefficients
        nonlocal reported_best_energy, last_report_calls
        if (
            phase_best_energy < reported_best_energy
            and optimizer_calls > last_report_calls
        ):
            accepted(phase_best_parameters)
            reported_best_energy = phase_best_energy
            last_report_calls = optimizer_calls

    phase_limit = min(228, optimizer_limit)
    if phase_limit > 0:
        coefficient_scales = np.asarray(
            [1.0, 1.0, 1.0, 1.0, 1.0, 0.40, 0.28]
            + [0.50, 0.50, 0.50, 0.50, 0.50, 0.20, 0.14]
        )
        initial_simplex = np.zeros((15, 14), dtype=float)
        for coordinate, scale in enumerate(coefficient_scales):
            initial_simplex[coordinate + 1, coordinate] = scale
        minimize(
            reduced_objective,
            np.zeros(14, dtype=float),
            method="Nelder-Mead",
            callback=simplex_accepted,
            options={
                "adaptive": True,
                "maxfev": phase_limit,
                "maxiter": 10000,
                "xatol": 1e-5,
                "fatol": 1e-8,
                "initial_simplex": initial_simplex,
            },
        )
        if (
            phase_best_energy < reported_best_energy
            and optimizer_calls > last_report_calls
        ):
            accepted(phase_best_parameters)

    remaining_calls = max(0, optimizer_limit - optimizer_calls)
    if remaining_calls == 0:
        return phase_best_parameters

    result = minimize(
        objective,
        phase_best_parameters,
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

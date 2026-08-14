"""Seeded SPSA-Adam basin search followed by a local COBYLA polish."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "SPSA-Adam 120-call search + COBYLA rhobeg=0.35"

RATIONALE = (
    "Round 1's broad COBYLA baseline converged after only 74 counted calls at "
    "a lowest energy of -5.4467026331080071, leaving most of the 300-call "
    "scientific budget unused. Use 120 calls of seeded SPSA-Adam exploration "
    "to cross-coordinate directions and seek a different basin, retaining "
    "any improving perturbation or update probe, then spend the remaining "
    "allowance on a smaller-radius COBYLA polish from the best explored point."
)

HYPOTHESIS = (
    "The SPSA-Adam exploration followed by COBYLA polishing will observe an "
    "energy below -5.4467026331080071. Unless the fixed convergence "
    "diagnostic fires first, it will use more than Round 1's 74 counted calls "
    "because the exploration phase alone is budgeted for up to 120 optimizer "
    "calls."
)


def optimize(
    objective,
    initial_parameters,
    initial_energy,
    max_calls,
    seed,
    accepted,
):
    x = np.asarray(initial_parameters, dtype=float).copy()
    incumbent_energy = float(initial_energy)
    rng = np.random.default_rng(seed)
    first_moment = np.zeros_like(x)
    second_moment = np.zeros_like(x)
    optimizer_calls = 0
    exploration_limit = min(120, max(0, int(max_calls) - 1))

    for iteration in range(40):
        if optimizer_calls + 3 > exploration_limit:
            break

        delta = rng.choice(np.array([-1.0, 1.0]), size=x.size)
        c_k = 0.15 / (iteration + 1) ** 0.101
        x_plus = x + c_k * delta
        x_minus = x - c_k * delta
        energy_plus = float(objective(x_plus))
        energy_minus = float(objective(x_minus))
        optimizer_calls += 2

        gradient = (energy_plus - energy_minus) * delta / (2.0 * c_k)
        first_moment = 0.9 * first_moment + 0.1 * gradient
        second_moment = 0.999 * second_moment + 0.001 * gradient * gradient
        step_number = iteration + 1
        corrected_first = first_moment / (1.0 - 0.9**step_number)
        corrected_second = second_moment / (1.0 - 0.999**step_number)
        a_k = 0.08 / step_number**0.602
        x_candidate = x - (
            a_k * corrected_first / (np.sqrt(corrected_second) + 1e-8)
        )
        energy_candidate = float(objective(x_candidate))
        optimizer_calls += 1

        candidates = (
            (energy_plus, x_plus),
            (energy_minus, x_minus),
            (energy_candidate, x_candidate),
        )
        best_energy, best_parameters = min(candidates, key=lambda item: item[0])
        if best_energy < incumbent_energy:
            x = np.asarray(best_parameters, dtype=float).copy()
            incumbent_energy = float(best_energy)
            accepted(x)

    remaining_calls = max(0, int(max_calls) - 1 - optimizer_calls)
    if remaining_calls == 0:
        return x

    result = minimize(
        objective,
        x,
        method="COBYLA",
        options={
            "maxiter": remaining_calls,
            "rhobeg": 0.35,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

"""Seeded SPSA-Adam basin search followed by a local COBYLA polish."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "SPSA-Adam 195-call search + COBYLA rhobeg=0.35"

RATIONALE = (
    "Round 3's seeded 180-call SPSA-Adam search followed by COBYLA is the "
    "current winner: it converged without a time cap at call 259 and observed "
    "-5.6173665910969879, improving Round 2 by 0.1191271078358529. Round 4's "
    "materially different orthogonal search converged earlier at call 216 but "
    "was worse by 0.0311184792037338, so return to the winning SPSA-Adam "
    "mechanism. Extend only its exploration allocation from 60 to 65 "
    "iterations (180 to 195 calls). This uses 15 of Round 3's 41 unused "
    "counted calls while retaining up to 104 calls for the unchanged COBYLA "
    "polish, about 26 more than Round 3 needed after its exploration phase."
)

HYPOTHESIS = (
    "Five additional seeded SPSA-Adam iterations will observe an energy below "
    "Round 3's -5.6173665910969879, and the unchanged COBYLA polish will still "
    "reach accepted-iterate convergence before the 300-call cap. Unless "
    "convergence fires during those additional SPSA iterations, Round 5 will "
    "use more than Round 3's 259 counted calls."
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
    exploration_limit = min(195, max(0, int(max_calls) - 1))

    for iteration in range(65):
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

"""Low-frequency layer-mode pattern search followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Five-mode layer search 160 calls + COBYLA rhobeg=0.35"

RATIONALE = (
    "Round 6's five-mode layer search followed by COBYLA is the current "
    "winner: it converged without a time cap at call 165 and observed "
    "-5.6295843246899535, improving Round 5 by 0.0058145512670089 while using "
    "131 fewer calls. Preserve its successful layer-correlated search geometry "
    "and local polish, but add two finer complete mode sweeps, extending gamma "
    "radii with 0.13 and 0.09 and beta radii with 0.055 and 0.04. This "
    "controlled change raises structured-search use from 120 to 160 calls "
    "while still reserving up to 139 calls for COBYLA, about 95 more than "
    "Round 6 used after its mode phase."
)

HYPOTHESIS = (
    "The two finer layer-mode sweeps will observe an energy below Round 6's "
    "-5.6295843246899535, and the unchanged COBYLA polish will still reach "
    "accepted-iterate convergence before the 300-call cap. Unless convergence "
    "fires during the added fine sweeps, Round 7 will use more than Round 6's "
    "165 counted calls."
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
    x = np.asarray(initial_parameters, dtype=float).copy()
    incumbent_energy = float(initial_energy)
    optimizer_calls = 0
    optimizer_limit = max(0, int(max_calls) - 1)
    layers = np.arange(15, dtype=float)
    modes = []
    for mode_index in range(5):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        modes.append(mode / np.linalg.norm(mode))

    gamma_radii = (1.00, 0.70, 0.50, 0.35, 0.25, 0.18, 0.13, 0.09)
    beta_radii = (0.50, 0.35, 0.25, 0.18, 0.12, 0.08, 0.055, 0.04)

    for sweep in range(8):
        mode_indices = range(5) if sweep % 2 == 0 else range(4, -1, -1)
        spaces = ("gamma", "beta") if sweep % 2 == 0 else ("beta", "gamma")
        for mode_index in mode_indices:
            for space in spaces:
                if optimizer_calls + 2 > min(160, optimizer_limit):
                    break
                direction = np.zeros_like(x)
                if space == "gamma":
                    direction[:15] = modes[mode_index]
                    radius = gamma_radii[sweep]
                else:
                    direction[15:] = modes[mode_index]
                    radius = beta_radii[sweep]

                plus = x + radius * direction
                minus = x - radius * direction
                plus_energy = float(objective(plus))
                minus_energy = float(objective(minus))
                optimizer_calls += 2
                if min(plus_energy, minus_energy) < incumbent_energy:
                    if plus_energy < minus_energy:
                        x = plus
                        incumbent_energy = plus_energy
                    else:
                        x = minus
                        incumbent_energy = minus_energy
                    accepted(x)

    remaining_calls = max(0, optimizer_limit - optimizer_calls)
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

"""Low-frequency layer-mode pattern search followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Five-mode layer search 120 calls + COBYLA rhobeg=0.20"

RATIONALE = (
    "Round 6 remains the study winner: its 120-call five-mode layer search "
    "followed by COBYLA with rhobeg 0.35 converged without a time cap at call "
    "165 and observed -5.6295843246899535. Round 7's extra fine mode sweeps "
    "regressed by 0.0012813244035854, and Round 8's layer-pair quadratic "
    "family regressed by 0.1011471157183266, so restore the exact Round 6 "
    "structured search. Tune only COBYLA's initial radius from 0.35 to 0.20, "
    "close to the final 0.18 gamma-mode radius, to polish the selected basin "
    "more locally while retaining up to 179 post-search calls."
)

HYPOTHESIS = (
    "The restored Round 6 mode search followed by the more local COBYLA "
    "radius of 0.20 will observe an energy below -5.6295843246899535, reach "
    "accepted-iterate convergence before the 300-call cap, and use fewer than "
    "Round 7's 211 counted calls."
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

    gamma_radii = (1.00, 0.70, 0.50, 0.35, 0.25, 0.18)
    beta_radii = (0.50, 0.35, 0.25, 0.18, 0.12, 0.08)

    for sweep in range(6):
        mode_indices = range(5) if sweep % 2 == 0 else range(4, -1, -1)
        spaces = ("gamma", "beta") if sweep % 2 == 0 else ("beta", "gamma")
        for mode_index in mode_indices:
            for space in spaces:
                if optimizer_calls + 2 > min(120, optimizer_limit):
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
            "rhobeg": 0.20,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

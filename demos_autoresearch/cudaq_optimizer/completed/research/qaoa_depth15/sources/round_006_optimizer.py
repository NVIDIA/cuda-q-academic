"""Low-frequency layer-mode pattern search followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Five-mode layer search 120 calls + COBYLA rhobeg=0.35"

RATIONALE = (
    "Round 5's extension to 195 SPSA-Adam exploration calls improved Round 3 "
    "by only 0.0064031823259567 and converged at call 296, leaving four calls "
    "of headroom. Round 4 showed that replacing SPSA with unstructured random "
    "orthogonal projections was worse, so test a materially different but "
    "problem-structured geometry: bidirectional pattern search over five "
    "low-frequency cosine modes independently embedded in the fifteen gamma "
    "and fifteen beta layers. Limit this phase to 120 calls and reserve up to "
    "179 calls for the proven COBYLA polish."
)

HYPOTHESIS = (
    "Smooth layer-correlated mode moves will place COBYLA in a basin that "
    "observes an energy below Round 5's -5.6237697734229446. Unless the "
    "accepted-iterate diagnostic fires during mode search, the round will use "
    "at least 121 counted calls, and the restored 179-call polish allowance "
    "will converge before call 296, using fewer calls than Round 5."
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
            "rhobeg": 0.35,
            "tol": 1e-7,
            "catol": 0.0,
        },
        callback=accepted,
    )
    return np.asarray(result.x, dtype=float)

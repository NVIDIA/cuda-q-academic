"""Orthogonal-subspace central differences followed by a COBYLA polish."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Orthogonal 12D search 135 calls + COBYLA rhobeg=0.35"

RATIONALE = (
    "Rounds 1-3 show that spending more calls on pre-COBYLA basin search "
    "improved the lowest energy from -5.4467026331080071 to "
    "-5.498239483261135 and then -5.6173665910969879, although Round 3 "
    "converged close to the budget at call 259. Replace SPSA's "
    "single-direction, Adam-filtered estimates with five seeded orthogonal "
    "12-direction central-difference blocks and three-scale line searches. "
    "This uses 135 exploratory calls-more than Round 2's effective basin "
    "search but less than Round 3's 180-call phase-and reserves up to 164 "
    "calls for COBYLA."
)

HYPOTHESIS = (
    "The lower-variance orthogonal-subspace estimates and explicit line-scale "
    "selection will observe an energy below Round 3's -5.6173665910969879. "
    "Unless the accepted-iterate diagnostic fires during structured search, "
    "the round will use more than 136 total counted calls, and the 164-call "
    "local-polish allowance will permit convergence before the 300-call cap."
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
    optimizer_calls = 0
    exploration_limit = min(135, max(0, int(max_calls) - 1))

    for block in range(5):
        if optimizer_calls + 27 > exploration_limit:
            break

        orthogonal, _ = np.linalg.qr(rng.standard_normal((x.size, x.size)))
        directions = orthogonal[:, :12].T
        radius = 0.30 * 0.80**block
        slopes = []
        probe_results = []

        for direction in directions:
            plus = x + radius * direction
            minus = x - radius * direction
            plus_energy = float(objective(plus))
            minus_energy = float(objective(minus))
            optimizer_calls += 2
            slopes.append((plus_energy - minus_energy) / (2.0 * radius))
            probe_results.extend(
                ((plus_energy, plus), (minus_energy, minus))
            )

        gradient = np.sum(
            np.asarray(slopes)[:, np.newaxis] * directions,
            axis=0,
        )
        gradient_norm = float(np.linalg.norm(gradient))
        if gradient_norm > 0.0:
            downhill_axis = gradient / gradient_norm
        else:
            largest = int(np.argmax(np.abs(slopes)))
            plus_result = probe_results[2 * largest]
            minus_result = probe_results[2 * largest + 1]
            downhill_axis = (
                -directions[largest]
                if plus_result[0] < minus_result[0]
                else directions[largest]
            )

        step = 0.60 * 0.70**block
        line_results = []
        for scale in (0.5, 1.0, 2.0):
            candidate = x - scale * step * downhill_axis
            candidate_energy = float(objective(candidate))
            optimizer_calls += 1
            line_results.append((candidate_energy, candidate))

        best_energy, best_parameters = min(
            probe_results + line_results,
            key=lambda item: item[0],
        )
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

"""Sequential layer-pair quadratic models followed by COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "Layer-pair quadratic models 135 calls + COBYLA rhobeg=0.35"

RATIONALE = (
    "Round 6's low-frequency layer-mode search produced the current best "
    "energy of -5.6295843246899535 and converged at call 165, but Round 7's "
    "two finer sweeps in the same smooth subspace regressed to "
    "-5.6283030002863681. Rather than further refine that basis, fit one "
    "evaluated quadratic response surface for each gamma-beta layer pair, "
    "including diagonal probes that identify within-layer coupling. Spend at "
    "most 135 calls on these block models and retain up to 164 calls for the "
    "proven COBYLA polish."
)

HYPOTHESIS = (
    "Layer-specific quadratic models will expose useful corrections outside "
    "the five-mode subspace and lead to an observed energy below Round 6's "
    "-5.6295843246899535. Unless the accepted-iterate diagnostic fires during "
    "block search, the round will use at least 121 counted calls and will "
    "converge before call 260, retaining substantially more headroom than "
    "Round 5."
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
    optimizer_calls = 0
    optimizer_limit = max(0, int(max_calls) - 1)
    rng = np.random.default_rng(seed)
    offsets = np.asarray(
        (
            (1.0, 0.0),
            (-1.0, 0.0),
            (0.0, 1.0),
            (0.0, -1.0),
            (1.0, 1.0),
            (1.0, -1.0),
            (-1.0, 1.0),
            (-1.0, -1.0),
        ),
        dtype=float,
    )
    design = np.column_stack(
        (
            offsets[:, 0],
            offsets[:, 1],
            0.5 * offsets[:, 0] ** 2,
            offsets[:, 0] * offsets[:, 1],
            0.5 * offsets[:, 1] ** 2,
        )
    )

    for layer in rng.permutation(15):
        if optimizer_calls + 8 > min(135, optimizer_limit):
            break
        block_energy = incumbent_energy
        probe_results = []
        energy_changes = []
        for gamma_offset, beta_offset in offsets:
            probe = x.copy()
            probe[layer] += 0.35 * gamma_offset
            probe[layer + 15] += 0.18 * beta_offset
            probe_energy = float(objective(probe))
            optimizer_calls += 1
            probe_results.append((probe_energy, probe))
            energy_changes.append(probe_energy - block_energy)

        coefficients = np.linalg.lstsq(
            design,
            np.asarray(energy_changes),
            rcond=None,
        )[0]
        gradient = coefficients[:2]
        hessian = np.asarray(
            (
                (coefficients[2], coefficients[3]),
                (coefficients[3], coefficients[4]),
            )
        )
        eigenvalues, eigenvectors = np.linalg.eigh(hessian)
        regularized = (
            eigenvectors
            @ np.diag(np.maximum(eigenvalues, 0.05))
            @ eigenvectors.T
        )
        model_step = -np.linalg.solve(regularized, gradient)
        model_step = np.clip(model_step, -1.5, 1.5)
        if (
            np.all(np.isfinite(model_step))
            and optimizer_calls < min(135, optimizer_limit)
        ):
            model_candidate = x.copy()
            model_candidate[layer] += 0.35 * model_step[0]
            model_candidate[layer + 15] += 0.18 * model_step[1]
            model_energy = float(objective(model_candidate))
            optimizer_calls += 1
            probe_results.append((model_energy, model_candidate))

        best_energy, best_parameters = min(
            probe_results,
            key=lambda item: item[0],
        )
        if best_energy < incumbent_energy:
            x = np.asarray(best_parameters, dtype=float).copy()
            incumbent_energy = float(best_energy)
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

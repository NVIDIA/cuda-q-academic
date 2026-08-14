"""Full-covariance evolution strategy in layer-mode space, then COBYLA."""

import numpy as np
from scipy.optimize import minimize


OPTIMIZER_LABEL = "10D full-covariance ES 156 calls + COBYLA rhobeg=0.20"

RATIONALE = (
    "Round 10's continuous mode-space Powell optimizer improved Round 9 by "
    "0.0336315641153071, while extending Powell by 40 calls in Round 11 "
    "yielded a smaller additional gain of 0.0051485854989544. This suggests "
    "diminishing returns from further deterministic line-search extension. "
    "Use the same ledger-supported ten-dimensional smooth subspace but replace "
    "Powell with a 156-call full-covariance evolution strategy that can explore "
    "correlated mode combinations and alternative basins, then retain the "
    "successful full-space COBYLA polish with rhobeg 0.20."
)

HYPOTHESIS = (
    "The covariance-adapted population search will observe a mode combination "
    "that, after COBYLA polishing, produces an energy below Round 11's "
    "-5.6833003448391226. Unless accepted-iterate convergence fires during "
    "evolutionary search, the round will use at least 157 total counted calls "
    "and will converge before call 260 without reaching the observe cap."
)


def optimize(
    objective,
    initial_parameters,
    initial_energy,
    max_calls,
    seed,
    accepted,
):
    initial = np.asarray(initial_parameters, dtype=float).copy()
    incumbent = initial.copy()
    incumbent_energy = float(initial_energy)
    optimizer_calls = 0
    optimizer_limit = max(0, int(max_calls) - 1)
    rng = np.random.default_rng(seed)
    layers = np.arange(15, dtype=float)
    basis = np.zeros((initial.size, 10), dtype=float)
    for mode_index in range(5):
        mode = np.cos(
            np.pi * (layers + 0.5) * float(mode_index) / 15.0
        )
        mode /= np.linalg.norm(mode)
        basis[:15, mode_index] = mode
        basis[15:, mode_index + 5] = mode
    scale = np.asarray([1.0] * 5 + [0.5] * 5)

    dimension = 10
    population_size = 12
    parent_count = 6
    weights = np.log(parent_count + 0.5) - np.log(
        np.arange(1, parent_count + 1)
    )
    weights /= np.sum(weights)
    mu_effective = 1.0 / np.sum(weights * weights)
    c_sigma = (mu_effective + 2.0) / (
        dimension + mu_effective + 5.0
    )
    d_sigma = (
        1.0
        + 2.0
        * max(
            0.0,
            np.sqrt((mu_effective - 1.0) / (dimension + 1.0)) - 1.0,
        )
        + c_sigma
    )
    c_c = (4.0 + mu_effective / dimension) / (
        dimension + 4.0 + 2.0 * mu_effective / dimension
    )
    c1 = 2.0 / ((dimension + 1.3) ** 2 + mu_effective)
    c_mu = min(
        1.0 - c1,
        2.0
        * (mu_effective - 2.0 + 1.0 / mu_effective)
        / ((dimension + 2.0) ** 2 + mu_effective),
    )
    chi_n = np.sqrt(dimension) * (
        1.0 - 1.0 / (4.0 * dimension) + 1.0 / (21.0 * dimension**2)
    )

    mean = np.zeros(dimension)
    covariance = np.eye(dimension)
    path_sigma = np.zeros(dimension)
    path_c = np.zeros(dimension)
    sigma = 0.60
    phase_limit = min(156, optimizer_limit)

    for generation in range(13):
        if optimizer_calls + population_size > phase_limit:
            break
        eigenvalues, eigenvectors = np.linalg.eigh(
            0.5 * (covariance + covariance.T)
        )
        eigenvalues = np.maximum(eigenvalues, 1e-10)
        square_root = (
            eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
        )
        inverse_square_root = (
            eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues))
            @ eigenvectors.T
        )
        old_mean = mean.copy()
        generation_results = []
        for _ in range(population_size):
            normalized = rng.standard_normal(dimension)
            displacement = square_root @ normalized
            coefficients = mean + sigma * displacement
            parameters = initial + basis @ (scale * coefficients)
            energy = float(objective(parameters))
            optimizer_calls += 1
            generation_results.append(
                (energy, coefficients, displacement, parameters)
            )

        generation_results.sort(key=lambda item: item[0])
        selected = generation_results[:parent_count]
        mean = np.sum(
            weights[:, np.newaxis]
            * np.asarray([item[1] for item in selected]),
            axis=0,
        )
        weighted_displacement = (mean - old_mean) / sigma
        path_sigma = (
            (1.0 - c_sigma) * path_sigma
            + np.sqrt(c_sigma * (2.0 - c_sigma) * mu_effective)
            * (inverse_square_root @ weighted_displacement)
        )
        normalized_path = (
            np.linalg.norm(path_sigma)
            / np.sqrt(1.0 - (1.0 - c_sigma) ** (2 * (generation + 1)))
            / chi_n
        )
        h_sigma = float(
            normalized_path < 1.4 + 2.0 / (dimension + 1.0)
        )
        path_c = (
            (1.0 - c_c) * path_c
            + h_sigma
            * np.sqrt(c_c * (2.0 - c_c) * mu_effective)
            * weighted_displacement
        )
        rank_mu = np.zeros_like(covariance)
        for weight, item in zip(weights, selected):
            rank_mu += weight * np.outer(item[2], item[2])
        covariance = (
            (1.0 - c1 - c_mu) * covariance
            + c1
            * (
                np.outer(path_c, path_c)
                + (1.0 - h_sigma) * c_c * (2.0 - c_c) * covariance
            )
            + c_mu * rank_mu
        )
        covariance = 0.5 * (covariance + covariance.T)
        sigma *= np.exp(
            (c_sigma / d_sigma)
            * (np.linalg.norm(path_sigma) / chi_n - 1.0)
        )

        best_energy, _, _, best_parameters = generation_results[0]
        if best_energy < incumbent_energy:
            incumbent = np.asarray(best_parameters, dtype=float).copy()
            incumbent_energy = float(best_energy)
            accepted(incumbent)

    remaining_calls = max(0, optimizer_limit - optimizer_calls)
    if remaining_calls == 0:
        return incumbent

    result = minimize(
        objective,
        incumbent,
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

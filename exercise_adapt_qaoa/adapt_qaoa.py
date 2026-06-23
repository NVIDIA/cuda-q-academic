"""Notebook-style CUDA-Q ADAPT-QAOA for MaxCut.

Edit the settings below, then run:

    python exercise_adapt_qaoa/adapt_qaoa.py

The problem can be written by hand, like the CUDA-Q notebook, or selected from
the local QED-C MaxCut data by setting PROBLEM_SOURCE = "qedc".
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Put the repo root first when this file is imported as a package module.
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

import cudaq
import numpy as np
from scipy.optimize import minimize

try:
    from exercise_adapt_qaoa.run_qedc_input import load_qedc_maxcut
except ModuleNotFoundError:
    # Direct script execution makes this folder the first import location, so
    # fall back to the sibling file.
    from run_qedc_input import load_qedc_maxcut


# ---------------------------------------------------------------------------
# Settings: this is the only section most experiments should need to edit.
# ---------------------------------------------------------------------------

PROBLEM_SOURCE = "manual"  # "manual" or "qedc"

# Manual graph, matching the small example shape used by the CUDA-Q notebook.
MANUAL_NAME = "manual_4q_complete"
MANUAL_QUBITS = 4
MANUAL_EDGES = [(0, 1), (0, 3), (0, 2), (1, 2), (1, 3), (2, 3)]
MANUAL_OPTIMAL_CUT = 4

# QED-C graph selected by name from maxcut_instances/.
QEDC_INSTANCE = "mc_004_003_000"

# ADAPT-QAOA controls.
MAX_ADAPT_ITERS = 1
GRADIENT_TOLERANCE = 1e-12
INITIAL_GAMMA = 0.01
MAX_OPTIMIZER_ITERS = 8
SHOTS = 128
SEED = 5
OUTPUT_DIR = Path(__file__).resolve().parent / "results"


# Bundle the editable constants so tests or other scripts can pass settings
# without mutating module-level globals.
@dataclass(frozen=True)
class RunSettings:
    max_adapt_iters: int = MAX_ADAPT_ITERS
    gradient_tolerance: float = GRADIENT_TOLERANCE
    initial_gamma: float = INITIAL_GAMMA
    max_optimizer_iters: int = MAX_OPTIMIZER_ITERS
    shots: int = SHOTS
    seed: int = SEED


# ---------------------------------------------------------------------------
# CUDA-Q kernels: these mirror the notebook's reference state, gradient probe,
# and current ADAPT-QAOA ansatz.
# ---------------------------------------------------------------------------

@cudaq.kernel
def initial_state(qubits_num: int):
    """Prepare the uniform superposition |+>^n."""
    qubits = cudaq.qvector(qubits_num)
    h(qubits)


@cudaq.kernel
def gradient_state(
    state: cudaq.State,
    ham_words: list[cudaq.pauli_word],
    ham_coefficients: list[complex],
    init_gamma: float,
):
    """Apply a tiny cost-Hamiltonian evolution before measuring gradients."""
    qubits = cudaq.qvector(state)
    for i in range(len(ham_coefficients)):
        exp_pauli(init_gamma * ham_coefficients[i].real, qubits, ham_words[i])


@cudaq.kernel
def adapt_qaoa_ansatz(
    qubits_num: int,
    ham_words: list[cudaq.pauli_word],
    ham_coefficients: list[complex],
    selected_mixers: list[list[cudaq.pauli_word]],
    gamma: list[float],
    beta: list[float],
    layers: int,
):
    """Apply all selected cost and mixer layers."""
    qubits = cudaq.qvector(qubits_num)
    h(qubits)
    for layer in range(layers):
        for i in range(len(ham_coefficients)):
            exp_pauli(gamma[layer] * ham_coefficients[i].real, qubits, ham_words[i])
        for word in selected_mixers[layer]:
            exp_pauli(beta[layer], qubits, word)


# ---------------------------------------------------------------------------
# MaxCut objects: cost Hamiltonian, operator pool, and Pauli-word conversion.
# ---------------------------------------------------------------------------

def set_cudaq_target():
    """Prefer the NVIDIA simulator when available, otherwise use CPU."""
    if cudaq.num_available_gpus() > 0 and cudaq.has_target("nvidia"):
        cudaq.set_target("nvidia", option="fp64")
    else:
        cudaq.set_target("qpp-cpu")


def spin_ham(edges):
    """Problem Hamiltonian H_C = -1/2 sum((I - Zi Zj))."""
    hamiltonian = 0.0
    for i, j in edges:
        hamiltonian += 0.5 * (cudaq.spin.z(i) * cudaq.spin.z(j) - cudaq.spin.i(i) * cudaq.spin.i(j))
    return hamiltonian


def operator_pool(qubits_num: int):
    """Mixer pool A_j from the CUDA-Q ADAPT-QAOA notebook."""
    pool = [cudaq.SpinOperator(cudaq.spin.x(i)) for i in range(qubits_num)]

    global_x = cudaq.spin.x(0)
    for i in range(1, qubits_num):
        global_x += cudaq.spin.x(i)
    pool.append(global_x)

    for i in range(qubits_num - 1):
        for j in range(i + 1, qubits_num):
            pool.append(cudaq.SpinOperator(cudaq.spin.x(i)) * cudaq.SpinOperator(cudaq.spin.x(j)))
            pool.append(cudaq.SpinOperator(cudaq.spin.y(i)) * cudaq.SpinOperator(cudaq.spin.y(j)))
            pool.append(cudaq.SpinOperator(cudaq.spin.y(i)) * cudaq.SpinOperator(cudaq.spin.z(j)))
            pool.append(cudaq.SpinOperator(cudaq.spin.z(i)) * cudaq.SpinOperator(cudaq.spin.y(j)))
    return pool


def pauli_words(operator, qubits_num: int):
    """Return both CUDA-Q pauli_word objects and readable string labels."""
    words = []
    labels = []
    for term in operator:
        label = term.get_pauli_word(qubits_num)
        words.append(cudaq.pauli_word(label))
        labels.append(label)
    return words, labels


def spin_words(hamiltonian, qubits_num: int):
    """Convert each Hamiltonian term into the pauli_word format exp_pauli needs."""
    return [cudaq.pauli_word(term.get_pauli_word(qubits_num)) for term in hamiltonian]


def spin_coefficients(hamiltonian):
    """Extract numeric coefficients from each Hamiltonian term."""
    return [term.evaluate_coefficient() for term in hamiltonian]


# ---------------------------------------------------------------------------
# Classical helpers: evaluate sampled bitstrings and choose the problem source.
# ---------------------------------------------------------------------------

def cut_value(bitstring: str, edges) -> int:
    """Count graph edges whose endpoints are assigned different bit values."""
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def best_sample(counts, edges):
    """Choose the sampled bitstring with the best MaxCut value."""
    return max(counts, key=lambda bitstring: (cut_value(bitstring, edges), counts[bitstring]))


def sample_counts(sample_result):
    """Convert CUDA-Q sample output into a plain {bitstring: count} dictionary."""
    if hasattr(sample_result, "items"):
        return {str(bitstring): int(count) for bitstring, count in sample_result.items()}
    return {str(bitstring): int(sample_result.count(bitstring)) for bitstring in sample_result}


def choose_problem():
    """Select either the manual graph above or the named QED-C input."""
    if PROBLEM_SOURCE == "manual":
        return MANUAL_NAME, MANUAL_QUBITS, MANUAL_EDGES, MANUAL_OPTIMAL_CUT
    if PROBLEM_SOURCE == "qedc":
        problem = load_qedc_maxcut(QEDC_INSTANCE)
        return problem.name, problem.qubits_num, problem.edges, problem.optimal_cut
    raise ValueError('PROBLEM_SOURCE must be "manual" or "qedc"')


# ---------------------------------------------------------------------------
# ADAPT-QAOA loop: measure commutator gradients, append a mixer, optimize, sample.
# ---------------------------------------------------------------------------

def run_adapt_qaoa(
    qubits_num: int,
    edges,
    optimal_cut: int | None = None,
    name: str = "maxcut",
    settings: RunSettings = RunSettings(),
    output_dir: str | Path = OUTPUT_DIR,
):
    """Run the ADAPT-QAOA loop on a MaxCut graph."""
    set_cudaq_target()
    cudaq.set_random_seed(settings.seed)
    random.seed(settings.seed)

    # Build H_C, the mixer pool A_j, and [H_C, A_j] for gradient selection.
    hamiltonian = spin_ham(edges)
    ham_words = spin_words(hamiltonian, qubits_num)
    ham_coefficients = spin_coefficients(hamiltonian)
    pool = operator_pool(qubits_num)
    commutators = [hamiltonian * operator - operator * hamiltonian for operator in pool]

    state = cudaq.get_state(initial_state, qubits_num)
    gamma = []
    beta = []
    selected_mixers = []
    layers = []

    for step in range(settings.max_adapt_iters):
        # Pick the next mixer from the largest commutator-gradient signal.
        gradients = []
        for commutator in commutators:
            value = cudaq.observe(
                gradient_state,
                commutator * (-1j),
                state,
                ham_words,
                ham_coefficients,
                settings.initial_gamma,
            ).expectation()
            gradients.append(float(value))

        gradient_norm = float(np.linalg.norm(gradients))
        if gradient_norm <= settings.gradient_tolerance:
            break

        selected_index = int(np.argmax(np.abs(gradients)))
        mixer_words, mixer_labels = pauli_words(pool[selected_index], qubits_num)
        selected_mixers.append(mixer_words)
        gamma.append(settings.initial_gamma)
        beta.append(0.0)
        layer_count = len(selected_mixers)

        # Re-optimize all active gamma/beta parameters after each new layer.
        def cost(theta):
            return float(
                cudaq.observe(
                    adapt_qaoa_ansatz,
                    hamiltonian,
                    qubits_num,
                    ham_words,
                    ham_coefficients,
                    selected_mixers,
                    list(theta[:layer_count]),
                    list(theta[layer_count:]),
                    layer_count,
                ).expectation()
            )

        optimized = minimize(
            cost,
            np.array(gamma + beta),
            method="BFGS",
            jac="2-point",
            options={"maxiter": settings.max_optimizer_iters},
        )
        theta = [float(value) for value in optimized.x.tolist()]
        gamma = theta[:layer_count]
        beta = theta[layer_count:]
        energy = float(optimized.fun)
        layers.append(
            {
                "step": step + 1,
                "gradient_norm": gradient_norm,
                "mixer": mixer_labels,
                "energy": energy,
            }
        )
        state = cudaq.get_state(
            adapt_qaoa_ansatz,
            qubits_num,
            ham_words,
            ham_coefficients,
            selected_mixers,
            gamma,
            beta,
            layer_count,
        )

    # The final sampling step turns the optimized state into a candidate cut.
    counts = sample_counts(
        cudaq.sample(
            adapt_qaoa_ansatz,
            qubits_num,
            ham_words,
            ham_coefficients,
            selected_mixers,
            gamma,
            beta,
            len(selected_mixers),
            shots_count=settings.shots,
        )
    )
    bitstring = best_sample(counts, edges)
    sampled_cut = cut_value(bitstring, edges)
    final_energy = layers[-1]["energy"] if layers else float(cudaq.observe(initial_state, hamiltonian, qubits_num).expectation())

    result = {
        "name": name,
        "qubits_num": qubits_num,
        "edges": edges,
        "layers": layers,
        "gamma": gamma,
        "beta": beta,
        "final_energy": final_energy,
        "best_bitstring": bitstring,
        "sampled_cut": sampled_cut,
        "optimal_cut": optimal_cut,
        "approx_ratio": final_energy / -optimal_cut if optimal_cut else None,
    }

    output_path = Path(output_dir) / f"{name}_adapt_qaoa.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run_from_top_level_settings(output_dir: str | Path = OUTPUT_DIR):
    """Convenience entry point for running the file like a notebook/script."""
    name, qubits_num, edges, optimal_cut = choose_problem()
    return run_adapt_qaoa(qubits_num, edges, optimal_cut, name, RunSettings(), output_dir)


if __name__ == "__main__":
    summary = run_from_top_level_settings()
    print(json.dumps(summary, indent=2))

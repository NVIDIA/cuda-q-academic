import pytest

from hamiltonian import (
    MaxCutSolution,
    approx_ratio_from_energy,
    bitstring_energy,
    compare_sampled_to_solution,
    emin_from_optimal_cut,
    evaluate_cut,
)


def test_evaluate_cut_counts_edges_across_partitions():
    edges = [(0, 1), (0, 2), (1, 2)]

    assert evaluate_cut([1, 0, 1], edges) == 2


def test_bitstring_energy_is_negative_cut_value():
    edges = [(0, 1), (0, 2), (1, 2)]

    assert bitstring_energy([1, 0, 1], edges) == -2.0


def test_energy_based_approximation_ratio_uses_qedc_hamiltonian_convention():
    emin = emin_from_optimal_cut(4)

    assert emin == -4.0
    assert approx_ratio_from_energy(-3.0, emin) == pytest.approx(0.75)


def test_compare_sampled_to_solution_reports_gap_from_provided_solution():
    solution = MaxCutSolution(
        name="toy",
        objective=3,
        bitstring=[1, 0, 1],
        path=None,
    )
    comparison = compare_sampled_to_solution([1, 1, 0], [(0, 1), (0, 2), (1, 2)], solution)

    assert comparison == {
        "sampled_cut": 2,
        "optimal_cut": 3,
        "opt_gap": 1,
        "matches_optimal_cut": False,
    }

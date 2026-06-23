import subprocess
import sys

import pytest

from exercise_adapt_qaoa.run_qedc_input import (
    DEFAULT_DATA_DIR,
    QedcInputError,
    list_qedc_instances,
    load_qedc_maxcut,
)


def test_lists_qedc_instances():
    names = list_qedc_instances(DEFAULT_DATA_DIR)

    assert len(names) == 26
    assert "mc_004_003_000" in names
    assert "mc_006_003_000" in names
    assert "mc_008_003_000" in names
    assert "mc_320_003_000" in names


def test_each_qedc_instance_has_a_solution_file():
    for name in list_qedc_instances(DEFAULT_DATA_DIR):
        assert (DEFAULT_DATA_DIR / f"{name}.sol").exists()


def test_loads_qedc_problem_by_name():
    problem = load_qedc_maxcut("mc_004_003_000", DEFAULT_DATA_DIR)

    assert problem.name == "mc_004_003_000"
    assert problem.qubits_num == 4
    assert problem.edges == [(0, 1), (0, 3), (0, 2), (1, 2), (1, 3), (2, 3)]
    assert problem.optimal_cut == 4


def test_rejects_missing_qedc_problem():
    with pytest.raises(QedcInputError, match="not found"):
        load_qedc_maxcut("missing_case", DEFAULT_DATA_DIR)


def test_qedc_script_can_list_inputs():
    completed = subprocess.run(
        [sys.executable, "exercise_adapt_qaoa/run_qedc_input.py", "--list"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "mc_004_003_000" in completed.stdout

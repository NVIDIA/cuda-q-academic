from pathlib import Path

import pytest

from conftest import DATA_DIR
from hamiltonian import read_maxcut_instance, read_maxcut_solution


CASES = {
    "mc_008_003_000": {
        "nodes": 8,
        "edges": [
            (0, 1),
            (0, 7),
            (0, 6),
            (1, 7),
            (1, 3),
            (7, 2),
            (2, 4),
            (2, 5),
            (4, 3),
            (4, 5),
            (3, 6),
            (6, 5),
        ],
        "objective": 10,
        "solution": [1, 0, 1, 1, 0, 1, 0, 0],
    },
}


def test_required_qedc_fixture_files_exist():
    for case in CASES:
        assert (DATA_DIR / f"{case}.txt").exists()
        assert (DATA_DIR / f"{case}.sol").exists()


@pytest.mark.parametrize("case, expected", CASES.items())
def test_reads_qedc_instance_files(case, expected):
    instance = read_maxcut_instance(DATA_DIR / f"{case}.txt")

    assert instance.name == case
    assert instance.nodes == expected["nodes"]
    assert instance.edges == expected["edges"]


@pytest.mark.parametrize("case, expected", CASES.items())
def test_reads_qedc_solution_files(case, expected):
    solution = read_maxcut_solution(DATA_DIR / f"{case}.sol", expected["nodes"])

    assert solution.name == case
    assert solution.objective == expected["objective"]
    assert solution.bitstring == expected["solution"]


def test_rejects_empty_instance_file(tmp_path: Path):
    bad_file = tmp_path / "empty.txt"
    bad_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="node count"):
        read_maxcut_instance(bad_file)


def test_rejects_bad_edge_tokens(tmp_path: Path):
    bad_file = tmp_path / "bad-edge.txt"
    bad_file.write_text("4\n0 x\n", encoding="utf-8")

    with pytest.raises(ValueError, match="edge"):
        read_maxcut_instance(bad_file)


def test_rejects_wrong_solution_length(tmp_path: Path):
    bad_file = tmp_path / "bad.sol"
    bad_file.write_text("4\n1 0 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="length"):
        read_maxcut_solution(bad_file, expected_nodes=4)

import json
import subprocess
import sys

from exercise_adapt_qaoa.adapt_qaoa import (
    MANUAL_EDGES,
    MANUAL_QUBITS,
    QEDC_INSTANCE,
    PROBLEM_SOURCE,
    RunSettings,
    choose_problem,
    run_adapt_qaoa,
    run_from_top_level_settings,
)


def test_manual_problem_is_available_at_top_of_file():
    assert MANUAL_QUBITS == 4
    assert MANUAL_EDGES == [(0, 1), (0, 3), (0, 2), (1, 2), (1, 3), (2, 3)]


def test_top_level_settings_default_to_qedc_workshop_instance():
    name, qubits_num, edges, optimal_cut = choose_problem()

    assert PROBLEM_SOURCE == "qedc"
    assert QEDC_INSTANCE == "mc_008_005_000"
    assert name == QEDC_INSTANCE
    assert qubits_num == 8
    assert len(edges) == 20
    assert optimal_cut == 16


def test_small_manual_adapt_qaoa_run_writes_summary(tmp_path):
    result = run_adapt_qaoa(
        qubits_num=4,
        edges=MANUAL_EDGES,
        optimal_cut=4,
        name="manual_test",
        settings=RunSettings(max_adapt_iters=1, shots=128, max_optimizer_iters=8, seed=5),
        output_dir=tmp_path,
    )

    assert result["name"] == "manual_test"
    assert len(result["layers"]) == 1
    assert result["final_energy"] <= 0.0
    assert len(result["best_bitstring"]) == 4
    assert result["sampled_cut"] <= 4

    output_path = tmp_path / "manual_test_adapt_qaoa.json"
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8"))["name"] == "manual_test"


def test_top_level_settings_runner_accepts_output_dir(tmp_path):
    result = run_from_top_level_settings(output_dir=tmp_path)

    assert result["qubits_num"] >= 1
    assert (tmp_path / f"{result['name']}_adapt_qaoa.json").exists()


def test_adapt_qaoa_script_runs_directly():
    completed = subprocess.run(
        [sys.executable, "exercise_adapt_qaoa/adapt_qaoa.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "mc_008_005_000" in completed.stdout
    assert "Final energy:" in completed.stdout
    assert "Iterations:" in completed.stdout
    assert "Total time:" in completed.stdout

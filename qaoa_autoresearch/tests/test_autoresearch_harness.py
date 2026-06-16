import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = PROJECT_ROOT / "harness.py"
CANDIDATE_KERNEL_PATH = PROJECT_ROOT / "candidate_kernel.py"

spec = importlib.util.spec_from_file_location("autoresearch_harness", HARNESS_PATH)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def test_fixed_main_kernel_owns_qubit_setup_and_superposition():
    source = HARNESS_PATH.read_text(encoding="utf-8")

    assert hasattr(harness, "main_kernel")
    assert "def main_kernel(angles: List[float]):" in source
    assert "qubits = cudaq.qvector(QUBITS)" in source
    assert "h(qubits)" in source
    assert "candidate_superkernel(qubits, angles)" in source


def test_candidate_kernel_is_editable_superkernel_only():
    candidate = harness._load_candidate_module()
    source = CANDIDATE_KERNEL_PATH.read_text(encoding="utf-8")

    assert candidate.PARAMETER_COUNT == 6
    assert harness._parameter_count(candidate) == 6
    assert hasattr(candidate, "candidate_superkernel")
    assert not hasattr(candidate, "candidate_ansatz")
    assert "def candidate_superkernel(qubits: cudaq.qview, angles: List[float]):" in source


def test_candidate_superkernel_is_custom_six_parameter_rx_ry_rz_cnot_ansatz():
    source = CANDIDATE_KERNEL_PATH.read_text(encoding="utf-8")

    assert "edges_src" not in source
    assert "edges_tgt" not in source
    assert "edge_index" not in source
    for parameter_index in range(6):
        assert f"angles[{parameter_index}]" in source
    assert "rz(" in source
    assert "rx(" in source
    assert "x.ctrl(qubits[0], qubits[1])" in source


def test_harness_scores_gate_counts_from_cudaq_kernel_trace():
    candidate = harness._load_candidate_module()

    single_count, two_count = harness._gate_counts(candidate)

    assert single_count > 0
    assert two_count > 0
    assert harness._gate_score(single_count, two_count) == single_count + 10 * two_count


def test_candidate_kernel_does_not_declare_gate_counts():
    candidate = harness._load_candidate_module()

    assert not hasattr(candidate, "SINGLE_QUBIT_GATES")
    assert not hasattr(candidate, "TWO_QUBIT_GATES")


def test_harness_owns_fixed_real_instance_metadata():
    candidate = harness._load_candidate_module()

    assert harness.INSTANCE == "instances/mc_008_003_000.txt"
    assert harness.SOLUTION == "instances/mc_008_003_000.sol"
    assert harness.QUBITS == 8
    assert not hasattr(candidate, "INSTANCE")
    assert not hasattr(candidate, "SOLUTION")
    assert not hasattr(candidate, "QUBITS")


def test_harness_initializes_two_zero_parameters_per_layer():
    candidate = harness._load_candidate_module()

    assert harness._initial_parameters(candidate).tolist() == [0.0] * 6


def test_candidate_kernel_does_not_define_optimizer_parameters_or_subkernels():
    candidate = harness._load_candidate_module()

    assert not hasattr(candidate, "BASELINE_PARAMETERS")
    assert not hasattr(candidate, "LAYER_COUNT")
    assert not hasattr(candidate, "initial_parameters")
    assert not hasattr(candidate, "qaoa_cost_edge")
    assert not hasattr(candidate, "qaoa_mixer")


def test_harness_loads_candidate_kernel_file_not_json_candidate():
    assert harness.CANDIDATE_KERNEL_PATH == CANDIDATE_KERNEL_PATH
    assert not hasattr(harness, "CANDIDATE_PATH")


def test_harness_uses_40_iteration_budget_by_default():
    assert harness.DEFAULT_MAX_ITERATIONS == 40


def test_baseline_ratio_defines_five_percent_passing_threshold():
    baseline_ratio = 0.82

    assert harness._pass_threshold(baseline_ratio) == 0.779
    assert harness._is_passing(0.779, baseline_ratio)
    assert harness._is_passing(0.90, baseline_ratio)
    assert not harness._is_passing(0.778999, baseline_ratio)


def test_objective_minimizes_gate_score_only_inside_baseline_band_or_better():
    baseline_ratio = 0.80

    assert harness._objective(0.77, 42, baseline_ratio) == 42.0
    assert harness._objective(0.759, 1, baseline_ratio) > 1_000_000.0


def test_report_rows_include_pass_status_from_baseline_ratio():
    row = {
        "round": 2,
        "change": "custom ansatz",
        "note": "n/a",
        "approx_ratio": 0.77,
        "baseline_ratio": 0.80,
        "pass_threshold": 0.76,
        "gate_score": 42.0,
        "objective": 42.0,
        "pass": "green",
        "keep": "yes",
    }

    assert harness._row_pass_color(row) == "green"
    row["approx_ratio"] = 0.75
    assert harness._row_pass_color(row) == "red"


def test_label_annotations_collapse_exact_duplicate_points_to_first_run():
    rows = [
        {"round": 4, "gate_score": 42.0, "approx_ratio": 0.81},
        {"round": 7, "gate_score": 42.0, "approx_ratio": 0.81},
        {"round": 9, "gate_score": 42.0, "approx_ratio": 0.81},
        {"round": 10, "gate_score": 55.0, "approx_ratio": 0.79},
    ]

    annotations = harness._label_annotations(rows)

    assert [(label, row["round"]) for row, label, _offset in annotations] == [
        ("4*", 4),
        ("10", 10),
    ]


def test_report_notes_asterisk_for_duplicate_points():
    source = HARNESS_PATH.read_text(encoding="utf-8")

    assert "multiple runs produced this result" in source


def test_report_scatter_does_not_connect_runs_with_line():
    source = HARNESS_PATH.read_text(encoding="utf-8")

    assert "ax.scatter(x, y" in source
    assert "ax.plot(x, y" not in source

"""Evaluate one fixed circuit with one researcher's tensornet settings."""

import argparse
import ast
import json
import math
import os
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parent
REFERENCE_PATH = ROOT / "reference.json"
CIRCUITS = ("nonlocal", "controlled")
SETTING_KEYS = {
    "precision",
    "controlled_rank",
    "path_reuse",
    "hyper_samples",
    "find_threads",
    "find_limit",
    "deterministic",
    "scratch_percentage",
}


def experiment_path(circuit):
    return ROOT / "research" / circuit / "experiment.py"


def load_experiment(path):
    """Parse researcher-authored literals without executing their code."""
    path = Path(path)
    tree = ast.parse(path.read_text(), filename=str(path))
    values = {}
    allowed_names = {"SETTINGS", "RATIONALE", "HYPOTHESIS"}

    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        if (
            not isinstance(node, ast.Assign)
            or len(node.targets) != 1
            or not isinstance(node.targets[0], ast.Name)
        ):
            raise ValueError(
                "experiment.py may contain only literal SETTINGS, RATIONALE, "
                "and HYPOTHESIS assignments"
            )
        name = node.targets[0].id
        if name not in allowed_names or name in values:
            raise ValueError(f"unexpected or duplicate assignment: {name}")
        values[name] = ast.literal_eval(node.value)

    if set(values) != allowed_names:
        raise ValueError(
            "experiment.py must define SETTINGS, RATIONALE, and HYPOTHESIS"
        )
    settings = values["SETTINGS"]
    if not isinstance(settings, dict) or set(settings) != SETTING_KEYS:
        raise ValueError(
            f"SETTINGS must contain exactly: {sorted(SETTING_KEYS)}"
        )

    if settings["precision"] not in {"fp32", "fp64"}:
        raise ValueError("precision must be fp32 or fp64")
    integer_ranges = {
        "controlled_rank": (1, 8),
        "hyper_samples": (1, 128),
        "find_threads": (1, 64),
        "scratch_percentage": (5, 95),
    }
    for name, (minimum, maximum) in integer_ranges.items():
        value = settings[name]
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(
                f"{name} must be an integer from {minimum} through {maximum}"
            )
    for name in ("path_reuse", "find_limit", "deterministic"):
        if type(settings[name]) is not bool:
            raise ValueError(f"{name} must be True or False")

    for name in ("RATIONALE", "HYPOTHESIS"):
        text = values[name]
        if not isinstance(text, str) or len(text.strip()) < 30:
            raise ValueError(f"{name} must be a concrete explanatory sentence")
        values[name] = " ".join(text.split())
    return settings, values["RATIONALE"], values["HYPOTHESIS"]


def configure_environment(settings):
    def on_off(value):
        return "ON" if value else "OFF"

    os.environ["CUDAQ_TENSORNET_CONTROLLED_RANK"] = str(
        settings["controlled_rank"]
    )
    os.environ["CUDAQ_TENSORNET_OBSERVE_CONTRACT_PATH_REUSE"] = on_off(
        settings["path_reuse"]
    )
    os.environ["CUDAQ_TENSORNET_NUM_HYPER_SAMPLES"] = str(
        settings["hyper_samples"]
    )
    os.environ["CUDAQ_TENSORNET_FIND_THREADS"] = str(settings["find_threads"])
    os.environ["CUDAQ_TENSORNET_FIND_LIMIT"] = on_off(settings["find_limit"])
    os.environ["CUDAQ_TENSORNET_FIND_DETERMINISTIC"] = on_off(
        settings["deterministic"]
    )
    os.environ["CUDAQ_TENSORNET_SCRATCH_SIZE_PERCENTAGE"] = str(
        settings["scratch_percentage"]
    )


def run_evaluation(circuit, path):
    settings, rationale, hypothesis = load_experiment(path)
    configure_environment(settings)

    import cudaq

    cudaq.set_target("tensornet", option=settings["precision"])
    cudaq.set_random_seed(20260723)

    from benchmark import benchmark_signature, run_circuit

    reference = json.loads(REFERENCE_PATH.read_text())
    if reference["benchmark_sha256"] != benchmark_signature():
        raise RuntimeError(
            "benchmark.py does not match reference.json; restore the fixed "
            "benchmark before running comparable experiments"
        )

    started = time.perf_counter()
    value = float(run_circuit(circuit))
    elapsed = time.perf_counter() - started
    expected = reference["circuits"][circuit]["expectation"]
    tolerance = reference["circuits"][circuit]["absolute_tolerance"]
    valid = math.isfinite(value) and abs(value - expected) <= tolerance
    result = {
        "circuit": circuit,
        "settings": settings,
        "rationale": rationale,
        "hypothesis": hypothesis,
        "runtime_seconds": elapsed,
        "expectation": value,
        "expected": expected,
        "absolute_error": abs(value - expected),
        "valid": valid,
    }
    print(
        f"{circuit}: {elapsed:.6f}s, value={value:.12f}, "
        f"valid={'yes' if valid else 'no'}",
        flush=True,
    )
    print("RESULT_JSON:" + json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("circuit", choices=CIRCUITS)
    parser.add_argument("--experiment", type=Path)
    args = parser.parse_args()
    path = args.experiment or experiment_path(args.circuit)
    run_evaluation(args.circuit, path)


if __name__ == "__main__":
    main()

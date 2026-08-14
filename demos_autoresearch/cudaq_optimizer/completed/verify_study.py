"""Validate pristine and completed observe-budgeted autoresearch states."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np

from benchmark import (
    CASES,
    benchmark_signature,
    case_specification,
    initial_parameters,
    initial_parameters_sha256,
)
from integrity import validate_fixed_files
from run_round import MAX_ROUNDS, PENDING_REASONING, prefix_metrics
from summarize_results import ENERGY_TIE_TOLERANCE, winner


ROOT = Path(__file__).resolve().parent
READY_ARTIFACTS = (
    "results.tsv",
    "traces",
    "sources",
    "logs",
    "insights.md",
    "figure_summary.txt",
    "summary.md",
)
ROOT_OUTPUTS = (
    "lowest_energy_by_round.png",
    "energy_trajectories_3d.png",
    "energy_trajectories_3d.html",
    "summary.md",
)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ledger_rows(case):
    path = ROOT / "research" / case / "results.tsv"
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _optional_int(value):
    return int(value) if value not in (None, "") else None


def _optional_float(value):
    return float(value) if value not in (None, "") else None


def _same_float(first, second, tolerance=1e-10):
    if first is None or second is None:
        return first is None and second is None
    return math.isclose(
        float(first),
        float(second),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def validate_reference():
    errors = []
    try:
        reference = json.loads((ROOT / "reference.json").read_text())
    except Exception as error:
        return [f"reference.json is invalid: {error}"]
    if reference.get("benchmark_sha256") != benchmark_signature():
        errors.append("benchmark hash does not match reference.json")
    if reference.get("target") != "nvidia":
        errors.append("CUDA-Q target must be nvidia")
    if reference.get("target_option") != "fp64":
        errors.append("CUDA-Q nvidia target option must be fp64")
    if set(reference.get("cases", {})) != set(CASES):
        errors.append("reference.json case registry is incorrect")
        return errors
    for case in CASES:
        entry = reference["cases"][case]
        specification = case_specification(case)
        if entry.get("initial_parameters_sha256") != (
            initial_parameters_sha256(case)
        ):
            errors.append(f"{case} initial parameter hash is incorrect")
        if entry.get("exact_energy") != specification["exact_energy"]:
            errors.append(f"{case} diagnostic exact energy is incorrect")
        if (
            not isinstance(entry.get("time_budget_seconds"), (int, float))
            or entry["time_budget_seconds"] != 120
        ):
            errors.append(
                f"{case} secondary time guard must be exactly 120 seconds"
            )
        if entry.get("max_calls") != 300:
            errors.append(f"{case} max_calls must be exactly 300")
        if entry.get("energy_tie_tolerance") != ENERGY_TIE_TOLERANCE:
            errors.append(
                f"{case} energy tie tolerance must be "
                f"{ENERGY_TIE_TOLERANCE:g}"
            )
        for field in ("energy_delta_tolerance",):
            value = entry.get(field)
            if not isinstance(value, (int, float)) or value <= 0.0:
                errors.append(f"{case} {field} must be positive")
        for field in (
            "energy_delta_patience",
            "minimum_accepted_iterations",
        ):
            value = entry.get(field)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"{case} {field} must be a positive integer")
        if entry["minimum_accepted_iterations"] < entry[
            "energy_delta_patience"
        ]:
            errors.append(
                f"{case} minimum accepted iterations must be at least patience"
            )
    return errors


def validate_ready():
    errors = validate_fixed_files() + validate_reference()
    initial = (ROOT / "initial_optimizer.py").read_text()
    research_root = ROOT / "research"
    actual_cases = {
        path.name
        for path in research_root.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    }
    if actual_cases != set(CASES):
        errors.append(
            f"research case directories are {sorted(actual_cases)}, "
            f"expected {sorted(CASES)}"
        )
    for case in CASES:
        directory = research_root / case
        proposal = directory / "optimizer.py"
        if not proposal.exists() or proposal.read_text() != initial:
            errors.append(
                f"{case} optimizer does not match round-one template"
            )
        for name in READY_ARTIFACTS:
            if (directory / name).exists():
                errors.append(f"unexpected ready-state artifact: {case}/{name}")
    for name in ROOT_OUTPUTS:
        if (ROOT / name).exists():
            errors.append(f"unexpected ready-state artifact: {name}")
    return errors


def valid_rows(rows):
    return [
        row
        for row in rows
        if row.get("valid") == "yes" and row.get("best_energy")
    ]


def _validate_convergence(label, row, result, trace, reference):
    errors = []
    convergence = result.get("convergence")
    if not convergence:
        if row.get("converged") == "yes":
            errors.append(f"{label} claims convergence without records")
        return errors

    tolerance = float(reference["energy_delta_tolerance"])
    patience = int(reference["energy_delta_patience"])
    minimum = int(reference["minimum_accepted_iterations"])
    if not _same_float(convergence.get("energy_delta_tolerance"), tolerance):
        errors.append(f"{label} has wrong convergence tolerance")
    if convergence.get("patience") != patience:
        errors.append(f"{label} has wrong convergence patience")
    if convergence.get("minimum_accepted_iterations") != minimum:
        errors.append(f"{label} has wrong minimum accepted iterations")

    records = convergence.get("records", [])
    calculated_reached = False
    calculated_call = None
    previous_energy = None
    previous_call = 0
    streak = 0
    for index, record in enumerate(records):
        if record.get("iteration") != index:
            errors.append(f"{label} accepted iterations are not sequential")
        call = int(record.get("call", 0))
        observation_call = int(record.get("observation_call", 0))
        if call <= previous_call or call > len(trace):
            errors.append(f"{label} accepted iteration {index} has bad call")
            continue
        if observation_call <= 0 or observation_call > call:
            errors.append(
                f"{label} accepted iteration {index} has bad observation call"
            )
            continue
        observation = trace[observation_call - 1]
        parameters = np.asarray(record.get("parameters"), dtype=float)
        if not np.array_equal(
            parameters,
            np.asarray(observation.get("parameters"), dtype=float),
        ):
            errors.append(
                f"{label} accepted iteration {index} parameters mismatch"
            )
        energy = float(record["energy"])
        if not _same_float(energy, observation["energy"]):
            errors.append(f"{label} accepted iteration {index} energy mismatch")
        if index == 0:
            if call != 1 or observation_call != 1:
                errors.append(f"{label} initial accepted point is not call 1")
            if record.get("delta_energy") is not None:
                errors.append(f"{label} initial delta must be null")
            if record.get("convergence_streak") != 0:
                errors.append(f"{label} initial streak must be zero")
        else:
            delta = abs(energy - previous_energy)
            streak = streak + 1 if delta <= tolerance + 1e-15 else 0
            if not _same_float(record.get("delta_energy"), delta):
                errors.append(f"{label} accepted delta is incorrect")
            if record.get("convergence_streak") != streak:
                errors.append(f"{label} accepted streak is incorrect")
            reached = index >= minimum and streak >= patience
            if reached and not calculated_reached:
                calculated_reached = True
                calculated_call = call
                if index != len(records) - 1:
                    errors.append(f"{label} continued after convergence")
        previous_energy = energy
        previous_call = call

    accepted_iterations = max(0, len(records) - 1)
    if convergence.get("accepted_iterations") != accepted_iterations:
        errors.append(f"{label} accepted iteration count is inconsistent")
    if bool(convergence.get("reached")) != calculated_reached:
        errors.append(f"{label} convergence flag is inconsistent")
    recorded_converged = row.get("converged") == "yes"
    if recorded_converged != calculated_reached:
        errors.append(f"{label} ledger convergence flag is incorrect")
    if _optional_int(row.get("calls_to_convergence")) != calculated_call:
        errors.append(f"{label} calls_to_convergence is incorrect")
    if calculated_reached and len(trace) != calculated_call:
        errors.append(f"{label} contains calls after convergence")
    if _optional_int(row.get("accepted_iterations")) != accepted_iterations:
        errors.append(f"{label} ledger accepted iteration count is wrong")
    if _optional_int(row.get("convergence_streak")) != streak:
        errors.append(f"{label} ledger streak is wrong")
    return errors


def _validate_trace(case, row, result, reference):
    errors = []
    label = f"{case} round {row['round']}"
    trace = result.get("trace", [])
    calls_used = _optional_int(row.get("calls_used"))
    if calls_used is not None and len(trace) != calls_used:
        errors.append(
            f"{label} trace length {len(trace)} != calls_used {calls_used}"
        )
    if [entry.get("call") for entry in trace] != list(
        range(1, len(trace) + 1)
    ):
        errors.append(f"{label} trace calls are not sequential")
    if len(trace) > int(reference["max_calls"]):
        errors.append(f"{label} exceeded the hard observe budget")
    if result.get("status") == "call_cap" and len(trace) != int(
        reference["max_calls"]
    ):
        errors.append(f"{label} call cap did not stop at the exact budget")

    parameter_count = int(case_specification(case)["parameter_count"])
    running_best = math.inf
    best_parameters = None
    previous_elapsed = -1.0
    for index, entry in enumerate(trace):
        parameters = np.asarray(entry.get("parameters"), dtype=float)
        if parameters.shape != (parameter_count,):
            errors.append(f"{label} trace has wrong parameter shape")
            break
        if not np.all(np.isfinite(parameters)):
            errors.append(f"{label} trace has non-finite parameters")
            break
        energy = float(entry["energy"])
        elapsed = float(entry["elapsed_s"])
        if not math.isfinite(energy) or elapsed < previous_elapsed:
            errors.append(f"{label} trace energy/time is invalid")
            break
        if energy < running_best:
            running_best = energy
            best_parameters = parameters.copy()
        if not _same_float(entry.get("best_energy"), running_best):
            errors.append(f"{label} running best energy is incorrect")
            break
        previous_elapsed = elapsed

    if trace:
        if trace[0].get("phase") != "initial":
            errors.append(f"{label} first call is not initial")
        if not np.array_equal(
            np.asarray(trace[0]["parameters"], dtype=float),
            initial_parameters(case),
        ):
            errors.append(f"{label} did not use the fixed start")
    recorded_valid = row.get("valid") == "yes"
    result_valid = bool(result.get("valid"))
    if recorded_valid != result_valid:
        errors.append(f"{label} ledger/result valid flags disagree")
    if recorded_valid:
        if not trace or not math.isfinite(running_best):
            errors.append(f"{label} valid result lacks finite observations")
        if not _same_float(row.get("best_energy"), running_best):
            errors.append(f"{label} ledger best energy is incorrect")
        returned = np.asarray(result.get("returned_parameters"), dtype=float)
        if best_parameters is None or not np.array_equal(
            returned, best_parameters
        ):
            errors.append(f"{label} did not return lowest-energy parameters")

    if row.get("status") != result.get("status"):
        errors.append(f"{label} ledger/result status mismatch")
    expected_time_cap = result.get("status") == "time_cap"
    if (row.get("time_cap_reached") == "yes") != expected_time_cap:
        errors.append(f"{label} time-cap flag is incorrect")
    if not _same_float(
        row.get("time_budget_s"), reference["time_budget_seconds"]
    ):
        errors.append(f"{label} ledger secondary time guard is incorrect")
    if not _same_float(
        result.get("time_budget_seconds"), reference["time_budget_seconds"]
    ):
        errors.append(f"{label} result secondary time guard is incorrect")
    if not _same_float(row.get("evaluator_elapsed_s"), result.get("elapsed_s")):
        errors.append(f"{label} evaluator elapsed time is inconsistent")
    if expected_time_cap and float(result.get("elapsed_s", 0)) < 119.0:
        errors.append(f"{label} time cap fired substantially early")
    errors.extend(_validate_convergence(label, row, result, trace, reference))
    return errors


def _sentence_count(text):
    return len(
        [
            sentence
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if sentence.strip()
        ]
    )


def validate_complete():
    errors = validate_fixed_files() + validate_reference()
    reference = json.loads((ROOT / "reference.json").read_text())
    initial_source = (ROOT / "initial_optimizer.py").read_text()
    actual_cases = {
        path.name
        for path in (ROOT / "research").iterdir()
        if path.is_dir() and not path.name.startswith("__")
    }
    if actual_cases != set(CASES):
        errors.append(
            f"research case directories are {sorted(actual_cases)}, "
            f"expected {sorted(CASES)}"
        )

    for case in CASES:
        directory = ROOT / "research" / case
        rows = ledger_rows(case)
        if len(rows) != MAX_ROUNDS:
            errors.append(
                f"{case} has {len(rows)} rows, expected {MAX_ROUNDS}"
            )
            continue
        if [int(row["round"]) for row in rows] != list(
            range(1, MAX_ROUNDS + 1)
        ):
            errors.append(f"{case} round numbers are not sequential")

        for index, row in enumerate(rows):
            round_number = index + 1
            label = f"{case} round {round_number}"
            if not row["reasoning_for_change"] or not row["hypothesis"]:
                errors.append(f"{label} lacks rationale or hypothesis")
            if index < MAX_ROUNDS - 1 and (
                not row["next_round_reasoning"]
                or row["next_round_reasoning"] == PENDING_REASONING
            ):
                errors.append(f"{label} lacks next-round reasoning")

            source_path = (
                directory
                / "sources"
                / f"round_{round_number:03d}_optimizer.py"
            )
            trace_path = (
                directory / "traces" / f"round_{round_number:03d}.json"
            )
            log_path = directory / "logs" / f"round_{round_number:03d}.log"
            for path in (source_path, trace_path, log_path):
                if not path.exists():
                    errors.append(f"{label} is missing {path.name}")
            if not source_path.exists() or not trace_path.exists():
                continue
            if sha256_file(source_path) != row["optimizer_source_sha256"]:
                errors.append(f"{label} source hash does not match snapshot")
            if round_number == 1 and source_path.read_text() != initial_source:
                errors.append(f"{case} round 1 is not the fixed baseline")
            try:
                result = json.loads(trace_path.read_text())
            except Exception as error:
                errors.append(f"{label} trace JSON is invalid: {error}")
                continue
            if result.get("round") != round_number:
                errors.append(f"{label} trace has wrong round number")
            errors.extend(
                _validate_trace(
                    case,
                    row,
                    result,
                    reference["cases"][case],
                )
            )

            metrics = prefix_metrics(rows[:round_number])
            if not _same_float(
                row.get("best_energy_so_far"), metrics["best_energy"]
            ):
                errors.append(f"{label} best-energy prefix is incorrect")
            recorded_improved = row.get("improved_best_so_far") == "yes"
            expected_improved = (
                row.get("valid") == "yes" and metrics["improved"]
            )
            if recorded_improved != expected_improved:
                errors.append(f"{label} new-best flag is incorrect")

        best = winner(rows)
        if best is None:
            errors.append(f"{case} has no valid energy result")
        else:
            winning_source = (
                directory
                / "sources"
                / f"round_{int(best['round']):03d}_optimizer.py"
            )
            proposal = directory / "optimizer.py"
            if (
                winning_source.exists()
                and proposal.exists()
                and proposal.read_text() != winning_source.read_text()
            ):
                errors.append(
                    f"{case} optimizer.py is not restored to winning source"
                )
        for name in ("insights.md", "figure_summary.txt", "summary.md"):
            if not (directory / name).exists():
                errors.append(f"{case} is missing {name}")
        figure_summary = directory / "figure_summary.txt"
        if figure_summary.exists() and _sentence_count(
            figure_summary.read_text()
        ) not in (2, 3):
            errors.append(
                f"{case} figure_summary.txt must contain 2 or 3 sentences"
            )

    for name in ROOT_OUTPUTS:
        if not (ROOT / name).exists():
            errors.append(f"completed study is missing {name}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ready", action="store_true")
    mode.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    errors = validate_ready() if args.ready else validate_complete()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    label = "ready to run" if args.ready else "complete"
    print(f"Study validation passed: {label}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

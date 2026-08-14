"""Run one guarded, observe-budgeted optimizer-autoresearch round."""

import argparse
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from evaluate import CASES, load_optimizer
from integrity import validate_fixed_files
from summarize_results import winner


ROOT = Path(__file__).resolve().parent
INITIAL_OPTIMIZER = ROOT / "initial_optimizer.py"
REFERENCE = json.loads((ROOT / "reference.json").read_text())
MAX_ROUNDS = 20
# The evaluator enforces the scientific 300-observe budget internally. The
# time limit and this larger subprocess timeout remain secondary safety guards.
EVALUATION_TIMEOUT_SECONDS = 135
PENDING_REASONING = "pending — the researcher has not selected the next round"
FIELDNAMES = [
    "round",
    "timestamp",
    "optimizer_label",
    "optimizer_source_sha256",
    "status",
    "valid",
    "converged",
    "time_cap_reached",
    "time_budget_s",
    "evaluator_elapsed_s",
    "wall_s",
    "calls_used",
    "calls_to_convergence",
    "max_calls",
    "optimizer_calls",
    "initial_energy",
    "best_energy",
    "best_energy_so_far",
    "improved_best_so_far",
    "accepted_iterations",
    "convergence_streak",
    "last_delta_energy",
    "energy_delta_tolerance",
    "energy_delta_patience",
    "minimum_accepted_iterations",
    "best_exact_error",
    "reasoning_for_change",
    "hypothesis",
    "observation",
    "next_round_reasoning",
]


def paths_for(case):
    directory = ROOT / "research" / case
    return {
        "directory": directory,
        "optimizer": directory / "optimizer.py",
        "ledger": directory / "results.tsv",
        "traces": directory / "traces",
        "sources": directory / "sources",
        "logs": directory / "logs",
    }


def clean_text(value):
    return " ".join(str(value).replace("\t", " ").split())


def read_ledger(path):
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_ledger(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDNAMES,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def append_row(path, row):
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDNAMES,
            delimiter="\t",
            lineterminator="\n",
        )
        if needs_header:
            writer.writeheader()
        writer.writerow(row)


def valid_energy_rows(rows):
    return [
        row
        for row in rows
        if row.get("valid") == "yes" and row.get("best_energy")
    ]


def prefix_metrics(rows, result=None):
    candidates = list(valid_energy_rows(rows))
    if (
        result is not None
        and result.get("valid")
        and result.get("best_energy") is not None
    ):
        candidates.append(
            {
                "round": str(len(rows) + 1),
                "valid": "yes",
                "best_energy": str(result["best_energy"]),
                "converged": (
                    "yes" if result.get("converged") else "no"
                ),
                "status": result.get("status", ""),
                "calls_used": result.get("calls_used"),
                "max_calls": result.get("max_calls"),
                "evaluator_elapsed_s": result.get("elapsed_s"),
            }
        )
    if not candidates:
        return {
            "best_energy": None,
            "improved": False,
            "winner_round": None,
        }
    selected = winner(candidates)
    lowest_energy = min(float(row["best_energy"]) for row in candidates)
    current_round = len(rows) + (1 if result is not None else 0)
    return {
        "best_energy": lowest_energy,
        "improved": int(selected["round"]) == current_round,
        "winner_round": int(selected["round"]),
    }


def _observation(result, metrics):
    status = result["status"]
    energy = result.get("best_energy")
    calls = result.get("calls_used")
    elapsed = result.get("elapsed_s")
    if not result.get("valid") or energy is None:
        return clean_text(
            f"Evaluation failed with status {status} after {elapsed or 0:.3f} "
            f"seconds and {calls or 0} calls; no valid energy was recorded."
        )
    improvement = (
        "the new study leader under the energy and tie-break rules"
        if metrics["improved"]
        else "not the study leader"
    )
    if result.get("converged"):
        ending = (
            f"Accepted-energy convergence occurred at call "
            f"{result['calls_to_convergence']}."
        )
    elif result.get("time_cap_reached"):
        ending = (
            "The secondary time guard was reached without convergence; this "
            "is a normal scored outcome, not an evaluator failure."
        )
    elif status == "call_cap":
        ending = (
            "The 300-observe budget was exhausted before convergence; the "
            "best completed observation was preserved and scored."
        )
    else:
        ending = (
            f"The optimizer ended with status {status} before convergence; "
            "its lowest observed energy remains a valid scored outcome."
        )
    return clean_text(
        f"Lowest observed energy {energy:.12g} after {elapsed:.3f} seconds "
        f"and {calls} counted calls was {improvement}. {ending}"
    )


def _synthetic_result(case, loaded, status, message):
    return {
        "case": case,
        "optimizer_label": loaded.label,
        "optimizer_source_sha256": loaded.source_sha256,
        "rationale": loaded.rationale,
        "hypothesis": loaded.hypothesis,
        "status": status,
        "valid": False,
        "converged": False,
        "time_cap_reached": False,
        "time_budget_seconds": REFERENCE["cases"][case][
            "time_budget_seconds"
        ],
        "elapsed_s": None,
        "calls_used": None,
        "calls_to_convergence": None,
        "optimizer_calls": None,
        "max_calls": REFERENCE["cases"][case]["max_calls"],
        "initial_energy": None,
        "best_energy": None,
        "best_exact_error": None,
        "convergence": None,
        "optimizer_error": message,
        "trace": [],
    }


def _parse_result(stdout):
    for line in reversed(stdout.splitlines()):
        if line.startswith("RESULT_JSON:"):
            return json.loads(line.removeprefix("RESULT_JSON:"))
    raise RuntimeError("evaluation output did not contain RESULT_JSON")


def _round_lock_path(case):
    digest = hashlib.sha256(str(ROOT).encode()).hexdigest()[:16]
    return Path("/tmp") / f"cudaq_optimizer_autoresearch_{digest}_{case}.lock"


def _number(value):
    return "" if value is None else value


def _float_text(value):
    return "" if value is None else f"{float(value):.17g}"


def run_round(case):
    if case not in CASES:
        raise KeyError(f"unknown case: {case}")
    integrity_errors = validate_fixed_files()
    if integrity_errors:
        raise RuntimeError(
            "fixed study files changed:\n- "
            + "\n- ".join(integrity_errors)
        )

    paths = paths_for(case)
    paths["directory"].mkdir(parents=True, exist_ok=True)
    with _round_lock_path(case).open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rows = read_ledger(paths["ledger"])
        round_number = len(rows) + 1
        if round_number > MAX_ROUNDS:
            raise RuntimeError(
                f"{case} already has the maximum {MAX_ROUNDS} rounds"
            )

        source = paths["optimizer"].read_text()
        if round_number == 1 and source != INITIAL_OPTIMIZER.read_text():
            raise RuntimeError(
                "round 1 optimizer must exactly match initial_optimizer.py"
            )
        loaded = load_optimizer(paths["optimizer"])

        for name in ("traces", "sources", "logs"):
            paths[name].mkdir(parents=True, exist_ok=True)
        stem = f"round_{round_number:03d}"
        source_path = paths["sources"] / f"{stem}_optimizer.py"
        source_path.write_text(source)

        command = [
            sys.executable,
            str(ROOT / "evaluate.py"),
            case,
            "--optimizer",
            str(paths["optimizer"]),
        ]
        environment = os.environ.copy()
        environment.setdefault(
            "MPLCONFIGDIR",
            "/tmp/cudaq_optimizer_autoresearch_matplotlib",
        )
        started = time.perf_counter()
        stdout = ""
        stderr = ""
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                timeout=EVALUATION_TIMEOUT_SECONDS,
                check=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            if completed.returncode:
                result = _synthetic_result(
                    case,
                    loaded,
                    "evaluator_error",
                    f"evaluate.py exited with {completed.returncode}",
                )
            else:
                result = _parse_result(stdout)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            result = _synthetic_result(
                case,
                loaded,
                "evaluator_timeout",
                f"evaluator exceeded {EVALUATION_TIMEOUT_SECONDS} seconds "
                "without serializing a result",
            )
        except Exception as error:
            result = _synthetic_result(
                case,
                loaded,
                "evaluator_error",
                f"{type(error).__name__}: {error}",
            )
        wall_s = time.perf_counter() - started

        result["round"] = round_number
        result["wall_s"] = wall_s
        trace_path = paths["traces"] / f"{stem}.json"
        trace_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
        log_path = paths["logs"] / f"{stem}.log"
        log_path.write_text(
            stdout
            + ("\nSTDERR:\n" + stderr if stderr else "")
            + (
                "\nHARNESS_ERROR:\n" + result["optimizer_error"]
                if result.get("optimizer_error")
                else ""
            )
        )

        if rows:
            rows[-1]["next_round_reasoning"] = clean_text(loaded.rationale)
            write_ledger(paths["ledger"], rows)

        metrics = prefix_metrics(rows, result)
        convergence = result.get("convergence") or {}
        row = {
            "round": round_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "optimizer_label": clean_text(result["optimizer_label"]),
            "optimizer_source_sha256": result["optimizer_source_sha256"],
            "status": result["status"],
            "valid": "yes" if result.get("valid") else "no",
            "converged": "yes" if result.get("converged") else "no",
            "time_cap_reached": (
                "yes" if result.get("time_cap_reached") else "no"
            ),
            "time_budget_s": _float_text(
                result.get("time_budget_seconds")
            ),
            "evaluator_elapsed_s": _float_text(result.get("elapsed_s")),
            "wall_s": f"{wall_s:.6f}",
            "calls_used": _number(result.get("calls_used")),
            "calls_to_convergence": _number(
                result.get("calls_to_convergence")
            ),
            "max_calls": _number(result.get("max_calls")),
            "optimizer_calls": _number(result.get("optimizer_calls")),
            "initial_energy": _float_text(result.get("initial_energy")),
            "best_energy": _float_text(result.get("best_energy")),
            "best_energy_so_far": _float_text(metrics["best_energy"]),
            "improved_best_so_far": (
                "yes"
                if result.get("valid") and metrics["improved"]
                else "no"
            ),
            "accepted_iterations": _number(
                convergence.get("accepted_iterations")
            ),
            "convergence_streak": _number(
                convergence.get("convergence_streak")
            ),
            "last_delta_energy": _float_text(
                convergence.get("last_delta_energy")
            ),
            "energy_delta_tolerance": _float_text(
                convergence.get("energy_delta_tolerance")
            ),
            "energy_delta_patience": _number(
                convergence.get("patience")
            ),
            "minimum_accepted_iterations": _number(
                convergence.get("minimum_accepted_iterations")
            ),
            "best_exact_error": _float_text(
                result.get("best_exact_error")
            ),
            "reasoning_for_change": clean_text(result["rationale"]),
            "hypothesis": clean_text(result["hypothesis"]),
            "observation": _observation(result, metrics),
            "next_round_reasoning": PENDING_REASONING,
        }
        append_row(paths["ledger"], row)
        convergence_label = (
            "converged" if result.get("converged") else "not converged"
        )
        energy_label = (
            f"{float(result['best_energy']):.12g}"
            if result.get("best_energy") is not None
            else "unavailable"
        )
        print(
            f"recorded {case} round {round_number}: {result['status']}, "
            f"{convergence_label}, best_energy={energy_label}"
        )
        return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    run_round(args.case)


if __name__ == "__main__":
    main()

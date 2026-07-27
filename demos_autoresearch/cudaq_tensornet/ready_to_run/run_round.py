"""Run one guarded round for one independent circuit researcher."""

import argparse
import csv
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

from evaluate import CIRCUITS, load_experiment


ROOT = Path(__file__).resolve().parent
INITIAL_EXPERIMENT = ROOT / "initial_experiment.py"
SETTING_NAMES = (
    "precision",
    "controlled_rank",
    "path_reuse",
    "hyper_samples",
    "find_threads",
    "find_limit",
    "deterministic",
    "scratch_percentage",
)
FIELDNAMES = [
    "round",
    "timestamp",
    *SETTING_NAMES,
    "runtime_s",
    "best_so_far_s",
    "wall_s",
    "expectation",
    "absolute_error",
    "valid",
    "status",
    "change",
    "reasoning_for_change",
    "hypothesis",
    "observation",
    "next_round_reasoning",
]
PENDING_REASONING = "pending — the researcher has not selected the next round"


def paths_for(circuit):
    directory = ROOT / "research" / circuit
    return {
        "directory": directory,
        "experiment": directory / "experiment.py",
        "ledger": directory / "results.tsv",
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
            handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def append_row(path, row):
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n"
        )
        if needs_header:
            writer.writeheader()
        writer.writerow(row)


def completed_rows(rows):
    return [
        row
        for row in rows
        if row["valid"] == "yes"
        and row["runtime_s"]
        and row["status"] not in {"crash", "timeout"}
    ]


def best_row(rows):
    complete = completed_rows(rows)
    return min(complete, key=lambda row: float(row["runtime_s"])) if complete else None


def backfill_next_reasoning(path, rows, rationale):
    if rows and rows[-1]["next_round_reasoning"] == PENDING_REASONING:
        rows[-1]["next_round_reasoning"] = clean_text(rationale)
        write_ledger(path, rows)


def describe_change(settings, base):
    if base is None:
        return "baseline"
    changes = []
    for name in SETTING_NAMES:
        old = base[name]
        new = str(settings[name])
        if old != new:
            changes.append(f"{name}: {old} -> {new}")
    return "; ".join(changes) if changes else "repeat best settings"


def validate_initial_settings(settings, rows):
    if rows:
        return
    initial_settings, _, _ = load_experiment(INITIAL_EXPERIMENT)
    if settings != initial_settings:
        raise ValueError(
            "round 1 must use the exact SETTINGS from initial_experiment.py; "
            "copy that template into this researcher's experiment.py before "
            "starting"
        )


def extract_result(stdout):
    for line in stdout.splitlines():
        if line.startswith("RESULT_JSON:"):
            return json.loads(line.removeprefix("RESULT_JSON:"))
    raise RuntimeError("evaluate.py did not emit RESULT_JSON")


def timeout_output(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def refresh_reports():
    try:
        from plot_results import plot_results

        plot_results()
    except Exception as error:
        print(f"warning: could not refresh results.png: {error}")
    try:
        from summarize_results import write_summaries

        write_summaries()
    except Exception as error:
        print(f"warning: could not refresh summaries: {error}")


def run_locked(circuit, timeout):
    paths = paths_for(circuit)
    settings, rationale, hypothesis = load_experiment(paths["experiment"])
    rows = read_ledger(paths["ledger"])
    validate_initial_settings(settings, rows)
    backfill_next_reasoning(paths["ledger"], rows, rationale)
    rows = read_ledger(paths["ledger"])
    base = best_row(rows)
    change = describe_change(settings, base)
    round_number = len(rows) + 1

    paths["logs"].mkdir(exist_ok=True)
    log_path = paths["logs"] / f"round_{round_number:03d}.log"
    command = [
        sys.executable,
        str(ROOT / "evaluate.py"),
        circuit,
        "--experiment",
        str(paths["experiment"]),
    ]
    started = time.perf_counter()
    result = None
    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        wall_seconds = time.perf_counter() - started
        stdout, stderr = completed.stdout, completed.stderr
        if completed.returncode != 0:
            status = "crash"
            observation = (
                f"Evaluator exited with code {completed.returncode}; inspect "
                f"{log_path.name}."
            )
        else:
            result = extract_result(stdout)
            if not result["valid"]:
                status = "discard"
                observation = (
                    "Correctness check failed: absolute error "
                    f"{result['absolute_error']:.3g}."
                )
            elif base is None:
                status = "keep"
                observation = (
                    f"Established a {result['runtime_seconds']:.3f}s baseline."
                )
            else:
                old = float(base["runtime_s"])
                new = result["runtime_seconds"]
                if new < old:
                    status = "keep"
                    observation = (
                        f"Runtime improved {old / new:.2f}x, from "
                        f"{old:.3f}s to {new:.3f}s."
                    )
                else:
                    status = "discard"
                    observation = (
                        f"Runtime regressed {new / old:.2f}x, from "
                        f"{old:.3f}s to {new:.3f}s."
                    )
    except subprocess.TimeoutExpired as error:
        wall_seconds = time.perf_counter() - started
        stdout = timeout_output(error.stdout)
        stderr = timeout_output(error.stderr)
        status = "timeout"
        observation = (
            f"Evaluation exceeded {timeout:.1f}s and was discarded as an outlier."
        )
    except Exception as error:
        wall_seconds = time.perf_counter() - started
        status = "crash"
        stderr = f"{type(error).__name__}: {error}\n"
        observation = f"Could not parse output; inspect {log_path.name}."

    log_path.write_text(
        f"$ {' '.join(command)}\n\n[stdout]\n{stdout}"
        f"\n[stderr]\n{stderr}"
    )

    prior_best = float(base["runtime_s"]) if base else None
    if result is None:
        runtime = ""
        expectation = ""
        absolute_error = ""
        valid = False
        best_so_far = prior_best if prior_best is not None else ""
    else:
        runtime = result["runtime_seconds"]
        expectation = result["expectation"]
        absolute_error = result["absolute_error"]
        valid = result["valid"]
        candidates = [value for value in (prior_best, runtime) if value is not None]
        best_so_far = min(candidates) if valid else prior_best

    row = {
        "round": round_number,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **settings,
        "runtime_s": f"{runtime:.6f}" if runtime != "" else "",
        "best_so_far_s": (
            f"{best_so_far:.6f}" if best_so_far not in {"", None} else ""
        ),
        "wall_s": f"{wall_seconds:.6f}",
        "expectation": f"{expectation:.12g}" if expectation != "" else "",
        "absolute_error": (
            f"{absolute_error:.6g}" if absolute_error != "" else ""
        ),
        "valid": "yes" if valid else "no",
        "status": status,
        "change": clean_text(change),
        "reasoning_for_change": clean_text(rationale),
        "hypothesis": clean_text(hypothesis),
        "observation": clean_text(observation),
        "next_round_reasoning": PENDING_REASONING,
    }
    append_row(paths["ledger"], row)
    refresh_reports()

    print(f"researcher:  {circuit}")
    print(f"round:       {round_number}")
    print(f"status:      {status}")
    print(f"change:      {change}")
    print(f"runtime:     {runtime:.6f}s" if runtime != "" else "runtime:     n/a")
    print(
        f"best:        {best_so_far:.6f}s"
        if best_so_far not in {"", None}
        else "best:        n/a"
    )
    print(f"wall:        {wall_seconds:.6f}s")
    print(f"observation: {observation}")
    print(f"ledger:      {paths['ledger'].relative_to(ROOT)}")
    return 0 if status in {"keep", "discard"} else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("circuit", choices=CIRCUITS)
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="hard wall-clock limit for this circuit evaluation",
    )
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    lock_path = ROOT / ".gpu.lock"
    with lock_path.open("w") as lock:
        print(f"{args.circuit}: waiting for the shared GPU", flush=True)
        fcntl.flock(lock, fcntl.LOCK_EX)
        print(f"{args.circuit}: acquired the shared GPU", flush=True)
        return run_locked(args.circuit, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())

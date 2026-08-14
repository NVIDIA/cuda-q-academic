"""Evaluate optimizer code through a counted energy and convergence oracle."""

import argparse
import ast
from dataclasses import dataclass
import hashlib
import importlib.util
import inspect
import json
import math
from pathlib import Path
import random
import signal
import time
import traceback

import numpy as np


ROOT = Path(__file__).resolve().parent
REFERENCE_PATH = ROOT / "reference.json"
CASES = ("qaoa_depth15",)

ALLOWED_IMPORT_ROOTS = {
    "collections",
    "functools",
    "itertools",
    "math",
    "numpy",
    "random",
    "scipy",
    "statistics",
}
FORBIDDEN_CALL_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}
FORBIDDEN_ATTRIBUTES = {
    "__class__",
    "__dict__",
    "__globals__",
    "__subclasses__",
    "dump",
    "dumps",
    "fromfile",
    "load",
    "loads",
    "save",
    "savez",
    "savez_compressed",
    "tofile",
}
REQUIRED_OPTIMIZER_PARAMETERS = (
    "objective",
    "initial_parameters",
    "initial_energy",
    "max_calls",
    "seed",
    "accepted",
)


class CallBudgetExceeded(BaseException):
    """Stop the round immediately when the counted-call budget is complete."""


class ProtocolViolation(ValueError):
    """Raised when optimizer code violates the energy-oracle contract."""


class EnergyConverged(BaseException):
    """Stop optimizer execution when accepted energies have converged."""


class TimeBudgetExpired(BaseException):
    """Stop optimizer execution while preserving all completed observations."""


@dataclass(frozen=True)
class LoadedOptimizer:
    label: str
    rationale: str
    hypothesis: str
    optimize: object
    source_sha256: str


def optimizer_path(case):
    return ROOT / "research" / case / "optimizer.py"


def audit_optimizer_source(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in ALLOWED_IMPORT_ROOTS:
                    raise ValueError(
                        f"optimizer import is not allowed: {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise ValueError("relative imports are not allowed")
            root = (node.module or "").split(".", 1)[0]
            if root not in ALLOWED_IMPORT_ROOTS:
                raise ValueError(
                    f"optimizer import is not allowed: {node.module}"
                )
        elif isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id in FORBIDDEN_CALL_NAMES
            ):
                raise ValueError(
                    f"optimizer call is not allowed: {node.func.id}"
                )
        elif isinstance(node, ast.Attribute):
            if (
                node.attr.startswith("__")
                or node.attr in FORBIDDEN_ATTRIBUTES
            ):
                raise ValueError(
                    f"optimizer attribute is not allowed: {node.attr}"
                )
    return tree


def _clean_explanation(value, name):
    if not isinstance(value, str) or len(" ".join(value.split())) < 40:
        raise ValueError(f"{name} must be a concrete explanatory sentence")
    return " ".join(value.split())


def load_optimizer(path):
    path = Path(path)
    source = path.read_text()
    audit_optimizer_source(source)
    digest = hashlib.sha256(source.encode()).hexdigest()
    module_name = f"_autoresearch_optimizer_{digest[:16]}"
    specification = importlib.util.spec_from_file_location(module_name, path)
    if specification is None or specification.loader is None:
        raise ValueError(f"cannot load optimizer from {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    label = getattr(module, "OPTIMIZER_LABEL", None)
    if not isinstance(label, str) or not label.strip():
        raise ValueError("OPTIMIZER_LABEL must be a non-empty string")
    rationale = _clean_explanation(
        getattr(module, "RATIONALE", None),
        "RATIONALE",
    )
    hypothesis = _clean_explanation(
        getattr(module, "HYPOTHESIS", None),
        "HYPOTHESIS",
    )
    optimize = getattr(module, "optimize", None)
    if not callable(optimize):
        raise ValueError("optimizer.py must define callable optimize")
    signature = inspect.signature(optimize)
    if tuple(signature.parameters) != REQUIRED_OPTIMIZER_PARAMETERS:
        raise ValueError(
            "optimize parameters must be exactly: "
            + ", ".join(REQUIRED_OPTIMIZER_PARAMETERS)
        )
    return LoadedOptimizer(
        label=" ".join(label.split()),
        rationale=rationale,
        hypothesis=hypothesis,
        optimize=optimize,
        source_sha256=digest,
    )


class CountedEnergyOracle:
    """A one-vector-at-a-time energy oracle with a hard call budget."""

    def __init__(
        self,
        raw_energy,
        max_calls,
        parameter_count=None,
        exact_energy=None,
        started_at=None,
        time_budget_seconds=None,
    ):
        self.raw_energy = raw_energy
        self.max_calls = int(max_calls)
        self.parameter_count = parameter_count
        self.exact_energy = (
            float(exact_energy) if exact_energy is not None else None
        )
        self.phase = "optimization"
        self.trace = []
        self.best_energy = math.inf
        self.best_parameters = None
        self.started_at = (
            float(started_at)
            if started_at is not None
            else time.perf_counter()
        )
        self.time_budget_seconds = (
            float(time_budget_seconds)
            if time_budget_seconds is not None
            else None
        )

    @property
    def calls_used(self):
        return len(self.trace)

    @property
    def best_exact_error(self):
        if self.exact_energy is None or not math.isfinite(self.best_energy):
            return None
        return abs(self.best_energy - self.exact_energy)

    def __call__(self, parameters):
        elapsed_before = time.perf_counter() - self.started_at
        if (
            self.time_budget_seconds is not None
            and elapsed_before >= self.time_budget_seconds
        ):
            raise TimeBudgetExpired
        if self.calls_used >= self.max_calls:
            raise CallBudgetExceeded(
                f"fixed budget of {self.max_calls} circuit calls exhausted"
            )
        vector = np.asarray(parameters, dtype=float)
        if vector.ndim != 1:
            raise ProtocolViolation("objective expects one 1D parameter vector")
        if (
            self.parameter_count is not None
            and vector.shape != (self.parameter_count,)
        ):
            raise ProtocolViolation(
                f"objective expects {self.parameter_count} parameters, "
                f"got shape {vector.shape}"
            )
        if not np.all(np.isfinite(vector)):
            raise ProtocolViolation("objective parameters must all be finite")

        previous_mask = None
        if (
            self.time_budget_seconds is not None
            and hasattr(signal, "pthread_sigmask")
        ):
            previous_mask = signal.pthread_sigmask(
                signal.SIG_BLOCK,
                {signal.SIGALRM},
            )
        try:
            energy = float(self.raw_energy(vector.copy()))
            if not math.isfinite(energy):
                raise ProtocolViolation("circuit energy must be finite")
            if energy < self.best_energy:
                self.best_energy = energy
                self.best_parameters = vector.copy()
            call = self.calls_used + 1
            elapsed = time.perf_counter() - self.started_at
            entry = {
                "call": call,
                "phase": self.phase,
                "elapsed_s": elapsed,
                "energy": energy,
                "best_energy": self.best_energy,
                "parameters": vector.tolist(),
            }
            if self.exact_energy is not None:
                entry["absolute_error"] = abs(energy - self.exact_energy)
                entry["best_exact_error"] = self.best_exact_error
            self.trace.append(entry)
        finally:
            if previous_mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        if (
            self.time_budget_seconds is not None
            and elapsed >= self.time_budget_seconds
        ):
            raise TimeBudgetExpired
        if self.calls_used >= self.max_calls:
            raise CallBudgetExceeded(
                f"fixed budget of {self.max_calls} circuit calls completed"
            )
        return energy


def opaque_objective(oracle, call_limit=None):
    """Expose only a counted one-vector energy callable."""

    limit = int(call_limit) if call_limit is not None else None

    def objective(parameters):
        if limit is not None and oracle.calls_used >= limit:
            raise CallBudgetExceeded(
                f"optimizer allowance of {limit} total calls exhausted"
            )
        return oracle(parameters)

    return objective


class AcceptedEnergyTracker:
    """Track counted accepted iterates and enforce delta-energy convergence."""

    def __init__(
        self,
        oracle,
        initial_parameters,
        initial_energy,
        energy_delta_tolerance,
        patience,
        minimum_iterations,
    ):
        self.oracle = oracle
        self.energy_delta_tolerance = float(energy_delta_tolerance)
        self.patience = int(patience)
        self.minimum_iterations = int(minimum_iterations)
        initial = np.asarray(initial_parameters, dtype=float).copy()
        self.records = [
            {
                "iteration": 0,
                "call": 1,
                "observation_call": 1,
                "energy": float(initial_energy),
                "delta_energy": None,
                "convergence_streak": 0,
                "parameters": initial.tolist(),
            }
        ]
        self.best_energy = float(initial_energy)
        self.best_parameters = initial
        self.converged = False
        self.calls_to_convergence = None

    @property
    def accepted_iterations(self):
        return len(self.records) - 1

    @property
    def last_delta_energy(self):
        if self.accepted_iterations == 0:
            return None
        return self.records[-1]["delta_energy"]

    @property
    def convergence_streak(self):
        return int(self.records[-1]["convergence_streak"])

    def _matching_observation(self, vector):
        previous_acceptance_call = int(self.records[-1]["call"])
        if self.oracle.calls_used <= previous_acceptance_call:
            raise ProtocolViolation(
                "accepted(parameters) requires at least one new counted "
                "objective evaluation since the preceding accepted iteration"
            )
        for entry in reversed(self.oracle.trace):
            observed = np.asarray(entry["parameters"], dtype=float)
            if np.array_equal(observed, vector):
                return entry
        raise ProtocolViolation(
            "accepted parameters must match a previously counted objective "
            "evaluation exactly"
        )

    def report(self, parameters):
        previous_mask = None
        if hasattr(signal, "pthread_sigmask"):
            previous_mask = signal.pthread_sigmask(
                signal.SIG_BLOCK,
                {signal.SIGALRM},
            )
        try:
            return self._report_consistently(parameters)
        finally:
            if previous_mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    def _report_consistently(self, parameters):
        vector = np.asarray(parameters, dtype=float)
        if vector.ndim != 1:
            raise ProtocolViolation(
                "accepted parameters must be one-dimensional"
            )
        if (
            self.oracle.parameter_count is not None
            and vector.shape != (self.oracle.parameter_count,)
        ):
            raise ProtocolViolation(
                f"accepted parameters must have shape "
                f"({self.oracle.parameter_count},)"
            )
        if not np.all(np.isfinite(vector)):
            raise ProtocolViolation("accepted parameters must all be finite")

        observation = self._matching_observation(vector)
        energy = float(observation["energy"])
        previous_energy = float(self.records[-1]["energy"])
        delta_energy = abs(energy - previous_energy)
        streak = (
            self.convergence_streak + 1
            if delta_energy <= self.energy_delta_tolerance + 1e-15
            else 0
        )
        record = {
            "iteration": self.accepted_iterations + 1,
            "call": self.oracle.calls_used,
            "observation_call": int(observation["call"]),
            "energy": energy,
            "delta_energy": delta_energy,
            "convergence_streak": streak,
            "parameters": vector.tolist(),
        }
        self.records.append(record)
        if energy < self.best_energy:
            self.best_energy = energy
            self.best_parameters = vector.copy()

        if (
            self.accepted_iterations >= self.minimum_iterations
            and streak >= self.patience
        ):
            self.converged = True
            self.calls_to_convergence = self.oracle.calls_used
            raise EnergyConverged
        return False


def opaque_accepted_callback(tracker):
    """Expose only the accepted-iterate reporting callable."""

    def accepted(parameters):
        return tracker.report(parameters)

    return accepted


def _validate_reference(case, reference):
    from benchmark import (
        benchmark_signature,
        initial_parameters_sha256,
    )

    if reference["benchmark_sha256"] != benchmark_signature():
        raise RuntimeError(
            "benchmark.py does not match reference.json; restore fixed files"
        )
    expected_hash = reference["cases"][case]["initial_parameters_sha256"]
    if expected_hash != initial_parameters_sha256(case):
        raise RuntimeError(
            f"{case} initial parameters do not match reference.json"
        )


def run_evaluation(case, path):
    if case not in CASES:
        raise KeyError(f"unknown case: {case}")
    loaded = load_optimizer(path)
    reference = json.loads(REFERENCE_PATH.read_text())
    _validate_reference(case, reference)
    entry = reference["cases"][case]

    import cudaq

    target_option = reference.get("target_option")
    if target_option:
        cudaq.set_target(reference["target"], option=target_option)
    else:
        cudaq.set_target(reference["target"])
    cudaq.set_random_seed(int(entry["optimizer_seed"]))
    np.random.seed(int(entry["optimizer_seed"]))
    random.seed(int(entry["optimizer_seed"]))

    from benchmark import case_specification, energy, initial_parameters

    initial = initial_parameters(case)
    parameter_count = int(case_specification(case)["parameter_count"])
    optimizer_call_budget = int(entry["max_calls"])
    time_budget_seconds = float(entry["time_budget_seconds"])
    if optimizer_call_budget <= 1:
        raise RuntimeError("max_calls leaves no usable optimizer allowance")
    if time_budget_seconds <= 0.0:
        raise RuntimeError("time_budget_seconds must be positive")

    started_at = time.perf_counter()
    oracle = CountedEnergyOracle(
        raw_energy=lambda vector: energy(case, vector),
        max_calls=entry["max_calls"],
        parameter_count=parameter_count,
        exact_energy=entry.get("exact_energy"),
        started_at=started_at,
        time_budget_seconds=time_budget_seconds,
    )

    status = "not_converged"
    optimizer_error = ""
    returned_parameters = None
    initial_energy = None
    optimization_calls = None
    tracker = None
    previous_alarm_handler = signal.getsignal(signal.SIGALRM)

    def expire_time_budget(signum, frame):
        del signum, frame
        raise TimeBudgetExpired

    signal.signal(signal.SIGALRM, expire_time_budget)
    signal.setitimer(signal.ITIMER_REAL, time_budget_seconds)
    try:
        oracle.phase = "initial"
        initial_energy = oracle(initial)
        oracle.phase = "optimization"
        tracker = AcceptedEnergyTracker(
            oracle,
            initial,
            initial_energy,
            entry["energy_delta_tolerance"],
            entry["energy_delta_patience"],
            entry["minimum_accepted_iterations"],
        )
        returned = loaded.optimize(
            opaque_objective(oracle),
            initial.copy(),
            initial_energy,
            optimizer_call_budget,
            int(entry["optimizer_seed"]),
            opaque_accepted_callback(tracker),
        )
        optimization_calls = oracle.calls_used
        if returned is None:
            status = "invalid_return"
            optimizer_error = "optimizer returned None"
        else:
            returned_vector = np.asarray(returned, dtype=float)
            returned_parameters = returned_vector.tolist()
            status = "not_converged"
    except EnergyConverged:
        status = "converged"
        optimization_calls = oracle.calls_used
        returned_parameters = (
            oracle.best_parameters.tolist()
            if oracle.best_parameters is not None
            else None
        )
    except TimeBudgetExpired:
        status = (
            "converged"
            if tracker is not None and tracker.converged
            else "time_cap"
        )
        optimization_calls = oracle.calls_used
        returned_parameters = (
            oracle.best_parameters.tolist()
            if oracle.best_parameters is not None
            else None
        )
    except CallBudgetExceeded as error:
        status = "call_cap"
        optimizer_error = str(error)
        optimization_calls = oracle.calls_used
        returned_parameters = (
            oracle.best_parameters.tolist()
            if oracle.best_parameters is not None
            else None
        )
    except Exception as error:
        status = "error"
        optimizer_error = "".join(
            traceback.format_exception_only(type(error), error)
        ).strip()
        optimization_calls = oracle.calls_used
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_alarm_handler)

    elapsed_s = time.perf_counter() - started_at
    valid_statuses = {"converged", "time_cap", "not_converged", "call_cap"}
    valid = bool(
        status in valid_statuses
        and oracle.best_parameters is not None
        and math.isfinite(oracle.best_energy)
    )
    candidate_energy = oracle.best_energy if valid else None
    if valid:
        returned_parameters = oracle.best_parameters.tolist()
    convergence = (
        {
            "reached": tracker.converged,
            "energy_delta_tolerance": tracker.energy_delta_tolerance,
            "patience": tracker.patience,
            "minimum_accepted_iterations": tracker.minimum_iterations,
            "accepted_iterations": tracker.accepted_iterations,
            "convergence_streak": tracker.convergence_streak,
            "last_delta_energy": tracker.last_delta_energy,
            "records": tracker.records,
        }
        if tracker is not None
        else None
    )
    result = {
        "case": case,
        "optimizer_label": loaded.label,
        "optimizer_source_sha256": loaded.source_sha256,
        "rationale": loaded.rationale,
        "hypothesis": loaded.hypothesis,
        "status": status,
        "valid": valid,
        "converged": bool(tracker and tracker.converged),
        "time_cap_reached": status == "time_cap",
        "time_budget_seconds": time_budget_seconds,
        "elapsed_s": elapsed_s,
        "calls_used": oracle.calls_used,
        "calls_to_convergence": (
            tracker.calls_to_convergence
            if tracker is not None and tracker.converged
            else None
        ),
        "optimizer_calls": optimization_calls,
        "optimizer_call_budget": optimizer_call_budget,
        "max_calls": oracle.max_calls,
        "initial_energy": initial_energy,
        "candidate_energy": candidate_energy,
        "best_energy": (
            oracle.best_energy if math.isfinite(oracle.best_energy) else None
        ),
        "best_exact_error": oracle.best_exact_error,
        "convergence": convergence,
        "exact_energy": entry.get("exact_energy"),
        "returned_parameters": returned_parameters,
        "optimizer_error": optimizer_error,
        "trace": oracle.trace,
    }
    convergence_text = (
        str(result["calls_to_convergence"])
        if result["calls_to_convergence"] is not None
        else "not converged"
    )
    candidate_text = (
        f"{candidate_energy:.12g}"
        if candidate_energy is not None
        else "unavailable"
    )
    print(
        f"{case}: {status}, elapsed={elapsed_s:.3f}s, "
        f"calls={oracle.calls_used}, "
        f"calls_to_convergence={convergence_text}, "
        f"best_energy={candidate_text}",
        flush=True,
    )
    print("RESULT_JSON:" + json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES)
    parser.add_argument("--optimizer", type=Path)
    args = parser.parse_args()
    run_evaluation(
        args.case,
        args.optimizer or optimizer_path(args.case),
    )


if __name__ == "__main__":
    main()

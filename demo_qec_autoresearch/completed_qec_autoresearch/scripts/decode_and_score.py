from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np

from qldpc_data import dataset_name_from_path, load_release_dataset

FORBIDDEN_DECODERS = frozenset({"single_error_lut", "multi_error_lut"})
FORBIDDEN_BATCH_FEATURES = frozenset({"decode_batch", "bp_batch_size", "osd_batch_size"})
FORBIDDEN_BATCH_NAMES = {
    "decode_batch": "decode_batch",
    "bp_batch_size": "bp_batch_size",
    "osd_batch_size": "osd_batch_size",
    "BP_BATCH_SIZE": "bp_batch_size",
    "OSD_BATCH_SIZE": "osd_batch_size",
}
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Problem:
    H: np.ndarray
    syndromes: np.ndarray
    observable_matrix: np.ndarray
    priors: np.ndarray
    metadata: dict[str, Any]


def _load_metadata(value: np.ndarray) -> dict[str, Any]:
    return json.loads(str(value.tolist()))


def load_problem(dataset_path: str | Path) -> tuple[Problem, np.ndarray, str]:
    path = Path(dataset_path)
    if path.name.endswith(".json.bz2"):
        payload, hidden, dataset_name = load_release_dataset(path)
        problem = Problem(
            H=np.ascontiguousarray(payload["H"], dtype=np.uint8),
            syndromes=np.ascontiguousarray(payload["syndromes"], dtype=np.uint8),
            observable_matrix=np.ascontiguousarray(payload["observable_matrix"], dtype=np.uint8),
            priors=np.asarray(payload["priors"], dtype=np.float64),
            metadata=dict(payload["metadata"]),
        )
        return problem, np.ascontiguousarray(hidden, dtype=np.uint8), dataset_name
    data = np.load(path, allow_pickle=False)
    problem = Problem(
        H=np.ascontiguousarray(data["H"], dtype=np.uint8),
        syndromes=np.ascontiguousarray(data["syndromes"], dtype=np.uint8),
        observable_matrix=np.ascontiguousarray(data["observable_matrix"], dtype=np.uint8),
        priors=np.asarray(data["priors"], dtype=np.float64),
        metadata=_load_metadata(data["metadata_json"]),
    )
    hidden = np.ascontiguousarray(data["logical_observables"], dtype=np.uint8)
    return problem, hidden, dataset_name_from_path(path)


def decoder_hash(decoder_path: str | Path) -> str:
    return hashlib.sha256(Path(decoder_path).read_bytes()).hexdigest()[:16]


def import_decoder(decoder_path: str | Path) -> ModuleType:
    path = Path(decoder_path)
    module_name = f"autoresearch_decoder_{hashlib.sha1(str(path).encode()).hexdigest()}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import decoder from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "decode"):
        raise AttributeError(f"{path} must define decode(problem)")
    return module


def _forbidden_decoder_names(module: ModuleType) -> list[str]:
    names: set[str] = set()
    for value in vars(module).values():
        if isinstance(value, str) and value in FORBIDDEN_DECODERS:
            names.add(value)
        elif isinstance(value, (tuple, list, set, frozenset)):
            names.update(item for item in value if isinstance(item, str) and item in FORBIDDEN_DECODERS)
    return sorted(names)


def _forbidden_batch_features(decoder_path: str | Path) -> list[str]:
    source = Path(decoder_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(decoder_path))
    features: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_BATCH_FEATURES:
            features.add(node.attr)
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_BATCH_NAMES:
            features.add(FORBIDDEN_BATCH_NAMES[node.id])
        elif isinstance(node, ast.keyword) and node.arg in FORBIDDEN_BATCH_FEATURES:
            features.add(node.arg)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in FORBIDDEN_BATCH_FEATURES:
                features.add(node.value)
    return sorted(features)


def _validate_corrections(corrections: Any, problem: Problem) -> np.ndarray:
    array = np.asarray(corrections, dtype=np.uint8)
    expected_shape = (problem.syndromes.shape[0], problem.H.shape[1])
    if array.shape != expected_shape:
        raise ValueError(f"corrections shape {array.shape} != {expected_shape}")
    if not np.isin(array, [0, 1]).all():
        raise ValueError("corrections must be binary")
    return np.ascontiguousarray(array, dtype=np.uint8)


def _ler(corrections: np.ndarray, problem: Problem, hidden: np.ndarray) -> float:
    predicted = (corrections @ problem.observable_matrix % 2).astype(np.uint8)
    if predicted.shape != hidden.shape:
        raise ValueError(f"predicted observable shape {predicted.shape} != {hidden.shape}")
    logical_error_by_shot = np.any(predicted != hidden, axis=1)
    return float(np.mean(logical_error_by_shot))


def evaluate_dataset(
    *,
    dataset_path: str | Path,
    decoder_path: str | Path,
    lane: str,
    round_index: int,
    time_cap_seconds: float,
    objective: str = "ler",
    ler_cap: float = 1.0,
) -> dict[str, Any]:
    if objective not in {"ler", "decode_time"}:
        raise ValueError(f"unknown objective: {objective}")
    problem, hidden, dataset_name = load_problem(dataset_path)
    start = time.perf_counter()
    status = "pass"
    failure_reason = ""
    ler = 1.0
    used_cudaq_qec = False
    try:
        module = import_decoder(decoder_path)
        forbidden_decoders = _forbidden_decoder_names(module)
        if forbidden_decoders:
            status = "fail"
            failure_reason = f"forbidden_decoder: {','.join(forbidden_decoders)}"
            decode_seconds = time.perf_counter() - start
            return {
                "round": int(round_index),
                "lane": lane,
                "decoder_path": str(decoder_path),
                "decoder_hash": decoder_hash(decoder_path),
                "dataset": dataset_name,
                "status": status,
                "ler": float(ler),
                "decode_seconds": float(decode_seconds),
                "time_cap_seconds": float(time_cap_seconds),
                "score": float(_penalty_score(objective)),
                "failure_reason": failure_reason,
                "used_cudaq_qec": used_cudaq_qec,
                "objective": objective,
                "ler_cap": float(ler_cap),
                "notes": "",
            }
        forbidden_batch_features = _forbidden_batch_features(decoder_path)
        if forbidden_batch_features:
            status = "fail"
            failure_reason = f"forbidden_batch_mode: {','.join(forbidden_batch_features)}"
            decode_seconds = time.perf_counter() - start
            return {
                "round": int(round_index),
                "lane": lane,
                "decoder_path": str(decoder_path),
                "decoder_hash": decoder_hash(decoder_path),
                "dataset": dataset_name,
                "status": status,
                "ler": float(ler),
                "decode_seconds": float(decode_seconds),
                "time_cap_seconds": float(time_cap_seconds),
                "score": float(_penalty_score(objective)),
                "failure_reason": failure_reason,
                "used_cudaq_qec": used_cudaq_qec,
                "objective": objective,
                "ler_cap": float(ler_cap),
                "notes": "",
            }
        start = time.perf_counter()
        corrections = _validate_corrections(module.decode(problem), problem)
        decode_seconds = time.perf_counter() - start
        used_cudaq_qec = bool(getattr(module, "USED_CUDAQ_QEC", False))
        if decode_seconds > time_cap_seconds:
            status = "fail"
            failure_reason = "decode_timeout"
        elif not used_cudaq_qec:
            status = "fail"
            failure_reason = "cudaq_qec_not_used"
        else:
            ler = _ler(corrections, problem, hidden)
            if objective == "decode_time" and ler > ler_cap:
                status = "fail"
                failure_reason = "ler_cap_exceeded"
    except Exception as exc:
        decode_seconds = time.perf_counter() - start
        status = "fail"
        failure_reason = f"{type(exc).__name__}: {exc}"
    score = _score_record(
        objective=objective,
        status=status,
        ler=ler,
        decode_seconds=decode_seconds,
    )
    return {
        "round": int(round_index),
        "lane": lane,
        "decoder_path": str(decoder_path),
        "decoder_hash": decoder_hash(decoder_path),
        "dataset": dataset_name,
        "status": status,
        "ler": float(ler),
        "decode_seconds": float(decode_seconds),
        "time_cap_seconds": float(time_cap_seconds),
        "score": float(score),
        "failure_reason": failure_reason,
        "used_cudaq_qec": used_cudaq_qec,
        "objective": objective,
        "ler_cap": float(ler_cap),
        "notes": "",
    }


def _penalty_score(objective: str) -> float:
    return 1_000_000_000.0 if objective == "decode_time" else 1.0


def _score_record(
    *,
    objective: str,
    status: str,
    ler: float,
    decode_seconds: float,
) -> float:
    if status != "pass":
        return _penalty_score(objective)
    if objective == "decode_time":
        return float(decode_seconds)
    return float(ler)


def load_records(ledger_path: str | Path) -> list[dict[str, Any]]:
    path = Path(ledger_path)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def append_records(ledger_path: str | Path, records: list[dict[str, Any]]) -> None:
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_records(path)
    next_id = max([int(record.get("experiment_id", 0)) for record in existing] + [0]) + 1
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            item = dict(record)
            item["experiment_id"] = next_id
            item["created_at"] = datetime.now(timezone.utc).isoformat()
            handle.write(json.dumps(item, sort_keys=True) + "\n")
            next_id += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode one dataset and append one ledger row.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--decoder", type=Path, required=True)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--time-cap-seconds", type=float, default=5.0)
    parser.add_argument("--objective", choices=("ler", "decode_time"), default="ler")
    parser.add_argument("--ler-cap", type=float, default=1.0)
    parser.add_argument("--ledger", type=Path, default=ROOT / "output" / "ledger" / "experiments.jsonl")
    args = parser.parse_args()
    record = evaluate_dataset(
        dataset_path=args.dataset,
        decoder_path=args.decoder,
        lane=args.lane,
        round_index=args.round,
        time_cap_seconds=args.time_cap_seconds,
        objective=args.objective,
        ler_cap=args.ler_cap,
    )
    append_records(args.ledger, [record])
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import bz2
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


RELEASE_TAG = "0.2.0"
RELEASE_NAME = "NVIDIA/cudaqx 0.2.0"
RELEASE_DOWNLOAD_BASE = f"https://github.com/NVIDIA/cudaqx/releases/download/{RELEASE_TAG}"


@dataclass(frozen=True)
class QLDPCDatasetSpec:
    name: str

    @property
    def url(self) -> str:
        return f"{RELEASE_DOWNLOAD_BASE}/{self.name}"


DEFAULT_QLDPC_DATASETS = (
    QLDPCDatasetSpec("osd_216_865_0.005.json.bz2"),
    QLDPCDatasetSpec("osd_288_1585_0.005.json.bz2"),
    QLDPCDatasetSpec("osd_360_2305_0.005.json.bz2"),
    QLDPCDatasetSpec("osd_432_3025_0.005.json.bz2"),
    QLDPCDatasetSpec("osd_504_3745_0.005.json.bz2"),
)


def default_dataset_urls() -> list[str]:
    return [spec.url for spec in DEFAULT_QLDPC_DATASETS]


def default_dataset_paths(data_dir: str | Path = "data") -> list[Path]:
    root = Path(data_dir)
    return [root / spec.name for spec in DEFAULT_QLDPC_DATASETS]


def ensure_default_datasets(data_dir: str | Path = "data") -> list[Path]:
    root = Path(data_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for spec in DEFAULT_QLDPC_DATASETS:
        output = root / spec.name
        if not output.exists():
            with urllib.request.urlopen(spec.url, timeout=120) as response:
                output.write_bytes(response.read())
        paths.append(output)
    return paths


def dataset_name_from_path(path: str | Path) -> str:
    name = Path(path).name
    if name.endswith(".json.bz2"):
        return name.removesuffix(".json.bz2")
    if name.endswith(".npz"):
        return name.removesuffix(".npz")
    return Path(name).stem


def _csr_to_dense(
    *,
    shape: list[int],
    indptr: list[int],
    indices: list[int],
) -> np.ndarray:
    rows, cols = int(shape[0]), int(shape[1])
    if len(indptr) != rows + 1:
        raise ValueError(f"CSR indptr length {len(indptr)} does not match rows {rows}")
    dense = np.zeros((rows, cols), dtype=np.uint8)
    for row in range(rows):
        start = int(indptr[row])
        stop = int(indptr[row + 1])
        row_indices = np.asarray(indices[start:stop], dtype=np.int64)
        if row_indices.size:
            if row_indices.min() < 0 or row_indices.max() >= cols:
                raise ValueError(f"CSR index out of bounds in row {row}")
            dense[row, row_indices] = 1
    return np.ascontiguousarray(dense, dtype=np.uint8)


def load_release_dataset(path: str | Path) -> tuple[dict[str, Any], np.ndarray, str]:
    dataset_path = Path(path)
    with bz2.open(dataset_path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)

    H = _csr_to_dense(
        shape=payload["shape"],
        indptr=payload["H_indptr"],
        indices=payload["H_indices"],
    )
    observable_matrix = _csr_to_dense(
        shape=payload["obs_mat_shape"],
        indptr=payload["obs_mat_indptr"],
        indices=payload["obs_mat_indices"],
    )
    trials = payload["trials"]
    syndromes = np.ascontiguousarray(
        [trial["syndrome_truth"] for trial in trials],
        dtype=np.uint8,
    )
    logical_observables = np.ascontiguousarray(
        [trial["obs_truth"] for trial in trials],
        dtype=np.uint8,
    )
    priors = np.asarray(payload["error_rate_vec"], dtype=np.float64)
    if H.shape[1] != observable_matrix.shape[0]:
        raise ValueError(
            f"H block size {H.shape[1]} != observable rows {observable_matrix.shape[0]}"
        )
    if H.shape[1] != priors.shape[0]:
        raise ValueError(f"H block size {H.shape[1]} != prior length {priors.shape[0]}")
    if syndromes.shape != (len(trials), H.shape[0]):
        raise ValueError(f"syndrome shape {syndromes.shape} does not match H rows {H.shape[0]}")
    if logical_observables.shape != (len(trials), observable_matrix.shape[1]):
        raise ValueError(
            "logical observable shape does not match observable matrix columns"
        )
    metadata = {
        "code_family": "qldpc",
        "source_release": RELEASE_NAME,
        "source_asset": dataset_path.name,
        "error_rate": float(payload.get("error_rate", 0.0)),
        "max_iter": int(payload.get("max_iter", 0)),
        "num_trials": int(payload.get("num_trials", len(trials))),
    }
    return {
        "H": H,
        "syndromes": syndromes,
        "observable_matrix": observable_matrix,
        "priors": priors,
        "metadata": metadata,
    }, logical_observables, dataset_name_from_path(dataset_path)

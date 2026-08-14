"""Validate hashes for files that optimizer researchers may not edit."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "fixed_manifest.json"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_fixed_files():
    if not MANIFEST_PATH.exists():
        return ["fixed_manifest.json is missing"]
    manifest = json.loads(MANIFEST_PATH.read_text())
    errors = []
    for relative, expected in manifest["files"].items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"{relative} is missing")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"{relative} hash mismatch")
    return errors

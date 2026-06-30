from __future__ import annotations

import argparse
from pathlib import Path

from qldpc_data import ensure_default_datasets


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Download default QLDPC release datasets.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "output" / "data")
    args = parser.parse_args()
    for path in ensure_default_datasets(args.data_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

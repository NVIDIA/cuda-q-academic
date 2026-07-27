"""Run one serialized round for each independent researcher."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CIRCUITS = ("nonlocal", "controlled")


def main():
    return_codes = []
    for circuit in CIRCUITS:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "run_round.py"), circuit],
            cwd=ROOT,
            check=False,
        )
        return_codes.append(completed.returncode)
    return 0 if all(code == 0 for code in return_codes) else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compatibility wrapper for d11_convergence_detector.py at repo root."""

from pathlib import Path
import runpy
import sys


def main() -> int:
    repo_root_script = Path(__file__).resolve().parents[1] / "d11_convergence_detector.py"
    if not repo_root_script.exists():
        print(
            "ERROR: canonical detector missing at d11_convergence_detector.py",
            file=sys.stderr,
        )
        return 1
    runpy.run_path(str(repo_root_script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

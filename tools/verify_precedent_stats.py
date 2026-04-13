
#!/usr/bin/env python3
"""Compatibility wrapper for the canonical verifier at repo root.

This file remains for backward compatibility with earlier references to
`tools/verify_precedent_stats.py`. The authoritative implementation is
`verify_precedent_stats.py` at repository root.
"""

from pathlib import Path
import runpy
import sys


def main() -> int:
    repo_root_script = Path(__file__).resolve().parents[1] / "verify_precedent_stats.py"
    if not repo_root_script.exists():
        print(
            "ERROR: canonical verifier missing at verify_precedent_stats.py",
            file=sys.stderr,
        )
        return 1
    runpy.run_path(str(repo_root_script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

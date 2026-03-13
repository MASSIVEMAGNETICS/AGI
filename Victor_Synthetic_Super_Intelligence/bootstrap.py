#!/usr/bin/env python3
"""
Victor one-command bootstrapper.

Actions:
- Installs Python dependencies (requirements.txt)
- Runs a lightweight smoke check to verify core imports

Usage:
    python bootstrap.py
    python bootstrap.py --smoke-only
    python bootstrap.py --allow-missing
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).parent
REQUIREMENTS = ROOT / "requirements.txt"
DEFAULT_PYTHON = sys.executable


def _run(cmd, check: bool = True) -> int:
    """Run a command and stream output."""
    print(f"[bootstrap] $ {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=check)
    return proc.returncode


def install_requirements(python_bin: str = DEFAULT_PYTHON) -> None:
    """Install dependencies from requirements.txt."""
    if not REQUIREMENTS.exists():
        print("[bootstrap] requirements.txt not found; skipping install.")
        return
    _run([python_bin, "-m", "pip", "install", "-r", str(REQUIREMENTS)])


def smoke_check(allow_missing: bool = False) -> Tuple[Dict[str, bool], bool]:
    """Verify critical imports are available."""
    summary = {
        "python": sys.version,
        "numpy": False,
        "victor_interactive": False,
    }
    ok = True

    def _mark(label: str, exc: Exception):
        nonlocal ok
        print(f"[bootstrap] {label} import failed: {exc}")
        ok = ok and allow_missing

    try:
        import numpy as _np  # noqa: F401

        summary["numpy"] = True
    except Exception as exc:  # pragma: no cover - environment dependent
        _mark("numpy", exc)

    try:
        __import__("victor_interactive")
        summary["victor_interactive"] = True
    except Exception as exc:  # pragma: no cover - environment dependent
        _mark("victor_interactive", exc)

    return summary, ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Victor bootstrapper")
    parser.add_argument(
        "--python",
        default=DEFAULT_PYTHON,
        help="Python executable to use for pip installs (default: current interpreter)",
    )
    parser.add_argument(
        "--smoke-only",
        action="store_true",
        help="Skip installs and only run smoke checks",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Treat missing optional dependencies as warnings (exit 0)",
    )
    args = parser.parse_args()

    print("[bootstrap] Starting Victor bootstrap")
    print(f"[bootstrap] Using python: {args.python}")

    if not args.smoke_only:
        install_requirements(args.python)

    summary, ok = smoke_check(allow_missing=args.allow_missing)
    print("[bootstrap] Smoke summary:")
    print(json.dumps(summary, indent=2))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Guided setup wizard for Victor (beginner-friendly).

Flow:
- Validate Python environment
- Install dependencies (delegates to bootstrap.py)
- Run a smoke check
- Optionally launch the runtime

One-command, no-prompt mode:
    python guided_setup.py --auto --launch-runtime
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple

ROOT = Path(__file__).parent
BOOTSTRAP = ROOT / "bootstrap.py"
RUNTIME = ROOT / "victor_interactive.py"


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _prompt_bool(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def run_step(title: str, fn: Callable[[], bool]) -> bool:
    print(f"\n=== {title} ===")
    try:
        return fn()
    except KeyboardInterrupt:
        print("Cancelled by user.")
        return False
    except Exception as exc:
        print(f"Step failed: {exc}")
        return False


def step_validate_python() -> bool:
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    return sys.version_info >= (3, 8)


def step_install() -> bool:
    code, out, err = _run([sys.executable, str(BOOTSTRAP), "--allow-missing"])
    print(out)
    if err:
        print(err)
    return code == 0


def step_smoke() -> bool:
    code, out, err = _run([sys.executable, str(BOOTSTRAP), "--smoke-only", "--allow-missing"])
    print(out)
    if err:
        print(err)
    return code == 0


def step_launch_runtime() -> bool:
    if not RUNTIME.exists():
        print("Runtime script not found; skipping launch.")
        return False
    print("Launching Victor runtime in a new process...")
    try:
        subprocess.Popen([sys.executable, str(RUNTIME)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Victor runtime started. Check the other window/process for the interface.")
        return True
    except Exception as exc:  # pragma: no cover - launch depends on env
        print(f"Launch failed: {exc}")
        return False


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Victor Guided Setup Wizard")
    parser.add_argument(
        "--auto",
        "--yes",
        action="store_true",
        help="Run all steps without prompts (best for non-technical users).",
    )
    parser.add_argument(
        "--launch-runtime",
        action="store_true",
        help="Attempt to launch victor_interactive.py after setup.",
    )
    parser.add_argument(
        "--skip-smoke",
        action="store_true",
        help="Skip smoke check step.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    print("Victor Guided Setup")
    print("-------------------")
    print("This wizard will install everything, run a check, and (optionally) launch Victor.")
    if not args.auto and not _prompt_bool("Continue with setup?", True):
        return 1

    steps = [
        ("Validate Python environment", step_validate_python),
        ("Install dependencies", step_install),
    ]
    if not args.skip_smoke:
        steps.append(("Run smoke check", step_smoke))
    if args.launch_runtime:
        steps.append(("Launch Victor runtime", step_launch_runtime))

    results = []
    for title, fn in steps:
        ok = run_step(title, fn)
        results.append((title, ok))
        if not ok and not args.auto:
            if not _prompt_bool("Continue despite failure?", False):
                break

    print("\nSummary:")
    summary = {title: ok for title, ok in results}
    print(json.dumps(summary, indent=2))
    all_ok = all(ok for _, ok in results)
    if all_ok:
        print("\n✅ Setup complete. Next: open the Victor runtime window. If it didn't launch, run:")
        print(f"  python {RUNTIME.name}")
    else:
        print("\n⚠️ Some steps failed. Re-run with:")
        print("  python guided_setup.py --auto --launch-runtime")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

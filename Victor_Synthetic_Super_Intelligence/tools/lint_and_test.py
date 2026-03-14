#!/usr/bin/env python3
"""
Minimal lint/test harness for Victor.

Runs:
- compileall for syntax validation
- unittest discovery for test_*.py (skip import errors as failures)
"""
from __future__ import annotations

import argparse
import compileall
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compile_sources() -> bool:
    print("[qa] compileall .")
    return compileall.compile_dir(str(ROOT), quiet=1)


def run_tests(pattern: str = "test_*.py") -> bool:
    print(f"[qa] unittest discovery ({pattern})")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(ROOT), pattern=pattern)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest discovery")
    parser.add_argument("--pattern", default="test_*.py", help="Test pattern")
    args = parser.parse_args()

    ok = compile_sources()
    if not args.skip_tests:
        ok &= run_tests(pattern=args.pattern)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

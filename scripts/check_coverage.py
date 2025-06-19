#!/usr/bin/env python3
"""Script to verify 100% test coverage."""

import subprocess
import sys


def run_coverage() -> bool:
    """Run coverage analysis and verify 100% coverage.

    Returns:
        True if coverage is 100%, False otherwise.
    """
    try:
        # run tests with coverage
        result = subprocess.run(
            ["python", "-m", "coverage", "run", "-m", "pytest", "tests/"],
            capture_output=True,
            text=True,
            check=True,
        )

        # generate coverage report
        result = subprocess.run(
            ["python", "-m", "coverage", "report", "--fail-under=100"],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ 100% test coverage achieved!")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print("❌ Coverage check failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


if __name__ == "__main__":
    success = run_coverage()
    sys.exit(0 if success else 1)

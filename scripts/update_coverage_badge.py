#!/usr/bin/env python3
"""Generate coverage badge for README."""

import re
import subprocess


def get_coverage_percentage() -> int:
    """Get the current coverage percentage.

    Returns:
        Coverage percentage as integer.
    """
    try:
        # run coverage report
        result = subprocess.run(
            ["python", "-m", "coverage", "report"],
            capture_output=True,
            text=True,
            check=True,
        )

        # extract total coverage percentage
        lines = result.stdout.strip().split("\n")
        total_line = [line for line in lines if line.startswith("TOTAL")]

        if total_line:
            # extract percentage from "TOTAL    109      0   100%"
            match = re.search(r"(\d+)%", total_line[0])
            if match:
                return int(match.group(1))

        return 0

    except subprocess.CalledProcessError:
        return 0


def update_readme_badge(coverage: int) -> None:
    """Update the coverage badge in README.md.

    Args:
        coverage: Coverage percentage.
    """
    try:
        with open("README.md") as f:
            content = f.read()

        # determine badge color based on coverage
        if coverage >= 95:
            color = "brightgreen"
        elif coverage >= 80:
            color = "green"
        elif coverage >= 70:
            color = "yellow"
        else:
            color = "red"

        # Update badge
        badge_pattern = r"\[!\[Coverage\]\(https://img\.shields\.io/badge/coverage-\d+%25-\w+\.svg\)\]"
        new_badge = f"[![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-{color}.svg)]"

        updated_content = re.sub(badge_pattern, new_badge, content)

        with open("README.md", "w") as f:
            f.write(updated_content)

        print(f"✅ Updated README badge: {coverage}% coverage ({color})")

    except Exception as e:
        print(f"❌ Failed to update README: {e}")


if __name__ == "__main__":
    coverage = get_coverage_percentage()
    print(f"Current coverage: {coverage}%")

    if coverage > 0:
        update_readme_badge(coverage)
    else:
        print("❌ Could not determine coverage percentage")

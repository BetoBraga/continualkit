"""Gate: fail if PR diff exceeds the line limit.

Usage:
    python scripts/check_diff_size.py --max-lines 400

Exit codes:
    0 — diff is within limit
    1 — diff exceeds limit
"""

import argparse
import subprocess
import sys


def count_diff_lines() -> int:
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD", "--stat"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = result.stdout.strip().splitlines()
    if not lines:
        return 0
    # Last line: "X files changed, Y insertions(+), Z deletions(-)"
    summary = lines[-1]
    total = 0
    for part in summary.split(","):
        part = part.strip()
        if "insertion" in part or "deletion" in part:
            try:
                total += int(part.split()[0])
            except (ValueError, IndexError):
                pass
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Check PR diff size.")
    parser.add_argument("--max-lines", type=int, default=400)
    args = parser.parse_args()

    total = count_diff_lines()
    print(f"Diff size: {total} lines (limit: {args.max_lines})")

    if total > args.max_lines:
        print(f"❌ Diff too large: {total} > {args.max_lines} lines.")
        print("   Split this PR into smaller, focused changes.")
        sys.exit(1)

    print(f"✅ Diff size OK: {total} <= {args.max_lines} lines.")


if __name__ == "__main__":
    main()

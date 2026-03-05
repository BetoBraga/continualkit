"""Gate: validate that the PR body contains all required template sections.

Usage:
    python scripts/validate_pr_template.py --body "$(gh pr view $PR_NUMBER --json body -q .body)"

Exit codes:
    0 — all required sections present
    1 — missing sections detected
"""

import argparse
import sys

REQUIRED_SECTIONS = [
    "## Related Issue",
    "## What Changed",
    "## How I Tested",
    "## Checklist",
]

PLACEHOLDER_PATTERNS = [
    "Fixes #<!-- issue number -->",
    "<!-- Clear, objective description",
    "<!-- Describe the tests",
]


def validate(body: str) -> tuple[list[str], list[str]]:
    missing = []
    unfilled = []

    for section in REQUIRED_SECTIONS:
        if section not in body:
            missing.append(section)

    for placeholder in PLACEHOLDER_PATTERNS:
        if placeholder in body:
            unfilled.append(placeholder)

    return missing, unfilled


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate PR template completeness.")
    parser.add_argument("--body", required=True, help="PR body text")
    args = parser.parse_args()

    missing, unfilled = validate(args.body)
    ok = True

    if missing:
        ok = False
        print("❌ Missing required sections:")
        for s in missing:
            print(f"   {s}")

    if unfilled:
        ok = False
        print("❌ Unfilled placeholders found:")
        for p in unfilled:
            print(f"   {p!r}")

    if ok:
        print("✅ PR template valid — all sections present and filled.")
    else:
        print("\n   Fill in all sections of the PR template before requesting review.")
        sys.exit(1)


if __name__ == "__main__":
    main()

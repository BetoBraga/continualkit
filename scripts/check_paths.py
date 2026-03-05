"""Gate: fail if PR touches forbidden paths.

Usage:
    python scripts/check_paths.py

Exit codes:
    0 — all changed files are within the allowlist
    1 — forbidden path detected
"""

import subprocess
import sys

# Files/directories the agent is ALLOWED to touch autonomously
ALLOWLIST_PREFIXES = (
    "src/continualkit/",
    "tests/",
    "docs/",
    "examples/",
    "README.md",
)

# Files/directories the agent must NEVER touch without human review
FORBIDDEN_PREFIXES = (
    ".github/workflows/",
    ".github/CODEOWNERS",
    "scripts/",
    "pyproject.toml",
    "LICENSE",
    "CONTRIBUTING.md",
)


def get_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]


def main() -> None:
    changed = get_changed_files()

    if not changed:
        print("No changed files detected.")
        sys.exit(0)

    violations = []
    warnings = []

    for filepath in changed:
        # Check forbidden first
        if any(filepath.startswith(p) for p in FORBIDDEN_PREFIXES):
            violations.append(filepath)
            continue
        # Check if within allowlist
        if not any(filepath.startswith(p) for p in ALLOWLIST_PREFIXES):
            warnings.append(filepath)

    if warnings:
        print("⚠️  Files outside allowlist (manual review required):")
        for f in warnings:
            print(f"   {f}")

    if violations:
        print("\n❌ Forbidden paths touched — human approval required:")
        for f in violations:
            print(f"   {f}")
        print(
            "\n   These paths require explicit maintainer review.\n"
            "   Remove label 'agent-generated' and request review."
        )
        sys.exit(1)

    print(f"✅ Path check OK — {len(changed)} file(s) within allowed scope.")


if __name__ == "__main__":
    main()

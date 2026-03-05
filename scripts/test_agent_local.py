"""Local dry-run of the agent dispatch pipeline.

Simulates what agent-dispatch.yml does in GitHub Actions — without needing
a push, a label trigger, or CI minutes.

Usage:
    # Test against a real GitHub issue (fetches body via gh CLI)
    python scripts/test_agent_local.py --issue 2

    # Test against a local issue body file
    python scripts/test_agent_local.py --issue-file /tmp/my_issue.txt

    # Dry-run only: generate files but don't run gates
    python scripts/test_agent_local.py --issue 2 --no-gates

    # Use a specific provider/model for this run (overrides env vars)
    AGENT_LLM_PROVIDER=openrouter AGENT_LLM_MODEL=anthropic/claude-haiku-4-5 \\
        python scripts/test_agent_local.py --issue 2

Environment:
    AGENT_LLM_KEY       — your API key (required, except for ollama)
    AGENT_LLM_PROVIDER  — provider (default: openrouter)
    AGENT_LLM_MODEL     — model (default: provider default)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path  # noqa: E402

SYSTEM_PROMPT = """You are an implementation agent for ContinualKit, a Python continual learning toolkit for LLMs.

Rules:
- Only create or modify files in: src/continualkit/, tests/, docs/, examples/, README.md
- NEVER touch: .github/workflows/, .github/CODEOWNERS, scripts/, pyproject.toml, LICENSE
- Always write tests for every new function or class
- Keep diff small (< 200 lines total across all files)
- Use ruff-compatible Python: py310+, type hints, no unused imports
- Use stdlib only unless the issue explicitly allows a dependency
- One function or class per PR, no premature abstraction
- Tests must be in the tests/ directory, mirroring the src/ structure
- For tests that require optional dependencies (torch, transformers, peft, etc.), add pytest.importorskip at the top of the test module: torch = pytest.importorskip("torch")

Output ONLY valid JSON with this exact structure:
{
  "files": [
    {"path": "src/continualkit/eval/__init__.py", "content": "...full file content..."},
    {"path": "tests/eval/test_metrics.py", "content": "...full file content..."}
  ],
  "pr_description": "markdown string describing what was implemented and why"
}"""


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=False)


def fetch_issue_body(issue_number: int) -> str:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--json",
            "body,title",
            "-q",
            '.title + "\\n\\n" + .body',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def call_llm(user_msg: str, out_path: str) -> dict:
    subprocess.run(
        [
            sys.executable,
            "scripts/llm_adapter.py",
            "--system",
            SYSTEM_PROMPT,
            "--user",
            user_msg,
            "--temperature",
            "0.2",
            "--out",
            out_path,
        ],
        check=True,
    )
    with open(out_path) as f:
        return json.load(f)


def write_generated_files(response: dict) -> list[str]:
    written = []
    for file_spec in response.get("files", []):
        path = Path(file_spec["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_spec["content"])
        written.append(str(path))
        print(f"  ✅ Written: {path}")
    return written


def run_gates() -> bool:
    print("\n── Running gates ─────────────────────────────────────")
    ok = True

    print("\n[1/4] ruff format (auto-fix)")
    subprocess.run([sys.executable, "-m", "ruff", "format", "."], check=False)
    subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", "."], check=False)

    print("\n[2/4] ruff check")
    r = subprocess.run([sys.executable, "-m", "ruff", "check", "."], check=False)
    if r.returncode != 0:
        ok = False

    print("\n[3/4] pytest")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=short", "-q"], check=False
    )
    if r.returncode != 0:
        ok = False

    print("\n[4/4] diff size check")
    r = subprocess.run(
        [sys.executable, "scripts/check_diff_size.py", "--max-lines", "400"],
        check=False,
    )
    if r.returncode != 0:
        ok = False

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Local dry-run of agent dispatch.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--issue", type=int, metavar="N", help="GitHub issue number to fetch"
    )
    group.add_argument(
        "--issue-file", metavar="PATH", help="Local file containing the issue body"
    )
    parser.add_argument(
        "--no-gates", action="store_true", help="Skip gate checks after generation"
    )
    args = parser.parse_args()

    print("═" * 60)
    print("  ContinualKit — Local Agent Dry Run")
    print("═" * 60)

    # ── Fetch issue ────────────────────────────────────────────────
    if args.issue:
        print(f"\nFetching issue #{args.issue} from GitHub...")
        issue_body = fetch_issue_body(args.issue)
        user_msg = f"Issue #{args.issue}:\n\n{issue_body}"
    else:
        issue_body = Path(args.issue_file).read_text()
        user_msg = f"Issue (local file):\n\n{issue_body}"

    print(f"\n{'─' * 40}")
    print(issue_body[:400] + ("..." if len(issue_body) > 400 else ""))
    print(f"{'─' * 40}\n")

    # ── Call LLM ───────────────────────────────────────────────────
    provider = os.environ.get("AGENT_LLM_PROVIDER", "openrouter")
    model = os.environ.get("AGENT_LLM_MODEL", "")
    print(f"Calling LLM — provider: {provider}, model: {model or 'default'}...")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out_path = f.name

    response = call_llm(user_msg, out_path)

    # ── Write files ────────────────────────────────────────────────
    print(f"\nGenerating {len(response.get('files', []))} file(s):")
    written = write_generated_files(response)

    print(f"\nPR description preview:\n{'─' * 40}")
    print(response.get("pr_description", "(none)")[:600])
    print(f"{'─' * 40}")

    # ── Gates ──────────────────────────────────────────────────────
    if args.no_gates:
        print("\n⚠  Gates skipped (--no-gates).")
        print("\nGenerated files (review before committing):")
        for f in written:
            print(f"  {f}")
        return

    gates_passed = run_gates()

    print("\n═" * 60)
    if gates_passed:
        print("✅  ALL GATES PASSED — ready to open a PR.")
        print("\nNext steps:")
        print("  1. Review the generated files above")
        print("  2. Apply label 'agent-ready' on GitHub to run via CI")
        print("     OR commit manually: git add -A && git commit -m 'feat: ...'")
    else:
        print("❌  GATES FAILED — review errors above before pushing.")
        print("\nGenerated files (may need manual fixes):")
        for f in written:
            print(f"  {f}")
    print("═" * 60)


if __name__ == "__main__":
    main()

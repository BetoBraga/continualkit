# Contributing to ContinualKit

Thanks for your interest. Before anything: this is an R&D-first project. Baseline quality matters more than feature quantity.

---

## Principles

1. **Evidence over opinion.** Every change that affects training or eval behavior needs a benchmark comparing before/after.
2. **Simple baseline first.** Before proposing something exotic (MoE, smart replay selection, adapters), the simple baseline (replay + regularization) must be solid.
3. **No regression.** If your change breaks existing tasks without clear justification, it's a no.

---

## Development Setup

```bash
git clone https://github.com/BetoBraga/continualkit
cd continualkit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Verify setup:

```bash
ruff check .           # should return 0 errors
ruff format --check .  # should return 0 errors
pytest                 # all tests passing
```

---

## Opening an Issue

Use the templates — they exist for a reason.

- **Bug:** describe the expected behavior, the actual behavior, and how to reproduce it.
- **Feature:** describe the pain it solves, the success metric, and the smallest test that validates the idea.
- **`agent-ready`:** issues labeled with this tag may be automatically implemented by the agent pipeline. Use the specific template — it requires a hypothesis + acceptance criteria + well-defined scope.

---

## Opening a PR

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Ensure `ruff check .`, `ruff format --check .`, and `pytest` all pass locally
4. Open the PR using the template — all sections are required
5. PRs without tests for new code are not accepted

---

## Code Style

- Ruff handles everything: `ruff check --fix . && ruff format .`
- Type hints on public functions
- Docstrings on public modules and classes
- Atomic commits with descriptive messages

---

## What NOT to Submit (to save everyone time)

- Features without clear acceptance criteria
- Changes to `.github/workflows/` without explicit maintainer review
- Heavy new dependencies without clear justification
- "This would be nice to have" without data showing someone needs it

---

## Questions

Open an issue with the `question` label. Best-effort response.

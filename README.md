# ContinualKit

**Update your LLM without playing roulette with regression and forgetting.**

Incremental fine-tuning, first-class forgetting evaluation, automatic release gates, and rollback with full audit trail. For teams that have already been burned by "it worked yesterday, now it's broken" — and don't want to go through it again.

---

## The Problem

The typical fine-tuning cycle in production is broken:

1. New data arrives → quick fine-tune
2. Push to prod → silent regression on old tasks
3. Nobody notices until support explodes
4. Remedy: full retraining — expensive, slow, and you still don't know what broke

The real gap isn't "training" — it's **training without forgetting + proving you didn't forget**.

---

## What It Is

An open-source Python toolkit that becomes your team's ML pipeline standard:

```
continual train    # incremental with replay + regularization
continual eval     # forgetting metrics suite per task
continual compare  # candidate vs current — clear diff before pushing
```

With **release gates**: the model doesn't go to prod if it breaks more than X% on old tasks.

---

## Status

**Pre-alpha — R&D in progress.**

The commands exist. The implementations don't yet. The current focus is defining the right interfaces and reference benchmark suite.

Follow progress in [GitHub Issues](https://github.com/BetoBraga/continualkit/issues) or contribute.

---

## Quickstart

```bash
# requires Python 3.10+
pip install continualkit

# or, for development
git clone https://github.com/BetoBraga/continualkit
cd continualkit
pip install -e ".[dev]"

# verify installation
continual --version
```

---

## Roadmap

| Milestone | Focus | Status |
|-----------|-------|--------|
| M1 — MVP | Functional CLI + eval suite + basic replay + HF/PEFT integration | In progress |
| M2 — Runtime | Versioned storage, automatic release gates, FastAPI, n8n pipeline | Planned |
| M3 — SOTA | MoE routing, smart replay, drift detection, automatic policies | Future |

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

The most important rule: **no metric and regression test, no merge**. Every feature must become a measurable experiment or gate.

Issues labeled `agent-ready` are prioritized for automatic implementation via our agent pipeline.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

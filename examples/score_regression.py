"""Compare two fixed task-score sets without running a model."""

from continualkit.eval import compute_forgetting


def main() -> None:
    before = {"support_qa": 0.90, "tool_selection": 0.70}
    after = {"support_qa": 0.80, "tool_selection": 0.75}

    for task, score in before.items():
        candidate = after[task]
        loss = max(0.0, score - candidate)
        print(f"{task}: {score:.2f} -> {candidate:.2f} | loss: {loss:.2f}")

    forgetting = compute_forgetting(before, after)
    print(
        f"mean forgetting: {forgetting:.2f} ({forgetting * 100:.1f} percentage points)"
    )


if __name__ == "__main__":
    main()

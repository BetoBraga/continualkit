def compute_forgetting(before: dict[str, float], after: dict[str, float]) -> float:
    if before.keys() != after.keys():
        raise ValueError("before and after must have the same keys")
    if not before:
        raise ValueError("before and after must not be empty")
    forgetting = [max(0, before[t] - after[t]) for t in before]
    return sum(forgetting) / len(forgetting)

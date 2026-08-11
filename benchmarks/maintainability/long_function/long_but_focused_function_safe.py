def summarize_scores(scores: list[int]) -> dict[str, float | int]:
    total = sum(scores)
    count = len(scores)

    if count == 0:
        return {
            "count": 0,
            "total": 0,
            "average": 0.0,
            "minimum": 0,
            "maximum": 0,
        }

    average = total / count
    minimum = min(scores)
    maximum = max(scores)

    return {
        "count": count,
        "total": total,
        "average": average,
        "minimum": minimum,
        "maximum": maximum,
    }
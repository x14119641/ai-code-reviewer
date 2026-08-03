from reviewer.models import (
    BenchmarkResult,
    ResultProblem,
    ResultProblemType,
)
    
    
def inspect_result(
    result: BenchmarkResult,
) -> list[ResultProblem]:
    """Extract detection and severity problems from an exported result."""

    problems: list[ResultProblem] = []

    for evaluation in result.evaluations:
        if evaluation.get("false_positive") is True:
            problems.append(
                ResultProblem(
                    problem_type=ResultProblemType.FALSE_POSITIVE,
                    evaluation=evaluation,
                )
            )
            continue

        if evaluation.get("false_negative") is True:
            problems.append(
                ResultProblem(
                    problem_type=ResultProblemType.FALSE_NEGATIVE,
                    evaluation=evaluation,
                )
            )
            continue

        if evaluation.get("passed") is False:
            if evaluation.get("rule_matched") is False:
                problems.append(
                    ResultProblem(
                        problem_type=ResultProblemType.RULE_MISMATCH,
                        evaluation=evaluation,
                    )
                )

            if evaluation.get("category_matched") is False:
                problems.append(
                    ResultProblem(
                        problem_type=ResultProblemType.CATEGORY_MISMATCH,
                        evaluation=evaluation,
                    )
                )

        if (
            evaluation.get("expected_issue_count", 0) > 0
            and evaluation.get("actual_issue_count", 0) > 0
            and evaluation.get("severity_matched") is False
        ):
            problems.append(
                ResultProblem(
                    problem_type=ResultProblemType.SEVERITY_MISMATCH,
                    evaluation=evaluation,
                )
            )

    return problems

from reviewer.models import BenchmarkResult, BenchmarkResultComparison


def compare_benchmark_results(
    old: BenchmarkResult,
    new: BenchmarkResult,
) -> BenchmarkResultComparison:
    old_by_path = {
        evaluation["benchmark"]["code_path"]: evaluation
        for evaluation in old.evaluations
    }

    new_by_path = {
        evaluation["benchmark"]["code_path"]: evaluation
        for evaluation in new.evaluations
    }

    fixed: list[str] = []
    regressed: list[str] = []
    still_failing: list[str] = []

    for code_path in sorted(old_by_path.keys() & new_by_path.keys()):
        old_evaluation = old_by_path[code_path]
        new_evaluation = new_by_path[code_path]

        if not old_evaluation["passed"] and new_evaluation["passed"]:
            fixed.append(code_path)

        elif old_evaluation["passed"] and not new_evaluation["passed"]:
            regressed.append(code_path)

        elif not old_evaluation["passed"] and not new_evaluation["passed"]:
            still_failing.append(code_path)

    
    added = tuple(sorted(new_by_path.keys() - old_by_path.keys()))
    removed = tuple(sorted(old_by_path.keys() - new_by_path.keys()))
    
    return BenchmarkResultComparison(
        fixed=tuple(fixed),
        regressed=tuple(regressed),
        still_failing=tuple(still_failing),
        added=added,
        removed=removed,
    )
    
    
    
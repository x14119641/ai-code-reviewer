from pathlib import Path

from reviewer.benchmark_comparison import compare_benchmark_results
from reviewer.models import BenchmarkResult, BenchmarkResultSummary


def make_result(evaluations: list[dict]) -> BenchmarkResult:
    summary = BenchmarkResultSummary(
        source=Path("result.json"),
        prompt_version="v1",
        model="test-model",
        benchmark_count=len(evaluations),
        passed=sum(evaluation["passed"] for evaluation in evaluations),
        failed=sum(not evaluation["passed"] for evaluation in evaluations),
        false_positives=0,
        false_negatives=0,
        errors=0,
        accuracy=0.0,
        duration_seconds=0.0,
        severity_matches=0,
        severity_evaluated_count=0,
        severity_accuracy=0.0,
    )

    return BenchmarkResult(
        summary=summary,
        evaluations=evaluations,
    )


def test_compare_results_detects_fixed_benchmark():
    old = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": False,
            }
        ]
    )

    new = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": True,
            }
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ("benchmarks/example.py",)
    assert comparison.regressed == ()
    assert comparison.still_failing == ()
    assert comparison.added == ()
    assert comparison.removed == ()


def test_compare_results_detects_regressed_benchmark():
    old = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": True,
            }
        ]
    )

    new = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": False,
            }
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ()
    assert comparison.regressed == ("benchmarks/example.py",)
    assert comparison.still_failing == ()
    assert comparison.added == ()
    assert comparison.removed == ()


def test_compare_results_detects_still_failing_benchmark():
    old = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": False,
            }
        ]
    )

    new = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": False,
            }
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ()
    assert comparison.regressed == ()
    assert comparison.still_failing == ("benchmarks/example.py",)
    assert comparison.added == ()
    assert comparison.removed == ()


def test_compare_results_ignores_still_passing_benchmark():
    old = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": True,
            }
        ]
    )

    new = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/example.py",
                },
                "passed": True,
            }
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ()
    assert comparison.regressed == ()
    assert comparison.still_failing == ()
    assert comparison.added == ()
    assert comparison.removed == ()


def test_compare_results_detects_added_benchmark():
    old = make_result([])

    new = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/new_case.py",
                },
                "passed": True,
            }
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ()
    assert comparison.regressed == ()
    assert comparison.still_failing == ()
    assert comparison.added == ("benchmarks/new_case.py",)
    assert comparison.removed == ()


def test_compare_results_detects_removed_benchmark():
    old = make_result(
        [
            {
                "benchmark": {
                    "code_path": "benchmarks/old_case.py",
                },
                "passed": True,
            }
        ]
    )

    new = make_result([])

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ()
    assert comparison.regressed == ()
    assert comparison.still_failing == ()
    assert comparison.added == ()
    assert comparison.removed == ("benchmarks/old_case.py",)


def test_compare_results_classifies_multiple_benchmarks():
    old = make_result(
        [
            {"benchmark": {"code_path": "fixed.py"}, "passed": False},
            {"benchmark": {"code_path": "regressed.py"}, "passed": True},
            {"benchmark": {"code_path": "still_failing.py"}, "passed": False},
            {"benchmark": {"code_path": "still_passing.py"}, "passed": True},
            {"benchmark": {"code_path": "removed.py"}, "passed": True},
        ]
    )

    new = make_result(
        [
            {"benchmark": {"code_path": "fixed.py"}, "passed": True},
            {"benchmark": {"code_path": "regressed.py"}, "passed": False},
            {"benchmark": {"code_path": "still_failing.py"}, "passed": False},
            {"benchmark": {"code_path": "still_passing.py"}, "passed": True},
            {"benchmark": {"code_path": "added.py"}, "passed": True},
        ]
    )

    comparison = compare_benchmark_results(old, new)

    assert comparison.fixed == ("fixed.py",)
    assert comparison.regressed == ("regressed.py",)
    assert comparison.still_failing == ("still_failing.py",)
    assert comparison.added == ("added.py",)
    assert comparison.removed == ("removed.py",)

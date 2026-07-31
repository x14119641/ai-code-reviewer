import json
from pathlib import Path

from reviewer.benchmark_runner import (
    find_benchmark_files,
    run_benchmarks,
)
from reviewer.models import CodeReview, Issue

TEST_MODEL = "test-model"


def create_benchmark(
    directory: Path,
    *,
    name: str,
    expected_issues: list[dict[str, str]],
) -> Path:
    code_path = directory / f"{name}.py"
    definition_path = directory / f"{name}.json"

    code_path.write_text(
        "value = 1\n",
        encoding="utf-8",
    )

    definition_path.write_text(
        json.dumps(
            {
                "name": name,
                "expected_issues": expected_issues,
            }
        ),
        encoding="utf-8",
    )

    return code_path


def test_find_benchmark_files_recursively(
    tmp_path: Path,
) -> None:
    security_directory = tmp_path / "security"
    python_directory = tmp_path / "python"

    security_directory.mkdir()
    python_directory.mkdir()

    first_path = create_benchmark(
        security_directory,
        name="sql_injection",
        expected_issues=[],
    )

    second_path = create_benchmark(
        python_directory,
        name="mutable_default",
        expected_issues=[],
    )

    paths = find_benchmark_files(tmp_path)

    assert paths == tuple(sorted((first_path, second_path)))


def test_run_benchmarks_returns_summary(
    tmp_path: Path,
) -> None:
    clean_path = create_benchmark(
        tmp_path,
        name="clean_example",
        expected_issues=[],
    )

    unsafe_path = create_benchmark(
        tmp_path,
        name="unsafe_example",
        expected_issues=[
            {
                "category": "security",
                "rule": "sql_injection",
                "severity": "high",
                "explanation": "Unsafe input handling.",
            }
        ],
    )

    def fake_review(code_path: Path) -> CodeReview:
        if code_path.name == "unsafe_example.py":
            return CodeReview(
                issues=[
                    Issue(
                        title="Unsafe input",
                        severity="high",
                        rule="sql_injection",
                        category="security",
                        explanation="Unsafe input handling.",
                        recommendation="Validate the input.",
                    )
                ]
            )

        return CodeReview(issues=[])

    run = run_benchmarks(
        benchmark_paths=(clean_path, unsafe_path),
        review_function=fake_review,
        model=TEST_MODEL,
    )

    assert run.benchmark_count == 2
    assert run.passed == 2
    assert run.failed == 0
    assert run.false_positives == 0
    assert run.false_negatives == 0
    assert run.accuracy == 1.0
    assert run.failure_count == 0
    assert run.model == TEST_MODEL
    assert run.duration_seconds >= 0.0


def test_run_counts_false_positive(
    tmp_path: Path,
) -> None:
    code_path = create_benchmark(
        tmp_path,
        name="clean_example",
        expected_issues=[],
    )

    def fake_review(_: Path) -> CodeReview:
        return CodeReview(
            issues=[
                Issue(
                    title="Invented problem",
                    severity="low",
                    category="bug",
                    rule="duplicate_code",
                    explanation="This issue does not exist.",
                    recommendation="No change needed.",
                )
            ]
        )

    run = run_benchmarks(
        benchmark_paths=(code_path,), review_function=fake_review, model=TEST_MODEL
    )

    assert run.benchmark_count == 1
    assert run.passed == 0
    assert run.failed == 1
    assert run.false_positives == 1
    assert run.false_negatives == 0
    assert run.accuracy == 0.0


def test_run_counts_false_negative(
    tmp_path: Path,
) -> None:
    code_path = create_benchmark(
        tmp_path,
        name="unsafe_example",
        expected_issues=[
            {
                "category": "security",
                "rule": "sql_injection",
                "severity": "high",
                "explanation": "Unsafe input handling.",
            }
        ],
    )

    def fake_review(_: Path) -> CodeReview:
        return CodeReview(issues=[])

    run = run_benchmarks(
        benchmark_paths=(code_path,), review_function=fake_review, model=TEST_MODEL
    )

    assert run.benchmark_count == 1
    assert run.passed == 0
    assert run.failed == 1
    assert run.false_positives == 0
    assert run.false_negatives == 1


def test_empty_benchmark_run_has_zero_accuracy() -> None:
    def fake_review(_: Path) -> CodeReview:
        return CodeReview(issues=[])

    run = run_benchmarks(
        benchmark_paths=(), review_function=fake_review, model=TEST_MODEL
    )

    assert run.benchmark_count == 0
    assert run.passed == 0
    assert run.failed == 0
    assert run.accuracy == 0.0



def test_run_records_failure_and_continues(
    tmp_path: Path,
) -> None:
    first_path = create_benchmark(
        tmp_path,
        name="first_example",
        expected_issues=[],
    )

    broken_path = create_benchmark(
        tmp_path,
        name="broken_example",
        expected_issues=[],
    )

    third_path = create_benchmark(
        tmp_path,
        name="third_example",
        expected_issues=[],
    )

    reviewed_paths: list[Path] = []

    def fake_review(code_path: Path) -> CodeReview:
        reviewed_paths.append(code_path)

        if code_path.name == "broken_example.py":
            raise RuntimeError("The model returned invalid JSON")

        return CodeReview(issues=[])

    run = run_benchmarks(
        benchmark_paths=(
            first_path,
            broken_path,
            third_path,
        ),
        review_function=fake_review,
        model=TEST_MODEL,
    )

    assert reviewed_paths == [
        first_path,
        broken_path,
        third_path,
    ]

    assert run.benchmark_count == 3
    assert len(run.evaluations) == 2
    assert run.failure_count == 1

    assert run.passed == 2
    assert run.failed == 1
    assert run.accuracy == 2 / 3

    failure = run.failures[0]

    assert failure.benchmark.code_path == broken_path.resolve()
    assert failure.error_type == "RuntimeError"
    assert failure.message == "The model returned invalid JSON"
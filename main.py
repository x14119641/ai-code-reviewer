from pathlib import Path

import typer

from reviewer.benchmark_comparison import compare_benchmark_results
from reviewer.benchmark_runner import find_benchmark_files, run_benchmarks
from reviewer.benchmark_serialization import save_benchmark_run
from reviewer.diff_benchmark_runner import find_diff_benchmarks, run_diff_benchmarks
from reviewer.engine import (
    build_changed_files_context,
    find_diff_candidates,
    find_python_files,
    review_diff,
    review_diff_multi_pass,
    review_diff_specialized,
    review_file,
    review_file_specialized,
    review_files,
)
from reviewer.git_diff import (
    GitDiffError,
    get_changed_python_files,
    get_changed_python_files_against,
    get_git_diff,
    get_git_diff_against,
)
from reviewer.models import CodeReview, InferenceConfig
from reviewer.prompts import DEFAULT_PROMPT_VERSION
from reviewer.rendering import (
    build_category_comparison_table,
    build_comparison_table,
    build_rule_comparison_table,
    print_benchmark_evaluations,
    print_benchmark_failures,
    print_benchmark_progress,
    print_benchmark_summary,
    print_error,
    print_result_analysis,
    print_result_saved,
    print_review,
    print_review_progress,
    print_run_comparison,
    print_success,
    print_table,
    print_warning,
)
from reviewer.result_comparison import (
    ResultComparisonError,
    load_result,
    load_result_summaries,
    load_results,
)

app = typer.Typer()


@app.callback()
def main() -> None:
    """Local AI-powered code reviewer."""


@app.command("review")
def review_command(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review a single Python file."""
    try:
        result = review_file(path=path, model=model)
        print_review(review=result)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print_error("Could not read the file", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("review-folder")
def review_folder_command(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review all Python files in a folder."""
    try:
        files = find_python_files(path)
        total = len(files)
        if total == 0:
            print_warning("No Python files found.")
            return

        for i, result in enumerate(review_files(files, model), start=1):
            print_review_progress(
                current=i,
                total=total,
                path=result.path,
            )

            if result.error:
                print_error("Review failed", result.error)
                continue
            print_review(result.review)
        print_success(f"Reviewed {total} Python files.")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print_error("Review Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark")
def benchmark_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the benchmark",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
    prompt_version: str = typer.Option(
        DEFAULT_PROMPT_VERSION,
        "--prompt-version",
        help="Prompt version used for the benchmark.",
    ),
) -> None:
    """Evaluate the AI reviewer using benchmark cases."""

    try:
        benchmark_paths = find_benchmark_files(path)

        if not benchmark_paths:
            print_warning("No benchmark files found.")
            return

        total = len(benchmark_paths)
        current = 0

        def review_with_model(
            source_path: Path,
        ) -> CodeReview:
            nonlocal current

            current += 1

            print_benchmark_progress(
                current=current,
                total=total,
                path=source_path,
            )

            return review_file(
                source_path,
                model,
                prompt_version=prompt_version,
            )

        run = run_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=prompt_version,
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / prompt_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("compare-results")
def compare_results(
    directory: Path,
    by_rule: bool = typer.Option(
        False,
        "--by-rule",
        help="Compare benchmark results grouped by rule",
    ),
    by_category: bool = typer.Option(
        False,
        "--by-category",
        help="Compare benchmark results grouped by category",
    ),
) -> None:
    """Compare previously exported benchmark result files."""
    if by_rule and by_category:
        print_error(
            "Error",
            "Use either --by-rule or --by-category, not both.",
        )
        raise typer.Exit(code=1)

    try:
        if by_rule:
            results = load_results(directory)

            results.sort(
                key=lambda result: result.summary.accuracy,
                reverse=True,
            )

            table = build_rule_comparison_table(results)

        elif by_category:
            results = load_results(directory)

            results.sort(
                key=lambda result: result.summary.accuracy,
                reverse=True,
            )

            table = build_category_comparison_table(results)

        else:
            summaries = load_result_summaries(directory)

            summaries.sort(
                key=lambda summary: summary.accuracy,
                reverse=True,
            )

            table = build_comparison_table(summaries)

    except ResultComparisonError as error:
        print_error("Error", str(error))
        raise typer.Exit(code=1) from error

    print_table(table)


@app.command("analyze-result")
def analyze_result_command(
    path: Path = typer.Argument(
        ...,
        help="Path to an exported benchmark result JSON file.",
    ),
) -> None:
    """Show detection failures and severity mismatches."""

    try:
        result = load_result(path)
        print_result_analysis(result)
    except ResultComparisonError as error:
        print_error("Error", str(error))
        raise typer.Exit(code=1) from error


@app.command("compare-runs")
def compare_runs_command(
    old_path: Path = typer.Argument(
        ...,
        help="Path to the older exported benchmark result JSON file.",
    ),
    new_path: Path = typer.Argument(
        ...,
        help="Path to the newer exported benchmark result JSON file.",
    ),
) -> None:
    """Compare benchmark-level changes between two exported runs."""

    try:
        old_result = load_result(old_path)
        new_result = load_result(new_path)

        comparison = compare_benchmark_results(old_result, new_result)

        print_run_comparison(
            old_result.summary,
            new_result.summary,
            comparison,
        )

    except ResultComparisonError as error:
        print_error("Error", str(error))
        raise typer.Exit(code=1) from error


@app.command("review-diff")
def review_diff_command(
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the review",
    ),
    prompt_version: str = typer.Option(
        DEFAULT_PROMPT_VERSION,
        "--prompt-version",
        help="Prompt version used for the diff review.",
    ),
) -> None:
    """Review the current unstaged Git diff."""
    try:
        diff = get_git_diff()

        if not diff.strip():
            print_warning("No changes to review")
            return

        changed_files = get_changed_python_files()
        current_code = build_changed_files_context(changed_files)

        result = review_diff(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

        print_review(review=result)
    except GitDiffError as exc:
        print_error("Git Diff Failed", str(exc))
        raise typer.Exit(code=1) from exc
    except (ValueError, RuntimeError) as exc:
        print_error("Diff Review Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark-diff")
def benchmark_diff_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the diff benchmark",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
    prompt_version: str = typer.Option(
        DEFAULT_PROMPT_VERSION,
        "--prompt-version",
        help="Prompt version used for the diff benchmark.",
    ),
) -> None:
    """Evaluate Git diff review using diff benchmark cases."""

    def review_with_model(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return review_diff(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

    try:
        benchmark_paths = find_diff_benchmarks(path)

        if not benchmark_paths:
            print_warning("No diff benchmark cases found.")
            return

        run = run_diff_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=prompt_version,
        )
        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / "diff" / prompt_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Diff Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("review-pr")
def review_pr_command(
    base: str = typer.Option(
        "main",
        "--base",
        help="Base branch or commit to compare against HEAD.",
    ),
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the review.",
    ),
    prompt_version: str = typer.Option(
        DEFAULT_PROMPT_VERSION,
        "--prompt-version",
        help="Prompt version used for the diff review.",
    ),
) -> None:
    """Review changes between a base ref and HEAD."""
    try:
        diff = get_git_diff_against(base)

        if not diff.strip():
            print_warning(f"No changes to review against {base}")
            return

        changed_files = get_changed_python_files_against(base)
        current_code = build_changed_files_context(changed_files)

        result = review_diff(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

        print_review(review=result)

    except GitDiffError as exc:
        print_error("PR Diff Failed", str(exc))
        raise typer.Exit(code=1) from exc

    except (ValueError, RuntimeError) as exc:
        print_error("PR Review Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("review-diff-candidates")
def review_diff_candidates_command(
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for candidate generation",
    ),
    prompt_version: str = typer.Option(
        "multipass_v1",
        "--prompt-version",
        help="Prompt version used for candidate generation.",
    ),
) -> None:
    """Find candidate issues in the current unstaged Git diff."""
    try:
        diff = get_git_diff()

        if not diff.strip():
            print_warning("No changes to review")
            return

        changed_files = get_changed_python_files()
        current_code = build_changed_files_context(changed_files)

        result = find_diff_candidates(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

        print_review(review=result)

    except GitDiffError as exc:
        print_error("Git Diff Failed", str(exc))
        raise typer.Exit(code=1) from exc
    except (ValueError, RuntimeError) as exc:
        print_error("Candidate Generation Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark-diff-candidates")
def benchmark_diff_candidates_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for candidate generation",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
    prompt_version: str = typer.Option(
        "multipass_v1",
        "--prompt-version",
        help="Prompt version used for candidate generation.",
    ),
) -> None:
    """Evaluate candidate generation using diff benchmark cases."""

    def review_with_model(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return find_diff_candidates(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

    try:
        benchmark_paths = find_diff_benchmarks(path)

        if not benchmark_paths:
            print_warning("No diff benchmark cases found.")
            return

        run = run_diff_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=prompt_version,
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / "diff" / prompt_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Candidate Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("review-diff-multi-pass")
def review_diff_multi_pass_command(
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the multi-pass review",
    ),
    prompt_version: str = typer.Option(
        "maintainability_v1",
        "--prompt-version",
        help="Prompt version used for the multi-pass review.",
    ),
) -> None:
    """Review the current unstaged Git diff using two LLM passes."""
    try:
        diff = get_git_diff()

        if not diff.strip():
            print_warning("No changes to review")
            return

        changed_files = get_changed_python_files()
        current_code = build_changed_files_context(changed_files)

        result = review_diff_multi_pass(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

        print_review(review=result)

    except GitDiffError as exc:
        print_error("Git Diff Failed", str(exc))
        raise typer.Exit(code=1) from exc
    except (TypeError, ValueError, RuntimeError) as exc:
        print_error("Multi-pass Review Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark-diff-multi-pass")
def benchmark_diff_multi_pass_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the multi-pass diff benchmark",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
    prompt_version: str = typer.Option(
        "maintainability_v1",
        "--prompt-version",
        help="Prompt version used for the multi-pass diff benchmark.",
    ),
) -> None:
    """Evaluate two-pass diff review using diff benchmark cases."""

    def review_with_model(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return review_diff_multi_pass(
            diff=diff,
            current_code=current_code,
            model=model,
            prompt_version=prompt_version,
        )

    try:
        benchmark_paths = find_diff_benchmarks(path)

        if not benchmark_paths:
            print_warning("No diff benchmark cases found.")
            return

        run = run_diff_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=prompt_version,
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / "diff" / prompt_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        NotADirectoryError,
        TypeError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Multi-pass Diff Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark-diff-specialized")
def benchmark_diff_specialized_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the specialized diff benchmark",
    ),
    prompt_version: str = typer.Option(
        "v11",
        "--prompt-version",
        help="General diff prompt version.",
    ),
    maintainability_prompt_version: str = typer.Option(
        "maintainability_v1",
        "--maintainability-prompt-version",
        help="Maintainability specialist prompt version.",
    ),
    maintainability_verifier_prompt_version: str | None = typer.Option(
        None,
        "--maintainability-verifier-prompt-version",
        help="Optional maintainability verifier prompt version.",
    ),
    context_size: int = typer.Option(
        4096,
        "--context-size",
        help="Ollama context window size.",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
) -> None:
    """Evaluate general + maintainability-specialist diff review."""

    general_prompt_version = prompt_version
    experiment_parts = [
        general_prompt_version,
        maintainability_prompt_version,
    ]

    if maintainability_verifier_prompt_version is not None:
        experiment_parts.append(maintainability_verifier_prompt_version)

    experiment_version = "+".join(experiment_parts)

    def review_with_model(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return review_diff_specialized(
            diff=diff,
            current_code=current_code,
            model=model,
            general_prompt_version=general_prompt_version,
            maintainability_prompt_version=maintainability_prompt_version,
            maintainability_verifier_prompt_version=maintainability_verifier_prompt_version,
            context_size=context_size,
        )

    try:
        benchmark_paths = find_diff_benchmarks(path)

        if not benchmark_paths:
            print_warning("No diff benchmark cases found.")
            return

        run = run_diff_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=experiment_version,
            inference=InferenceConfig(
                context_size=context_size,
            ),
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / "diff" / experiment_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        NotADirectoryError,
        TypeError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Specialized Diff Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


@app.command("benchmark-specialized")
def benchmark_specialized_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the specialized benchmark",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
) -> None:
    """Evaluate general + maintainability-specialist full-file review."""

    general_prompt_version = "v5"
    maintainability_prompt_version = "maintainability_file_v1"
    experiment_version = "v5+maintainability_file_v1"

    try:
        benchmark_paths = find_benchmark_files(path)

        if not benchmark_paths:
            print_warning("No benchmark files found.")
            return

        total = len(benchmark_paths)
        current = 0

        def review_with_model(
            source_path: Path,
        ) -> CodeReview:
            nonlocal current

            current += 1

            print_benchmark_progress(
                current=current,
                total=total,
                path=source_path,
            )

            return review_file_specialized(
                source_path,
                model=model,
                general_prompt_version=general_prompt_version,
                maintainability_prompt_version=maintainability_prompt_version,
            )

        run = run_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=experiment_version,
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / experiment_version / output

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        TypeError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Specialized Benchmark Failed", str(exc))
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()

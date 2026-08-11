from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reviewer.models import (
    BenchmarkResult,
    BenchmarkResultSummary,
    BenchmarkRun,
    CodeReview,
)
from reviewer.result_analysis import inspect_result
from reviewer.result_comparison import summarize_categories, summarize_rules

console = Console()


def print_benchmark_progress(
    current: int,
    total: int,
    path: Path,
) -> None:
    console.print(
        f"[bold cyan][{current:02d}/{total:02d}][/bold cyan] "
        f"[cyan]SCAN[/cyan] "
        f"[dim]{path}[/dim]"
    )


def print_review(review: CodeReview) -> None:
    if not review.issues:
        console.print("[green]No meaningful issues found.[/green]")
        return
    for issue in review.issues:
        console.print(f"[bold]{issue.title}[/bold]")
        console.print(f"[yellow]Severity:[/yellow] {issue.severity}")
        console.print(f"[magenta]Rule:[/magenta] {issue.rule}")
        console.print(f"[cyan]Category:[/cyan] {issue.category}")
        console.print(issue.explanation)
        console.print(f"[green]Recommendation:[/green] {issue.recommendation}")
        console.print()


def print_benchmark_evaluations(run: BenchmarkRun) -> None:
    """Render individual benchmark evaluation results."""

    console.print()
    console.rule("[bold cyan]Individual Results[/bold cyan]")

    for evaluation in run.evaluations:
        benchmark_name = evaluation.benchmark.name
        file_name = evaluation.benchmark.code_path.name

        if evaluation.passed:
            console.print(
                f"[bold green]PASS[/bold green] "
                f"{benchmark_name} "
                f"[dim]:: {file_name}[/dim]"
            )
            continue

        expected_rules = [issue.rule for issue in evaluation.benchmark.expected_issues]

        actual_rules = [issue.rule for issue in evaluation.review.issues]

        console.print(
            f"[bold red]FAIL[/bold red] "
            f"{benchmark_name} "
            f"[dim]:: {file_name}[/dim]"
        )

        console.print(
            "  [dim]Expected:[/dim] "
            f"{', '.join(expected_rules) if expected_rules else 'no issues'}"
        )

        console.print(
            "  [dim]Actual:[/dim]   "
            f"{', '.join(actual_rules) if actual_rules else 'no issues'}"
        )

        if evaluation.false_positive:
            console.print("  [yellow]↳ false positive[/yellow]")
        elif evaluation.false_negative:
            console.print("  [yellow]↳ false negative[/yellow]")
        elif not evaluation.rule_matched:
            console.print("  [red]↳ wrong rule[/red]")


def print_benchmark_failures(run: BenchmarkRun) -> None:
    """Render benchmark execution failures."""

    if not run.failures:
        return

    console.print()
    console.rule("[bold red]Execution Failures[/bold red]")

    for failure in run.failures:
        console.print(
            f"[bold red]ERROR[/bold red] "
            f"{failure.benchmark.name} "
            f"[dim]({failure.benchmark.code_path.name})[/dim]"
        )

        console.print(f"  [dim]Type:[/dim] {failure.error_type}")
        console.print(f"  [dim]Message:[/dim] {failure.message}")


def print_benchmark_summary(run: BenchmarkRun) -> None:
    """Render benchmark run summary."""

    table = Table(
        title="[bold cyan]Benchmark Complete[/bold cyan]",
        show_header=False,
        box=None,
    )

    table.add_column("Metric", style="dim")
    table.add_column("Value")

    table.add_row(
        "Model",
        f"[magenta]{run.model}[/magenta]",
    )
    table.add_row(
        "Prompt",
        f"[magenta]{run.prompt_version}[/magenta]",
    )
    table.add_row(
        "Benchmarks",
        str(run.benchmark_count),
    )
    table.add_row(
        "Passed",
        f"[green]{run.passed}[/green]",
    )
    table.add_row(
        "Failed",
        f"[red]{run.failed}[/red]",
    )
    table.add_row(
        "Errors",
        f"[red]{run.failure_count}[/red]",
    )
    table.add_row(
        "False positives",
        f"[yellow]{run.false_positives}[/yellow]",
    )
    table.add_row(
        "False negatives",
        f"[yellow]{run.false_negatives}[/yellow]",
    )
    table.add_row(
        "Accuracy",
        f"[bold cyan]{run.accuracy:.2%}[/bold cyan]",
    )
    table.add_row(
        "Severity",
        f"[cyan]{run.severity_matches}/"
        f"{run.severity_evaluated_count} "
        f"({run.severity_accuracy:.2%})[/cyan]",
    )
    table.add_row(
        "Duration",
        f"[dim]{run.duration_seconds:.2f}s[/dim]",
    )

    console.print()
    console.print(table)


def print_error(
    message: str,
    err: str | None = None,
) -> None:
    if err:
        console.print(f"[bold red]ERR[/bold red] " f"{message} [dim]::[/dim] {err}")
    else:
        console.print(f"[bold red]ERR[/bold red] {message}")


def print_warning(
    message: str,
    err: str | None = None,
) -> None:
    if err:
        console.print(
            f"[bold yellow]WARN[/bold yellow] " f"{message} [dim]::[/dim] {err}"
        )
    else:
        console.print(f"[bold yellow]WARN[/bold yellow] {message}")


def print_success(message: str) -> None:
    console.print(f"[bold green]OK[/bold green] {message}")


def print_result_saved(path: Path) -> None:
    console.print(f"\n[bold green]SAVED[/bold green] " f"[dim]{path}[/dim]")


def print_table(table: Table) -> None:
    console.print(table)


def print_review_progress(
    current: int,
    total: int,
    path: Path,
) -> None:
    console.print(
        f"[bold cyan][{current:02d}/{total:02d}][/bold cyan] "
        f"[cyan]REVIEW[/cyan] "
        f"[dim]{path}[/dim]"
    )


def build_comparison_table(
    summaries: list[BenchmarkResultSummary],
) -> Table:
    """Build a Rich table for benchmark result comparison."""

    table = Table(title="Model Comparison")

    table.add_column("Model")
    table.add_column("Prompt")
    table.add_column("Accuracy", justify="right")
    table.add_column("Severity", justify="right")
    table.add_column("Passed", justify="right")
    table.add_column("FP", justify="right")
    table.add_column("FN", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Time", justify="right")

    for summary in summaries:
        table.add_row(
            summary.model,
            summary.prompt_version,
            f"{summary.accuracy:.1%}",
            f"{summary.severity_accuracy:.1%}",
            str(summary.passed),
            str(summary.false_positives),
            str(summary.false_negatives),
            str(summary.errors),
            f"{summary.duration_seconds:.1f}s",
        )

    return table


def build_rule_comparison_table(results: list[BenchmarkResult]) -> Table:
    table = Table(title="Rule Comparison")

    table.add_column("Rule")

    for result in results:
        table.add_column(result.summary.model, justify="right")

    rules = sorted(
        {
            rule_summary.rule
            for result in results
            for rule_summary in summarize_rules(result.evaluations)
        }
    )

    summaries_by_model = {
        result.summary.model: {
            summary.rule: summary for summary in summarize_rules(result.evaluations)
        }
        for result in results
    }

    for rule in rules:
        row = [rule]

        for result in results:
            summary = summaries_by_model[result.summary.model].get(rule)

            if summary is None:
                row.append("-")
            else:
                row.append(
                    f"{summary.accuracy:.1%} "
                    f"({summary.passed}/{summary.benchmark_count})"
                )

        table.add_row(*row)

    return table


def build_category_comparison_table(
    results: list[BenchmarkResult],
) -> Table:
    table = Table(title="Category Comparison")

    table.add_column("Category")

    for result in results:
        table.add_column(
            result.summary.model,
            justify="right",
        )

    categories = sorted(
        {
            category_summary.category
            for result in results
            for category_summary in summarize_categories(result.evaluations)
        }
    )

    summaries_by_model = {
        result.summary.model: {
            summary.category: summary
            for summary in summarize_categories(result.evaluations)
        }
        for result in results
    }

    for category in categories:
        row = [category]

        for result in results:
            summary = summaries_by_model[result.summary.model].get(category)

            if summary is None:
                row.append("-")
            else:
                row.append(
                    f"{summary.accuracy:.1%} "
                    f"({summary.passed}/"
                    f"{summary.benchmark_count})"
                )

        table.add_row(*row)

    return table


def print_result_analysis(
    result: BenchmarkResult,
) -> None:
    """Render an exported benchmark result analysis."""
    problems = inspect_result(result)

    summary = result.summary

    summary_table = Table(
        title="Benchmark Result Analysis",
        show_header=False,
        box=None,
    )
    summary_table.add_column("Field", style="dim")
    summary_table.add_column("Value")

    summary_table.add_row(
        "Model",
        f"[magenta]{summary.model}[/magenta]",
    )
    summary_table.add_row(
        "Prompt",
        f"[magenta]{summary.prompt_version}[/magenta]",
    )
    summary_table.add_row(
        "Benchmarks",
        str(summary.benchmark_count),
    )
    summary_table.add_row(
        "Passed",
        f"[green]{summary.passed}[/green]",
    )
    summary_table.add_row(
        "Failed",
        f"[red]{summary.failed}[/red]",
    )
    summary_table.add_row(
        "Accuracy",
        f"[bold cyan]{summary.accuracy:.1%}[/bold cyan]",
    )
    summary_table.add_row(
        "Severity accuracy",
        f"[cyan]{summary.severity_accuracy:.1%}[/cyan]",
    )
    summary_table.add_row(
        "Execution time",
        f"[dim]{summary.duration_seconds:.1f}s[/dim]",
    )
    console.print(summary_table)

    if not problems:
        console.print(
            "\n[green]No detection failures or severity mismatches found.[/green]"
        )
        return

    for problem in problems:
        evaluation = problem.evaluation
        benchmark = evaluation.get("benchmark", {})
        review = evaluation.get("review", {})

        benchmark_name = benchmark.get("name", "Unknown benchmark")
        code_path = benchmark.get("code_path", "Unknown path")
        expected_issues = benchmark.get("expected_issues", [])
        actual_issues = review.get("issues", [])

        lines = [
            f"[bold]Benchmark:[/bold] [bold]{benchmark_name}[/bold]",
            f"[dim]Path: {code_path}[/dim]",
            "",
        ]

        if expected_issues:
            lines.append("[bold cyan]Expected[/bold cyan]")

            for issue in expected_issues:
                lines.extend(
                    [
                        f"  [dim]Rule:[/dim] {issue.get('rule', '-')}",
                        f"  [dim]Category:[/dim] {issue.get('category', '-')}",
                        f"  [dim]Severity:[/dim] {issue.get('severity', '-')}",
                    ]
                )
        else:
            lines.append("[bold cyan]Expected[/bold cyan] No issues")

        lines.append("")

        if actual_issues:
            lines.append("[bold magenta]Predicted[/bold magenta]")

            for issue in actual_issues:
                lines.extend(
                    [
                        f"  [dim]Rule:[/dim] {issue.get('rule', '-')}",
                        f"  [dim]Category:[/dim] {issue.get('category', '-')}",
                        f"  [dim]Severity:[/dim] {issue.get('severity', '-')}",
                        f"  [dim]Title:[/dim] {issue.get('title', '-')}",
                        f"  [dim]Explanation:[/dim] {issue.get('explanation', '-')}",
                    ]
                )
        else:
            lines.append("[bold magenta]Predicted[/bold magenta] No issues")

        console.print()
        if problem.problem_type.value == "false_positive":
            title = "[yellow]False Positive[/yellow]"
        elif problem.problem_type.value == "false_negative":
            title = "[yellow]False Negative[/yellow]"
        elif problem.problem_type.value == "severity_mismatch":
            title = "[magenta]Severity Mismatch[/magenta]"
        else:
            title = f"[red]{problem.problem_type.value.replace('_', ' ').title()}[/red]"
            
        console.print(
            Panel(
                "\n".join(lines),
                title=title,
                expand=False,
            )
        )

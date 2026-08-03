from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reviewer.models import BenchmarkResult, BenchmarkResultSummary, CodeReview
from reviewer.result_analysis import inspect_result
from reviewer.result_comparison import summarize_categories, summarize_rules

console = Console()



def print_benchmark_progress(
    current: int,
    total: int,
    path: Path,
) -> None:
    console.print(
        f"[bold cyan][{current:02d}/{total:02d}] SCAN[/bold cyan] "
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
    summary_table.add_column("Field", style="bold")
    summary_table.add_column("Value")

    summary_table.add_row("Model", summary.model)
    summary_table.add_row("Prompt", summary.prompt_version)
    summary_table.add_row(
        "Benchmarks",
        str(summary.benchmark_count),
    )
    summary_table.add_row("Passed", str(summary.passed))
    summary_table.add_row("Failed", str(summary.failed))
    summary_table.add_row(
        "Accuracy",
        f"{summary.accuracy:.1%}",
    )
    summary_table.add_row(
        "Severity accuracy",
        f"{summary.severity_accuracy:.1%}",
    )
    summary_table.add_row(
        "Execution time",
        f"{summary.duration_seconds:.1f}s",
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
            f"[bold]Type:[/bold] {problem.problem_type.value}",
            f"[bold]Benchmark:[/bold] {benchmark_name}",
            f"[bold]Path:[/bold] {code_path}",
            "",
        ]

        if expected_issues:
            lines.append("[bold]Expected:[/bold]")

            for issue in expected_issues:
                lines.extend(
                    [
                        f"  Rule: {issue.get('rule', '-')}",
                        f"  Category: {issue.get('category', '-')}",
                        f"  Severity: {issue.get('severity', '-')}",
                    ]
                )
        else:
            lines.append("[bold]Expected:[/bold] No issues")

        lines.append("")

        if actual_issues:
            lines.append("[bold]Predicted:[/bold]")

            for issue in actual_issues:
                lines.extend(
                    [
                        f"  Rule: {issue.get('rule', '-')}",
                        f"  Category: {issue.get('category', '-')}",
                        f"  Severity: {issue.get('severity', '-')}",
                        f"  Title: {issue.get('title', '-')}",
                        f"  Explanation: {issue.get('explanation', '-')}",
                    ]
                )
        else:
            lines.append("[bold]Predicted:[/bold] No issues")

        console.print()
        console.print(
            Panel(
                "\n".join(lines),
                title=problem.problem_type.value.replace("_", " ").title(),
                expand=False,
            )
        )
    
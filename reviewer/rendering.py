from rich.console import Console
from rich.table import Table

from reviewer.models import BenchmarkResult, BenchmarkResultSummary, CodeReview
from reviewer.result_comparison import summarize_categories, summarize_rules

console = Console()


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

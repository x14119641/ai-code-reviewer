# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants are designed by implementing each component step by step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation, controlled prompt experimentation, structured LLM outputs, and local execution.

## Roadmap

### Completed

- ✅ Review a single file
- ✅ Review multiple files
- ✅ Structured JSON output
- ✅ Benchmark runner
- ✅ Benchmark evaluation
- ✅ Benchmark result export
- ✅ Benchmark result comparison
- ✅ Rule comparison
- ✅ Category comparison
- ✅ Versioned prompt templates
- ✅ Benchmark result analysis
- ✅ Deterministic benchmark generation
- ✅ Rule-based severity normalization
- ✅ Controlled prompt optimization experiments
- ✅ Cross-run regression comparison
- ✅ Review local Git diffs
- ✅ Diff review with current source context

### Planned

- Review pull requests
- Continue benchmark and taxonomy expansion
- Diff-specific benchmarking
- HTML reports
- Agent mode

## Current Features

- Review individual Python files
- Review entire Python projects recursively
- Review local unstaged Git changes
- Combine Git diffs with current changed-file contents for contextual review
- Report issues introduced by a change rather than pre-existing issues
- Structured JSON responses from the LLM
- Response validation and parsing
- Versioned prompt templates
- Benchmark execution
- Automatic benchmark evaluation
- JSON export of benchmark results
- Compare aggregate benchmark results
- Compare models by rule
- Compare models by category
- Compare prompt versions
- Inspect benchmark failures and severity mismatches
- Compare individual benchmark behavior between two runs
- Detect fixed and regressed benchmark cases
- Detect benchmarks that remain failing
- Detect added and removed benchmark cases
- Deterministic LLM generation for reproducible experiments
- Rule-based severity normalization
- Controlled prompt optimization and comparison
- Local execution with Ollama

## Architecture

The reviewer supports both full-file review and Git-diff review while sharing the same parsing and structured review pipeline.

```text
                    ┌── Python File ────────────────┐
                    │                               ↓
CLI ────────────────┤                    Review Prompt Builder
                    │                               │
                    │                               │
                    └── Git Diff ───────────────────┤
                          +                         ↓
                     Changed Python Files    Diff Prompt Builder
                          │                         │
                          └── Current Source ───────┘
                                                    ↓
                                           Local LLM (Ollama)
                                                    ↓
                                         JSON Parsing / Validation
                                                    ↓
                                        Rule / Severity Normalization
                                                    ↓
                                          Structured CodeReview
```

Benchmark runs continue through the evaluation pipeline:

```text
Structured CodeReview
      ↓
Benchmark Evaluation
      ↓
Benchmark Serialization
      ↓
Result Comparison / Analysis
```

The main modules include:

```text
reviewer/
├── engine.py
├── git_diff.py
├── llm.py
├── prompts.py
├── models.py
├── taxonomy.py
├── benchmarks.py
├── benchmark_runner.py
├── benchmark_evaluator.py
├── benchmark_serialization.py
├── benchmark_comparison.py
├── result_comparison.py
└── rendering.py
```

The application keeps Git integration, LLM execution, prompt construction,
benchmark evaluation, experiment comparison, and CLI rendering separate so
each part can be tested and evolved independently.

## Benchmark Workflow

The benchmarking workflow is designed to support iterative prompt engineering and model evaluation.

```text
Review Code
      ↓
Run Benchmarks
      ↓
Export Benchmark Results
      ↓
Compare Models / Prompt Versions
      ↓
Inspect Failures
      ↓
Compare Runs for Regressions
      ↓
Improve Prompt / Taxonomy
      ↓
Repeat
```

This makes prompt iterations measurable and reproducible rather than relying on subjective impressions.

Aggregate metrics show whether a run improved overall, while cross-run comparison shows exactly which benchmark cases changed.

## Benchmarks

The project currently contains a **65-case benchmark suite** designed to test both detection ability and false-positive boundaries.

Benchmarks are deliberately built from positive, negative, and boundary cases rather than only obvious examples.

Each benchmark contains:

* A Python source file
* The expected findings
* Expected rule, category, and severity
* Automatic evaluation against the model response
* False-positive and false-negative detection

Current benchmark categories and rules include:

| Category        | Rules                                                   |
| --------------- | ------------------------------------------------------- |
| Bug             | Mutable default argument, Unreachable code              |
| Security        | SQL injection, Shell injection, Path traversal          |
| Performance     | List membership in loops, String concatenation in loops |
| Maintainability | Duplicate code, Long function                           |

Safe and boundary cases are included throughout the rule families to measure false positives.

Examples include parameterized SQL queries, allowlisted paths and commands, immutable default arguments, set and dictionary membership, `join()`-based string construction, shared helper functions, and valid control flow.

Benchmark runs can be exported as JSON and compared across different models and prompt versions.

Results include:

* Overall accuracy
* Severity accuracy
* False positives
* False negatives
* Response failures
* Rule-level comparison
* Category-level comparison
* Execution time
* Cross-run fixes and regressions

Detailed result inspection can identify:

* False positives
* False negatives
* Rule mismatches
* Category mismatches
* Severity mismatches

## Prompt Templates

Prompt templates are versioned independently from the application code.

Different review modes can use separate templates within the same prompt version:

```text
prompts/
├── v1/
│   └── review.txt
├── ...
├── v8/
│   └── diff.txt
└── v9/
    └── diff.txt
```

Full-file review prompts use the Python source code as input.

Diff-review prompts use both the Git diff and the current contents of changed
Python files. The diff identifies what changed, while the current source
provides the context needed to reason about the behavior of the new version.

Existing prompt versions remain frozen so previous experiments can be
reproduced and compared.

Each benchmark run records the prompt version used, allowing direct comparison
between prompt revisions without modifying historical prompts.

## Prompt Evaluation

Prompt changes are evaluated against benchmark suites using controlled generation settings.

Early Qwen 3.5 9B experiments on the original 35-case benchmark suite produced:

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| ------ | -------: | -----: | --------------: | --------------: |
| v1     |    85.7% |  30/35 |               4 |               1 |
| v2     |    88.6% |  31/35 |               3 |               1 |
| v3     |    88.6% |  31/35 |               3 |               1 |
| v4     |    91.4% |  32/35 |               2 |               1 |

These experiments showed that explicit rule-specific detection boundaries were more effective than increasingly generic instructions such as asking the model to be more careful about false positives.

The benchmark suite was subsequently expanded from 35 to 65 cases to test generalization and more difficult rule boundaries.

A recent Qwen 3.5 9B run using prompt v5 produced:

```text
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
Execution time    145.7s
```

Prompt v5 introduced the `unreachable_code` rule while retaining the existing taxonomy.

Severity is normalized deterministically from the detected rule instead of trusting the severity generated by the LLM. This currently produces **100% severity accuracy** when the expected rule and category are correctly detected.

## Cross-Run Regression Comparison

Aggregate accuracy can hide important behavior changes.

For example, a new prompt may improve overall accuracy while simultaneously breaking a benchmark that previously passed.

The `compare-runs` command compares two exported benchmark runs at the individual benchmark level:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

The comparison reports:

* **Fixed** — failed in the old run and passes in the new run
* **Regressed** — passed in the old run and fails in the new run
* **Still failing** — fails in both runs
* **Added** — exists only in the new benchmark run
* **Removed** — exists only in the old benchmark run

Example:

```text
Old: v4 / qwen3.5:9b — 53/60 (88.3%)
New: v5 / qwen3.5:9b — 60/65 (92.3%)

Comparable: 60 | Fixed: 3 | Regressed: 1 | Still failing: 4 | Added: 5 | Removed: 0

Fixed
✓ benchmarks/maintainability/duplicate_code/shared_helper_safe.py
✓ benchmarks/maintainability/duplicate_code/shared_validation_helper_safe.py
✓ benchmarks/performance/list_membership_in_loop/dict_key_membership_safe.py

Regressed
✗ benchmarks/security/path_traversal/user_absolute_path.py
```

This makes prompt regressions visible even when aggregate benchmark accuracy improves.

### `compare-results` vs `compare-runs`

The two commands answer different questions:

* `compare-results` compares aggregate performance across benchmark result files.
* `compare-runs` compares benchmark-by-benchmark changes between two specific runs.

## Models

The project focuses on models that can run locally on consumer hardware with 12 GB of VRAM.

Current benchmarked models:

| Model                 | Purpose                                   |
| --------------------- | ----------------------------------------- |
| Qwen 3.5 9B           | Main model for current prompt experiments |
| Qwen 2.5 Coder 7B     | Fast coding-specialized model             |
| Qwen 2.5 Coder 14B    | Larger coding-specialized model           |
| DeepSeek Coder V2 16B | Advanced coding and reasoning model       |
| Llama 3.1 8B          | General-purpose reference model           |
| Gemma 3 12B           | Google's open-weight general model        |

Additional models and quantizations may be added as the project evolves.

## Tech Stack

* Python 3.14
* uv
* Typer
* Rich
* pytest
* Ruff
* Ollama
* Local open-weight LLMs

## Test Environment

* AMD Radeon RX 6700 XT (12 GB VRAM)
* Arch Linux

## Run

### Show available commands

```bash
uv run python main.py --help
```

### Review a single file

```bash
uv run python main.py review examples/user_lookup.py
```

### Review an entire folder

```bash
uv run python main.py review-folder examples
```

### Run the benchmark suite

```bash
uv run python main.py benchmark benchmarks/
```

### Benchmark using a different model

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen2.5-coder:14b
```

### Benchmark using a specific prompt version

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5
```

### Export benchmark results

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5 \
    --output results/v5/qwen3.5-9b-seed42.json
```

### Compare aggregate benchmark results

```bash
uv run python main.py compare-results results/v5/
```

### Compare benchmark results by rule

```bash
uv run python main.py compare-results results/v5/ --by-rule
```

### Compare benchmark results by category

```bash
uv run python main.py compare-results results/v5/ --by-category
```

### Inspect an exported benchmark result

```bash
uv run python main.py analyze-result \
    results/v5/qwen3.5-9b-seed42.json
```

### Compare two benchmark runs for regressions

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

### Review current Git changes

Review the current unstaged Git diff:

```bash
uv run python main.py review-diff --prompt-version v9
```

The diff reviewer combines the Git diff with the current contents of changed
Python files. This allows the model to detect issues introduced indirectly by
a change, including cases where the affected line itself was not modified.

For example, changing a lookup collection from a dictionary to a list can make
an unchanged membership check inside a loop inefficient.

## Project Goal

This project is primarily an AI engineering learning environment.

The objective is not only to produce useful code reviews, but to understand the engineering behind LLM-based developer tools:

* Structured LLM output
* Prompt design and versioning
* Deterministic generation
* Evaluation datasets
* False-positive and false-negative analysis
* Model comparison
* Prompt regression detection
* Taxonomy design
* Reproducible experimentation
* Diff-aware code review
* Context construction for LLM code analysis
* Local LLM inference

The reviewer is intentionally being developed incrementally so each new capability can be evaluated before adding more complexity.

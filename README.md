# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants are designed by implementing each component step by step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation, controlled prompt experimentation, structured LLM outputs, diff-aware review, change attribution, and local execution.

## Roadmap

### Completed

* ✅ Review a single file
* ✅ Review multiple files
* ✅ Structured JSON output
* ✅ Benchmark runner
* ✅ Benchmark evaluation
* ✅ Benchmark result export
* ✅ Benchmark result comparison
* ✅ Rule comparison
* ✅ Category comparison
* ✅ Versioned prompt templates
* ✅ Benchmark result analysis
* ✅ Deterministic benchmark generation
* ✅ Rule-based severity normalization
* ✅ Controlled prompt optimization experiments
* ✅ Cross-run regression comparison
* ✅ Review local Git diffs
* ✅ Diff review with current source context
* ✅ Diff-specific benchmark format
* ✅ Diff benchmark discovery and loading
* ✅ Diff benchmark runner
* ✅ Diff benchmark CLI
* ✅ Diff benchmark result rendering
* ✅ Diff benchmark result export
* ✅ Diff benchmark coverage across all current taxonomy rules
* ✅ Diff change-attribution experiments
* ✅ Cross-run comparison for diff benchmarks
* ✅ Review committed branch changes against a base ref

### Planned

* Continue full-file benchmark and taxonomy expansion
* Evaluate diff prompts across additional local models
* Improve maintainability-rule recall
* HTML reports
* Agent / multi-pass review mode

## Current Features

* Review individual Python files
* Review entire Python projects recursively
* Review local unstaged Git changes
* Review committed branch changes against a base branch or commit
* Combine Git diffs with current changed-file contents for contextual review
* Focus diff reviews on issues introduced or worsened by a change
* Structured JSON responses from the LLM
* Response validation and parsing
* Versioned prompt templates
* Full-file benchmark execution
* Diff-specific benchmark execution
* Automatic benchmark evaluation
* JSON export of full-file and diff benchmark results
* Compare aggregate benchmark results
* Compare models by rule
* Compare models by category
* Compare prompt versions
* Inspect benchmark failures and severity mismatches
* Compare individual benchmark behavior between two runs
* Cross-run comparison for both full-file and diff benchmarks
* Detect fixed and regressed benchmark cases
* Detect benchmarks that remain failing
* Detect added and removed benchmark cases
* Deterministic LLM generation for reproducible experiments
* Rule-based severity normalization
* Controlled prompt optimization and comparison
* Local execution with Ollama

## Architecture

The reviewer supports full-file review, working-tree diff review, and committed branch comparison while sharing the same LLM, parsing, normalization, and structured review pipeline.

```text
                         ┌── Python File ────────────────┐
                         │                               ↓
CLI ─────────────────────┤                    Review Prompt Builder
                         │                               │
                         │                               │
                         ├── Working-Tree Git Diff ──────┤
                         │                               │
                         └── Base...HEAD Git Diff ───────┤
                                  +                      ↓
                           Changed Python Files    Diff Prompt Builder
                                  │                      │
                                  └── Current Source ────┘
                                                         ↓
                                                Local LLM (Ollama)
                                                         ↓
                                              JSON Parsing / Validation
                                                         ↓
                                             Rule / Severity Normalization
                                                         ↓
                                               Structured CodeReview
```

The Git integration supports two sources of changes:

```text
review-diff
    ↓
git diff
    ↓
current unstaged changes


review-pr --base <ref>
    ↓
git diff <base>...HEAD
    ↓
committed branch changes
```

Both feed the same diff-review pipeline.

Both review modes can continue through an evaluation pipeline:

```text
Structured CodeReview
      ↓
Benchmark Evaluation
      ↓
Benchmark Run
      ↓
Benchmark Serialization
      ↓
Result Comparison / Analysis
```

Diff benchmarks add an additional layer before evaluation:

```text
Diff Benchmark Directory
        ↓
before.py + after.py + benchmark.json
        ↓
Load DiffBenchmark
        ↓
Generate Unified Diff
        +
Current after.py Source
        ↓
Diff Review
        ↓
Benchmark Evaluation
        ↓
BenchmarkRun
```

The main modules include:

```text
reviewer/
├── engine.py
├── git_diff.py
├── benchmark_diff.py
├── diff_benchmark_runner.py
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
benchmark loading, benchmark execution, evaluation, experiment comparison,
serialization, and CLI rendering separate so each part can be tested and
evolved independently.

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

## Full-File Benchmarks

The project currently contains a **65-case full-file benchmark suite** designed to test both detection ability and false-positive boundaries.

Benchmarks are deliberately built from positive, negative, and boundary cases rather than only obvious examples.

Each full-file benchmark contains:

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

The current Qwen 3.5 9B full-file baseline uses prompt v5:

```text
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
```

`long_function` remains one of the weakest full-file rules.

A targeted prompt investigation tested increasingly explicit responsibility definitions but did not improve detection. Further tuning of that rule was paused to avoid benchmark-specific overfitting.

## Diff Benchmarks

Git-diff review has a separate benchmark format because evaluating a change is different from evaluating a complete source file.

A diff benchmark is represented by a directory containing:

```text
benchmark_case/
├── before.py
├── after.py
└── benchmark.json
```

`before.py` represents the code before the change.

`after.py` represents the current source after the change.

The benchmark system generates the diff between the two versions and sends both the generated diff and the current `after.py` source to the diff reviewer.

`benchmark.json` defines the expected issues introduced by the change.

Example:

```json
{
  "name": "Dict to list introduces membership in loop",
  "before_path": "before.py",
  "after_path": "after.py",
  "expected_issues": [
    {
      "severity": "medium",
      "rule": "list_membership_in_loop",
      "category": "performance",
      "explanation": "Changing the lookup collection from a dict to a list introduces linear membership checks inside the loop."
    }
  ]
}
```

Diff benchmarks test more than whether the model can recognize a problem.

They also test **change attribution**:

> Did the diff introduce or worsen the issue, or was the issue already present before the change?

A useful diff reviewer should not report every problem visible in the current file. It should focus on problems caused by the proposed change.

### Current Diff Benchmark Suite

The suite has expanded from the original 11 cases to **21 cases covering all nine rules in the current taxonomy**.

| Category        | Rule                          |  Cases |
| --------------- | ----------------------------- | -----: |
| Bug             | Mutable default argument      |      2 |
| Bug             | Unreachable code              |      2 |
| Security        | SQL injection                 |      2 |
| Security        | Shell injection               |      2 |
| Security        | Path traversal                |      2 |
| Performance     | List membership in loops      |      3 |
| Performance     | String concatenation in loops |      2 |
| Maintainability | Duplicate code                |      3 |
| Maintainability | Long function                 |      3 |
| **Total**       |                               | **21** |

The suite includes:

* introduced issues
* safe changes
* pre-existing issues
* changes affecting unchanged code
* stronger diagnostic maintainability cases

Examples include:

```text
dict → list
→ introduces expensive membership checks
→ report the performance issue

pre-existing list membership + local rename
→ issue existed before the diff
→ report nothing

None default → []
→ introduces mutable default argument
→ report the bug

pre-existing mutable default + local rename
→ issue existed before the diff
→ report nothing

parameterized SQL → interpolated SQL
→ introduces SQL injection
→ report the security issue

pre-existing SQL injection + unrelated logging change
→ vulnerable SQL construction is unchanged
→ report nothing
```

### Diff Prompt Evolution

The first expanded baseline used prompt v9:

```text
Prompt           v9
Benchmarks       21
Passed           15
Failed            6
False positives   3
False negatives   3
Accuracy         71.43%
Severity          8/8 (100.00%)
```

The main weakness was attribution of highly visible pre-existing issues.

Prompt v10 tested stronger generic before/after attribution instructions:

```text
Prompt           v10
Benchmarks       21
Passed           15
Failed            6
False positives   2
False negatives   4
Accuracy         71.43%
Severity          7/7 (100.00%)
```

v10 fixed pre-existing mutable-default attribution but continued to misattribute pre-existing SQL and shell injection.

It also regressed a strong `duplicate_code` case.

Prompt v11 instead uses more concrete attribution guidance.

Before reporting a finding, the model is instructed to identify the actual triggering code and compare it between the previous and current versions.

The central attribution rule is:

```text
triggering code unchanged
        +
diff changes unrelated surrounding behavior
        ↓
pre-existing issue
        ↓
do not report
```

This successfully fixed the remaining security attribution cases.

### Current Diff Baseline

The current Qwen 3.5 9B diff baseline uses **prompt v11**:

```text
Benchmarks       21
Passed           17
Failed            4
Errors            0
False positives   0
False negatives   4
Accuracy         80.95%
Severity          7/7 (100.00%)
```

This is the strongest diff-review result so far.

Comparison:

| Prompt  |    Passed |   Accuracy | False Positives | False Negatives |
| ------- | --------: | ---------: | --------------: | --------------: |
| v9      |     15/21 |     71.43% |               3 |               3 |
| v10     |     15/21 |     71.43% |               2 |               4 |
| **v11** | **17/21** | **80.95%** |           **0** |           **4** |

Compared with v9, v11 fixes:

```text
pre-existing mutable_default_argument
pre-existing shell_injection
pre-existing sql_injection
```

and regresses:

```text
strong duplicate_code positive
```

The remaining four false negatives are:

```text
duplicate_code positive
duplicate_code strong positive
long_function positive
long_function strong positive
```

All current pre-existing attribution boundary cases pass under v11.

The remaining weaknesses are therefore concentrated in maintainability-rule recognition rather than change attribution.

## Prompt Templates

Prompt templates are versioned independently from the application code.

Different review modes can use separate templates within the same prompt version:

```text
prompts/
├── v1/
│   └── review.txt
├── ...
├── v5/
│   └── review.txt
├── ...
├── v9/
│   └── diff.txt
├── v10/
│   └── diff.txt
└── v11/
    └── diff.txt
```

Full-file review prompts use the Python source code as input.

Diff-review prompts use both the Git diff and the current contents of changed Python files.

The diff identifies what changed, while the current source provides the context needed to reason about the behavior of the new version.

The current baselines are:

```text
Full-file review    v5
Git-diff review     v11
```

Existing prompt versions remain frozen so previous experiments can be reproduced and compared.

Each benchmark run records the prompt version used, allowing direct comparison between prompt revisions without modifying historical prompts.

## Prompt Evaluation

Prompt changes are evaluated against benchmark suites using controlled generation settings.

Early Qwen 3.5 9B experiments on the original 35-case full-file benchmark suite produced:

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| ------ | -------: | -----: | --------------: | --------------: |
| v1     |    85.7% |  30/35 |               4 |               1 |
| v2     |    88.6% |  31/35 |               3 |               1 |
| v3     |    88.6% |  31/35 |               3 |               1 |
| v4     |    91.4% |  32/35 |               2 |               1 |

The full-file suite was subsequently expanded from 35 to 65 cases.

Prompt v5 currently produces:

```text
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
```

Diff prompt experiments are evaluated independently.

The current v11 diff result is:

```text
Benchmarks         21
Passed             17
Failed              4
Accuracy           80.95%
False positives     0
False negatives     4
Severity accuracy 100.0%
```

Severity is normalized deterministically from the detected rule instead of trusting the severity generated by the LLM.

## Cross-Run Regression Comparison

Aggregate accuracy can hide important behavior changes.

The `compare-runs` command compares two exported benchmark runs at the individual benchmark level.

It supports both full-file and diff benchmark results.

Full-file example:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

Diff example:

```bash
uv run python main.py compare-runs \
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

The comparison reports:

* **Fixed** — failed in the old run and passes in the new run
* **Regressed** — passed in the old run and fails in the new run
* **Still failing** — fails in both runs
* **Added** — exists only in the new benchmark run
* **Removed** — exists only in the old benchmark run

The v9 → v11 diff comparison produced:

```text
Old: v9 / qwen3.5:9b — 15/21 (71.4%)
New: v11 / qwen3.5:9b — 17/21 (81.0%)

Comparable: 21 | Fixed: 3 | Regressed: 1 | Still failing: 3 | Added: 0 | Removed: 0

Fixed
✓ pre-existing mutable default
✓ pre-existing shell injection
✓ pre-existing SQL injection

Regressed
✗ strong duplicate-code positive

Still failing
• duplicate-code positive
• long-function positive
• strong long-function positive
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

### Review current Git changes

Review the current unstaged Git diff:

```bash
uv run python main.py review-diff \
    --model qwen3.5:9b \
    --prompt-version v11
```

The diff reviewer combines the Git diff with the current contents of changed Python files.

This allows the model to detect issues introduced indirectly by a change, including cases where the affected line itself was not modified.

### Review committed branch changes

Review the committed changes between a base branch or commit and `HEAD`:

```bash
uv run python main.py review-pr \
    --base main \
    --model qwen3.5:9b
```

Internally this reviews:

```text
git diff main...HEAD
```

The command reuses the existing v11 diff-review pipeline.

It does not require a separate PR-specific prompt or benchmark format.

This makes it useful for reviewing feature-branch changes before opening or merging a pull request.

### Run the full-file benchmark suite

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

### Export full-file benchmark results

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5 \
    --output qwen3.5-9b-seed42.json
```

### Run the diff benchmark suite

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v11
```

A specific rule family can also be evaluated independently:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks/security/sql_injection \
    --model qwen3.5:9b \
    --prompt-version v11
```

### Export diff benchmark results

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v11 \
    --output qwen3.5-9b.json
```

Diff results are stored separately from full-file results:

```text
results/
├── v1/
├── v2/
├── ...
└── diff/
    ├── v9/
    ├── v10/
    └── v11/
        └── qwen3.5-9b.json
```

Keeping diff results separate prevents fundamentally different benchmark suites from being accidentally mixed.

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
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

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
* Change attribution
* Context construction for LLM code analysis
* Git branch comparison
* Local LLM inference

The reviewer is intentionally being developed incrementally so each new capability can be evaluated before adding more complexity.

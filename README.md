# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants are designed by implementing each component step by step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation, controlled prompt experimentation, and local execution to better understand how AI-assisted code review tools are built.

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
* ✅ Controlled prompt optimization experiments

### Planned

* Review Git diffs
* Review pull requests
* Compare benchmark suites
* HTML reports
* Agent mode

## Current Features

* Review individual Python files
* Review entire Python projects recursively
* Structured JSON responses from the LLM
* Response validation and parsing
* Versioned prompt templates
* Benchmark execution
* Automatic benchmark evaluation
* JSON export of benchmark results
* Compare benchmark result files
* Compare models by rule
* Compare models by category
* Compare prompt versions
* Inspect benchmark failures and severity mismatches
* Deterministic benchmark generation for reproducible experiments
* Rule-based severity normalization
* Controlled prompt optimization and comparison
* Local execution with Ollama

## Architecture

The reviewer follows a modular pipeline:

```text
Python File
      ↓
Versioned Prompt Template
      ↓
Prompt Builder
      ↓
Local LLM (Ollama)
      ↓
JSON Validation
      ↓
Taxonomy Normalization
      ↓
Structured Review
      ↓
Benchmark Evaluation
      ↓
JSON Benchmark Report
```

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
Improve Prompt
      ↓
Repeat
```

This makes prompt iterations measurable and reproducible rather than relying on subjective impressions.

## Benchmarks

The project includes a growing benchmark suite used to evaluate the quality of local LLM code reviews.

Each benchmark contains:

* A Python source file
* The expected findings (rule, category, severity)
* Automatic evaluation against the model response
* False-positive and false-negative detection

Current benchmark categories include:

| Category        | Rules                                                   |
| --------------- | ------------------------------------------------------- |
| Bug             | Mutable default arguments                               |
| Security        | SQL injection, Shell injection, Path traversal          |
| Performance     | List membership in loops, String concatenation in loops |
| Maintainability | Duplicate code, Long functions                          |
| False Positives | Safe implementations that should not trigger findings   |

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

The project also provides detailed result inspection to help understand benchmark failures, including:

* False positives
* False negatives
* Rule mismatches
* Category mismatches
* Severity mismatches

This analysis is intended to support prompt iteration and model comparison.

## Prompt Templates

Prompt templates are versioned independently from the application code.

```text
prompts/
├── v1/
│   └── prompt1.txt
├── v2/
│   └── prompt1.txt
├── v3/
│   └── prompt1.txt
└── v4/
    └── prompt1.txt
```

Each benchmark run records the prompt version used, allowing direct comparison between prompt revisions without modifying the application code.

Benchmark generation uses controlled settings (`temperature=0` and a fixed seed) to reduce run-to-run variance during prompt experiments.

## Prompt Evaluation

Prompt changes are evaluated against the same benchmark suite using controlled generation settings.

For Qwen 3.5 9B, the prompt iterations produced:

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| ------ | -------- | ------ | --------------- | --------------- |
| v1     | 85.7%    | 30/35  | 4               | 1               |
| v2     | 88.6%    | 31/35  | 3               | 1               |
| v3     | 88.6%    | 31/35  | 3               | 1               |
| v4     | 91.4%    | 32/35  | 2               | 1               |

The experiments showed that making rule-specific detection boundaries explicit was more effective than adding increasingly general instructions to avoid false positives.

The current v4 prompt reaches 91.4% accuracy on the 35-case benchmark suite. Severity is derived deterministically from the detected rule and reaches 100% accuracy for correctly detected benchmark issues.

## Models

The project focuses on models that can run comfortably on a 12 GB GPU.

Current benchmarked models:

| Model                 | Purpose                             |
| --------------------- | ----------------------------------- |
| Qwen 3.5 9B           | General-purpose baseline            |
| Qwen 2.5 Coder 7B     | Fast coding-specialized model       |
| Qwen 2.5 Coder 14B    | Larger coding-specialized model     |
| DeepSeek Coder V2 16B | Advanced coding and reasoning model |
| Llama 3.1 8B          | General-purpose reference model     |
| Gemma 3 12B           | Google's open-weight general model  |

Additional models and quantizations may be added as the project evolves.

## Tech Stack

* Python
* uv
* Typer
* Rich
* Ollama
* Local open-weight LLMs

## Test Environment

* AMD Radeon RX 6700 XT (12 GB VRAM)
* Arch Linux

## Run

```bash
# Show available commands
uv run python main.py --help

# Review a single file
uv run python main.py review examples/user_lookup.py

# Review an entire folder
uv run python main.py review-folder examples

# Run the benchmark suite
uv run python main.py benchmark benchmarks/

# Benchmark using a different model
uv run python main.py benchmark benchmarks/ \
    --model qwen2.5-coder:14b

# Benchmark using a specific prompt version
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v4

# Export benchmark results
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v4 \
    --output results/v4/qwen3.5-9b-seed42.json

# Compare benchmark results
uv run python main.py compare-results results/v1/

# Compare benchmark results by rule
uv run python main.py compare-results results/v1/ --by-rule

# Compare benchmark results by category
uv run python main.py compare-results results/v1/ --by-category

# Inspect an exported benchmark result
uv run python main.py analyze-result results/v4/qwen3.5-9b-seed42.json
```

# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants work by implementing each part step by step. Everything runs locally using open-weight models and Ollama.

The project emphasizes modular design, reproducible evaluation, and local execution to better understand how AI-assisted code review tools are built.

## Roadmap

### Completed

- ✅ Review a single file
- ✅ Review multiple files
- ✅ Structured JSON output
- ✅ Benchmark runner
- ✅ Benchmark evaluation
- ✅ Benchmark result export
- ✅ Benchmark result comparison

### Planned

- Review Git diffs
- Review pull requests
- Prompt benchmarking
- Compare benchmark suites
- HTML reports
- Agent mode

## Current Features

- Review individual Python files
- Review entire Python projects recursively
- Structured JSON responses from the LLM
- Response validation and parsing
- Benchmark execution
- Automatic benchmark evaluation
- JSON export of benchmark results
- Compare benchmark result files
- Local execution with Ollama

## Architecture

The reviewer follows a modular pipeline:

```text
Python File
      ↓
Prompt Builder
      ↓
Local LLM (Ollama)
      ↓
JSON Validation
      ↓
Structured Review
      ↓
Benchmark Evaluation
      ↓
JSON Benchmark Report
```

## Benchmarks

The project includes a growing benchmark suite used to evaluate the quality of local LLM code reviews.

Each benchmark contains:

- A Python source file
- The expected findings (rule, category, severity)
- Automatic evaluation against the model response
- False-positive and false-negative detection

Current benchmark categories include:

| Category        | Rules                                                   |
| --------------- | ------------------------------------------------------- |
| Bug             | Mutable default arguments                               |
| Security        | SQL injection, Shell injection, Path traversal          |
| Performance     | List membership in loops, String concatenation in loops |
| Maintainability | Duplicate code, Long functions                          |
| False Positives | Safe implementations that should not trigger findings   |

Benchmark runs can be exported as JSON and compared later across different models, prompts, and benchmark suites.

Results include:

- Accuracy
- False positives
- False negatives
- Response failures
- Execution time

## Models

The project focuses on models that can run comfortably on a 12 GB GPU.

Current models to compare:

| Model              | Purpose                   |
| ------------------ | ------------------------- |
| Qwen 3.5 9B        | General-purpose baseline  |
| Qwen 2.5 Coder 14B | Coding-specialized model  |
| Gemma 3 12B        | Alternative general model |
| DeepSeek R1 8B     | Reasoning-focused model   |

Additional models and quantizations may be added as the project evolves.

## Tech Stack

- Python
- uv
- Typer
- Rich
- Ollama
- Local open-weight LLMs

## Test Environment

- AMD Radeon RX 6700 XT (12 GB VRAM)
- Arch Linux

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

# Select a different model
uv run python main.py benchmark benchmarks/ --model qwen2.5-coder:14b

# Export benchmark results
uv run python main.py benchmark benchmarks/ \
    --output results/qwen2.5-coder-7b.json

# Export results using another model
uv run python main.py benchmark benchmarks/ \
    --model qwen2.5-coder:14b \
    --output results/qwen2.5-coder-14b.json

# Compare exported benchmark results
uv run python main.py compare-results results/
```

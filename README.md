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
- ✅ Benchmark framework

### Planned

- Review Git diffs
- Review pull requests
- Compare local models
- Prompt benchmarking
- Agent mode

## Current Features

- Review individual Python files
- Review entire Python projects
- Structured JSON responses from the LLM
- Response validation
- Benchmark runner
- Benchmark evaluation
- Local execution with Ollama

## Architecture

The reviewer follows a simple pipeline:

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
```

## Benchmarks

The project includes a growing benchmark suite containing curated Python examples and their expected findings.

Current benchmark cases include:

- SQL Injection
- Shell Injection
- Path Traversal
- Mutable Default Arguments
- False Positive Detection

The benchmark suite is used to evaluate prompts and compare local LLMs.

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
```

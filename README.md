# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants work by implementing each part step by step. Everything runs locally using open-weight models and Ollama.

## Roadmap

- **Review a single file**  
  Read a Python file and generate a code review.

- **Review multiple files**  
  Analyze an entire folder and produce a combined report.

- **Review Git diffs**  
  Focus only on the lines changed in a commit or patch.

- **Review pull requests**  
  Review complete changes before they are merged.

- **Compare local models**  
  Benchmark different local coding models on the same tasks.

- **Improve prompts**  
  Experiment with prompt engineering to reduce false positives and improve review quality.

- **Agent mode**  
  Turn the reviewer into an agent capable of planning and performing more complex review tasks.

## Models

The project focuses on models that can run comfortably on a 12 GB GPU.

Current models to compare:

| Model | Purpose |
|--------|---------|
| Qwen 3.5 9B | General-purpose baseline |
| Qwen 2.5 Coder 14B | Coding-specialized model |
| Gemma 3 12B | Alternative general model |
| DeepSeek R1 8B | Reasoning-focused model |

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
uv run python main.py --help
```
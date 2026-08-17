from typing import Any

import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
REVIEW_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "security",
                            "bug",
                            "performance",
                            "maintainability",
                        ],
                    },
                    "rule": {
                        "type": "string",
                        "enum": [
                            "sql_injection",
                            "shell_injection",
                            "path_traversal",
                            "mutable_default_argument",
                            "unreachable_code",
                            "duplicate_code",
                            "long_function",
                            "list_membership_in_loop",
                            "string_concatenation_in_loop",
                        ],
                    },
                    "title": {"type": "string"},
                    "explanation": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": [
                    "severity",
                    "category",
                    "rule",
                    "title",
                    "explanation",
                    "recommendation",
                ],
            },
        }
    },
    "required": ["issues"],
}


def generate_review(
    prompt: str,
    model: str = "qwen3.5:9b",
    *,
    output_format: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "seed": 42,
        },
    }

    if output_format is not None:
        payload["format"] = output_format

    try:
        response = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        review = data.get("response")
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not communicate with Ollama: {exc}") from exc

    if not isinstance(review, str):
        raise TypeError("Ollama returned unexpected response.")
    return review.strip()

from typing import Any

import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

def generate_review(
    prompt:str,
    model:str="qwen3.5:9b",
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature":0,
            "seed": 42,
        }
    }
    
    try:
        response= requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
            
        review = data.get("response")
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not communicat with Ollama: {exc}") from exc
    
    
    if not isinstance(review, str):
        raise TypeError("Ollama returned unexpected response.")
    return review.strip()
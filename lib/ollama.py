"""Thin Ollama HTTP client for benchmark use.

Talks to the local Ollama daemon at http://localhost:11434. Keeps
responses deterministic (seed + temperature 0) where the model supports it.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"


class OllamaError(RuntimeError):
    pass


def generate(model: str, prompt: str, *, seed: int = 42,
             temperature: float = 0.0, num_predict: int = 256,
             timeout: float = 120.0) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "seed": seed,
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise OllamaError(f"Ollama unreachable at {OLLAMA_URL}: {e}") from e
    if "response" not in body:
        raise OllamaError(f"Malformed Ollama response: {body}")
    return body["response"]


def embed(model: str, text: str, *, timeout: float = 120.0) -> list[float]:
    payload = {"model": model, "prompt": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/embeddings",
        data=data, headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise OllamaError(f"Ollama unreachable: {e}") from e
    if "embedding" not in body:
        raise OllamaError(f"Malformed embedding response: {body}")
    return body["embedding"]


def available() -> bool:
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False

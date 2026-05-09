from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class LocalLLMError(RuntimeError):
    pass


def local_model_name() -> str:
    return os.getenv("LOCAL_LLM_MODEL", "llama3.1:8b")


def local_base_url() -> str:
    return os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434").rstrip("/")


def extract_json(text: str) -> dict[str, Any] | list[Any] | None:
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


async def generate_local_json(
    system_prompt: str,
    user_prompt: str,
    *,
    timeout: float = 120.0,
    temperature: float = 0.4,
    num_predict: int = 1200,
) -> dict[str, Any]:
    """
    Call a local Ollama-compatible chat endpoint and return parsed JSON.

    Default endpoint: http://localhost:11434/api/chat
    Default model: llama3.1:8b
    """
    base_url = local_base_url()
    model = local_model_name()
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        raise LocalLLMError(
            f"Local model call failed. Start Ollama and run `ollama pull {model}`, "
            f"or set LOCAL_LLM_BASE_URL/LOCAL_LLM_MODEL. Details: {exc}"
        ) from exc

    content = (data.get("message") or {}).get("content") or data.get("response") or ""
    parsed = extract_json(content)
    if not isinstance(parsed, dict):
        logger.debug(f"Local model raw output was not JSON object: {content[:500]}")
        raise LocalLLMError("Local model did not return a valid JSON object.")
    return parsed

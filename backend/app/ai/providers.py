import json
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.config import get_settings


class AIProviderError(RuntimeError):
    pass


def current_provider_name() -> str:
    return get_settings().ai_model_provider


def current_model_name() -> str:
    settings = get_settings()
    if settings.ai_model_name:
        return settings.ai_model_name
    if settings.ai_model_provider == "deepseek":
        return "deepseek-chat"
    return "gpt-4o-mini"


def call_json_model(
    *,
    system_prompt: str,
    user_prompt: str,
    response_model: type[BaseModel],
) -> dict[str, Any]:
    settings = get_settings()
    if settings.ai_pipeline_mode == "mock":
        raise AIProviderError("Live provider requested while AI_PIPELINE_MODE=mock.")

    provider = settings.ai_model_provider.lower()
    if provider == "openai":
        raw = _call_openai_chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
    elif provider == "deepseek":
        raw = _call_deepseek_chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
    else:
        raise AIProviderError(f"Unsupported AI provider: {settings.ai_model_provider}")

    try:
        parsed = response_model.model_validate(raw)
    except ValidationError as exc:
        raise AIProviderError(f"Model JSON validation failed: {exc}") from exc
    return parsed.model_dump()


def _call_openai_chat_json(*, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise AIProviderError("OPENAI_API_KEY is not configured.")

    payload = {
        "model": current_model_name(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    return _post_json(
        url="https://api.openai.com/v1/chat/completions",
        headers=headers,
        payload=payload,
    )


def _call_deepseek_chat_json(*, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.deepseek_api_key:
        raise AIProviderError("DEEPSEEK_API_KEY is not configured.")

    payload = {
        "model": current_model_name(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    return _post_json(
        url="https://api.deepseek.com/chat/completions",
        headers=headers,
        payload=payload,
    )


def _post_json(*, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIProviderError(f"Unexpected provider response shape: {body}") from exc

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIProviderError(f"Provider did not return valid JSON: {content}") from exc

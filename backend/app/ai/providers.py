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
    if settings.ai_model_provider == "xiaomi":
        return "mimo-v2-flash"
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
    raw = _call_provider(
        provider=provider,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    try:
        parsed = response_model.model_validate(raw)
    except ValidationError as exc:
        repaired_raw = _repair_json_to_schema(
            provider=provider,
            raw=raw,
            validation_error=str(exc),
            response_model=response_model,
        )
        try:
            parsed = response_model.model_validate(repaired_raw)
        except ValidationError as repair_exc:
            raise AIProviderError(
                f"Model JSON validation failed after repair attempt: {repair_exc}"
            ) from repair_exc
    return parsed.model_dump()


def _call_provider(*, provider: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    if provider == "openai":
        return _call_openai_chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
    if provider == "deepseek":
        return _call_deepseek_chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
    if provider == "xiaomi":
        return _call_xiaomi_chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
    raise AIProviderError(f"Unsupported AI provider: {provider}")


def _repair_json_to_schema(
    *,
    provider: str,
    raw: dict[str, Any],
    validation_error: str,
    response_model: type[BaseModel],
) -> dict[str, Any]:
    schema_json = json.dumps(response_model.model_json_schema(), ensure_ascii=True)
    raw_json = json.dumps(raw, ensure_ascii=True)
    system_prompt = (
        "You are a JSON repair assistant. "
        "Return valid JSON only. "
        "Fix the object so it strictly matches the provided JSON schema. "
        "Do not add markdown, code fences, or explanations."
    )
    user_prompt = (
        "Repair this JSON object to satisfy the target schema.\n\n"
        f"TARGET_JSON_SCHEMA:\n{schema_json}\n\n"
        f"VALIDATION_ERROR:\n{validation_error}\n\n"
        f"INVALID_JSON_OBJECT:\n{raw_json}"
    )
    return _call_provider(
        provider=provider,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


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


def _call_xiaomi_chat_json(*, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.xiaomi_api_key:
        raise AIProviderError("XIAOMI_API_KEY is not configured.")

    payload = {
        "model": current_model_name(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_completion_tokens": 2048,
        "temperature": 0.2,
        "top_p": 0.95,
        "stream": False,
        "thinking": {"type": "disabled"},
    }
    headers = {
        "api-key": settings.xiaomi_api_key,
        "Content-Type": "application/json",
    }
    return _post_json(
        url="https://api.xiaomimimo.com/v1/chat/completions",
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

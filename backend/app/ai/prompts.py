import json
from typing import Any

from app.models.article import Article


def build_structured_prompts(article: Article) -> tuple[str, str]:
    system_prompt = (
        "You are an information structuring assistant. "
        "Return valid JSON only. Do not include markdown, prose, or code fences. "
        "Be conservative and only use information supported by the article."
    )
    payload = {
        "title": article.title,
        "url": article.url,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "summary": article.summary,
        "content": _truncate(article.content or article.summary or article.title, 12000),
    }
    user_prompt = (
        "Parse this article into JSON with keys: "
        "title, source, article_type, topics, entities, summary, key_facts, "
        "sentiment, importance_score, confidence.\n\n"
        f"ARTICLE_JSON:\n{json.dumps(payload, ensure_ascii=True)}"
    )
    return system_prompt, user_prompt


def build_cognitive_prompts(article: Article, structured_result: dict[str, Any]) -> tuple[str, str]:
    system_prompt = (
        "You are a senior research analyst. "
        "Return valid JSON only. Distinguish direct facts, inference, and uncertainty."
    )
    payload = {
        "title": article.title,
        "content": _truncate(article.content or article.summary or article.title, 12000),
        "structured_result": structured_result,
    }
    user_prompt = (
        "Analyze what this article means. Return JSON with keys: "
        "core_insight, drivers, trend_type, impact_scope, bias_risk, "
        "uncertainties, related_trends, analysis_confidence.\n\n"
        f"ANALYSIS_INPUT_JSON:\n{json.dumps(payload, ensure_ascii=True)}"
    )
    return system_prompt, user_prompt


def build_decision_prompts(
    article: Article,
    structured_result: dict[str, Any],
    cognitive_result: dict[str, Any],
) -> tuple[str, str]:
    system_prompt = (
        "You are an investment research workflow assistant. "
        "Return valid JSON only. Make concrete but non-overstated decisions."
    )
    payload = {
        "title": article.title,
        "url": article.url,
        "structured_result": structured_result,
        "cognitive_result": cognitive_result,
        "user_profile": {
            "interests": ["macro", "policy", "markets", "crypto", "AI"],
            "risk_preference": "medium",
        },
    }
    user_prompt = (
        "Convert this analysis into a decision object. Return JSON with keys: "
        "attention_required, priority_level, impact_direction, impact_strength, "
        "recommended_action, is_actionable_signal, watchlist_tags, reason, confidence.\n\n"
        f"DECISION_INPUT_JSON:\n{json.dumps(payload, ensure_ascii=True)}"
    )
    return system_prompt, user_prompt


def _truncate(value: str, limit: int) -> str:
    return value[:limit]


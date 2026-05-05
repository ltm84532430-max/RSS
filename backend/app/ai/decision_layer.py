from app.models.article import Article
from app.ai.contracts import DecisionResultModel
from app.ai.prompts import build_decision_prompts
from app.ai.providers import call_json_model
from app.config import get_settings


def analyze_decision(article: Article, structured_result: dict, cognitive_result: dict) -> dict:
    if get_settings().ai_pipeline_mode != "mock":
        system_prompt, user_prompt = build_decision_prompts(
            article,
            structured_result,
            cognitive_result,
        )
        return call_json_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=DecisionResultModel,
        )

    _ = article
    importance_score = int(structured_result.get("importance_score") or 1)
    priority_level = _priority_level(importance_score)
    recommended_action = _recommended_action(priority_level)

    return {
        "attention_required": priority_level in {"medium", "high", "critical"},
        "priority_level": priority_level,
        "impact_direction": "uncertain",
        "impact_strength": max(1, min(importance_score, 10)),
        "recommended_action": recommended_action,
        "is_actionable_signal": priority_level in {"high", "critical"},
        "watchlist_tags": cognitive_result.get("related_trends") or [],
        "reason": f"Mock decision based on importance_score={importance_score}.",
        "confidence": 0.5,
        "mode": "mock",
    }


def _priority_level(score: int) -> str:
    if score >= 8:
        return "critical"
    if score >= 6:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _recommended_action(priority_level: str) -> str:
    if priority_level == "critical":
        return "alert"
    if priority_level == "high":
        return "track"
    if priority_level == "medium":
        return "read"
    return "ignore"

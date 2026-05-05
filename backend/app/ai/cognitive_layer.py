from app.models.article import Article
from app.ai.contracts import CognitiveResultModel
from app.ai.prompts import build_cognitive_prompts
from app.ai.providers import call_json_model
from app.config import get_settings


def analyze_cognitive(article: Article, structured_result: dict) -> dict:
    if get_settings().ai_pipeline_mode != "mock":
        system_prompt, user_prompt = build_cognitive_prompts(article, structured_result)
        return call_json_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=CognitiveResultModel,
        )

    _ = article
    topics = structured_result.get("topics") or []
    summary = structured_result.get("summary") or ""

    return {
        "core_insight": summary,
        "drivers": topics[:5],
        "trend_type": "medium_term_signal",
        "impact_scope": {
            "industries": [],
            "companies": [],
            "assets": [],
            "regions": [],
        },
        "bias_risk": {
            "has_bias": False,
            "bias_type": None,
            "explanation": "Mock pipeline has no external verification step.",
        },
        "uncertainties": ["Mock analysis only; replace with provider-backed reasoning later."],
        "related_trends": topics[:3],
        "analysis_confidence": 0.5,
        "mode": "mock",
    }

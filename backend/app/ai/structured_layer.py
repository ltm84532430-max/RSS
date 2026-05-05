from app.models.article import Article
from app.ai.contracts import StructuredResultModel
from app.ai.prompts import build_structured_prompts
from app.ai.providers import call_json_model
from app.config import get_settings


def analyze_structured(article: Article) -> dict:
    if get_settings().ai_pipeline_mode != "mock":
        system_prompt, user_prompt = build_structured_prompts(article)
        return call_json_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=StructuredResultModel,
        )

    text = article.content or article.summary or article.title
    summary = article.summary or _truncate(text, 420)
    topics = _keywords(text)
    importance_score = _importance_score(text)

    return {
        "title": article.title,
        "source_id": article.source_id,
        "article_type": "news",
        "topics": topics[:6],
        "entities": {
            "companies": [],
            "people": [],
            "countries": [],
            "industries": [],
            "assets": [],
            "technologies": [],
        },
        "summary": summary,
        "key_facts": [summary] if summary else [],
        "sentiment": "neutral",
        "importance_score": importance_score,
        "confidence": 0.55,
        "mode": "mock",
    }


def _truncate(value: str, limit: int) -> str:
    normalized = " ".join(value.split())
    return normalized[:limit]


def _keywords(value: str) -> list[str]:
    words = [
        word.strip(".,:;!?()[]{}\"'").lower()
        for word in value.split()
        if len(word.strip(".,:;!?()[]{}\"'")) >= 5
    ]
    seen: set[str] = set()
    result: list[str] = []
    for word in words:
        if word and word not in seen:
            seen.add(word)
            result.append(word)
    return result


def _importance_score(value: str) -> int:
    lower = value.lower()
    important_terms = (
        "federal reserve",
        "interest rate",
        "inflation",
        "monetary",
        "central bank",
        "policy",
        "market",
        "financial",
    )
    score = 3 + sum(1 for term in important_terms if term in lower)
    return min(max(score, 1), 10)

from dataclasses import dataclass

from app.ai.cognitive_layer import analyze_cognitive
from app.ai.decision_layer import analyze_decision
from app.ai.structured_layer import analyze_structured
from app.models.article import Article


@dataclass(frozen=True)
class PipelineResult:
    structured_result: dict
    cognitive_result: dict
    decision_result: dict


def run_ai_pipeline(article: Article) -> PipelineResult:
    structured_result = analyze_structured(article)
    cognitive_result = analyze_cognitive(article, structured_result)
    decision_result = analyze_decision(article, structured_result, cognitive_result)
    return PipelineResult(
        structured_result=structured_result,
        cognitive_result=cognitive_result,
        decision_result=decision_result,
    )


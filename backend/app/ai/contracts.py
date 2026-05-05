from pydantic import BaseModel, Field


class StructuredEntities(BaseModel):
    companies: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)


class StructuredResultModel(BaseModel):
    title: str
    source: str | None = None
    article_type: str
    topics: list[str] = Field(default_factory=list)
    entities: StructuredEntities
    summary: str
    key_facts: list[str] = Field(default_factory=list)
    sentiment: str
    importance_score: int = Field(ge=1, le=10)
    confidence: float = Field(ge=0, le=1)


class CognitiveBiasRisk(BaseModel):
    has_bias: bool
    bias_type: str | None = None
    explanation: str


class CognitiveImpactScope(BaseModel):
    industries: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)


class CognitiveResultModel(BaseModel):
    core_insight: str
    drivers: list[str] = Field(default_factory=list)
    trend_type: str
    impact_scope: CognitiveImpactScope
    bias_risk: CognitiveBiasRisk
    uncertainties: list[str] = Field(default_factory=list)
    related_trends: list[str] = Field(default_factory=list)
    analysis_confidence: float = Field(ge=0, le=1)


class DecisionResultModel(BaseModel):
    attention_required: bool
    priority_level: str
    impact_direction: str
    impact_strength: int = Field(ge=1, le=10)
    recommended_action: str
    is_actionable_signal: bool
    watchlist_tags: list[str] = Field(default_factory=list)
    reason: str
    confidence: float = Field(ge=0, le=1)


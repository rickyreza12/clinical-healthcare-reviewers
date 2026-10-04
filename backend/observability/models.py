from pydantic import BaseModel, ConfigDict, Field


class LLMCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    call_id: str
    purpose: str
    provider: str
    runtime: str
    model: str
    input_tokens: int | None = Field(default=0, ge=0)
    output_tokens: int | None = Field(default=0, ge=0)
    latency_ms: float = 0
    retries: int = 0
    cache_status: str = "not_used"
    outcome: str = "success"
    cost_usd: float | None = Field(default=0, ge=0)
    request_id: str | None = None
    review_id: str | None = None
    case_id: str | None = None
    timestamp: str | None = None
    error_category: str | None = None
    is_estimate: bool = False
    cost_basis: str | None = None


class ProcessingMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rules_executed: list[str] = Field(default_factory=list)
    retrieval: dict = Field(default_factory=dict)
    llm_calls: list[dict] = Field(default_factory=list)
    duration_ms: float = 0
    cost: dict = Field(default_factory=dict)

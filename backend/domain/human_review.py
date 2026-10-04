from pydantic import BaseModel, ConfigDict, Field


class HumanReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required: bool = False
    reasons: list[str] = Field(default_factory=list)

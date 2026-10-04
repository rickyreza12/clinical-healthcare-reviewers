from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from backend.domain.enums import FindingType, Severity
from backend.domain.evidence import Evidence
from backend.domain.human_review import HumanReview
from backend.domain.policy import PolicyReference


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    finding_id: str = Field(default_factory=lambda: f"F-{uuid4().hex[:10]}")
    type: FindingType
    severity: Severity
    title: str
    description: str
    field: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    policy: PolicyReference
    human_review: HumanReview

from pydantic import BaseModel, ConfigDict
from backend.domain.enums import ReviewStatus
from backend.review.models import Finding
from backend.observability.models import ProcessingMetadata


class ReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str
    review_status: ReviewStatus
    requires_human_review: bool
    findings: list[Finding]
    metadata: ProcessingMetadata | None = None

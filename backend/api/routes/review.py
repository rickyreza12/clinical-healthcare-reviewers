from fastapi import APIRouter, Body, Path, Query
from backend.api.models.request import ReviewRequest
from backend.api.models.response import ReviewResponse
from backend.review.service import review_case
from backend.semantic.remote_provider import configured_provider


router = APIRouter()


@router.post("/cases/{case_id}/review", response_model=ReviewResponse)
def review(case_id: str = Path(pattern=r"^CASE-\d{3}$"), include_metadata: bool = Query(False),
           request: ReviewRequest | None = Body(None)):
    return review_case(
        case_id,
        include_metadata=include_metadata or bool(request and request.include_metadata),
        semantic_provider=configured_provider(case_id),
    )

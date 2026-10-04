"""Application service for reviewing one case."""

from time import perf_counter

from backend.ingestion.case_loader import load_case
from backend.ingestion.fact_extractor import extract_facts
from backend.observability.models import ProcessingMetadata
from backend.observability.journal import record_calls
from backend.review.checks import ReviewChecks
from backend.review.status import aggregate_status
from backend.semantic.base import SemanticProvider


def review_case(case_id: str, include_metadata: bool = False,
                semantic_provider: SemanticProvider | None = None) -> dict:
    """Load, evaluate, and serialize a case review."""
    started = perf_counter()
    bundle = load_case(case_id)
    facts = extract_facts(bundle)
    checks = ReviewChecks(
        case_id=case_id,
        facts=facts,
        document_types={document.document_type for document in bundle.documents},
        semantic_provider=semantic_provider,
    )
    checks.run()
    record_calls(checks.semantic_calls)

    response = {
        "case_id": case_id,
        "review_status": aggregate_status(checks.findings),
        "requires_human_review": bool(checks.findings),
        "findings": checks.findings,
    }
    if include_metadata:
        response["metadata"] = _build_metadata(checks, started).model_dump()
    return response


def _build_metadata(checks: ReviewChecks, started: float) -> ProcessingMetadata:
    costs = [call.get("cost_usd") for call in checks.semantic_calls]
    return ProcessingMetadata(
        rules_executed=sorted(checks.rules_executed),
        llm_calls=checks.semantic_calls,
        duration_ms=(perf_counter() - started) * 1000,
        cost={
            "llm_cost_usd": sum(costs) if all(cost is not None for cost in costs) else None,
            "llm_call_count": len(checks.semantic_calls),
            "is_estimate": bool(costs),
            "basis": ("hourly_rate_not_configured" if any(cost is None for cost in costs)
                      else "self_hosted_runtime_allocation" if costs else "no_llm_calls"),
            "unknown_cost_calls": sum(cost is None for cost in costs),
        },
    )

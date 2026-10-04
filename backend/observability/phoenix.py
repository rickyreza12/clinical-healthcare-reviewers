"""Prompt-free OpenTelemetry export for local Phoenix monitoring."""

import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


_logger = logging.getLogger(__name__)
_tracer: trace.Tracer | None = None
_provider: TracerProvider | None = None


def configure_phoenix() -> None:
    """Set up one async exporter when Phoenix monitoring is explicitly enabled."""
    global _provider, _tracer
    if os.getenv("PHOENIX_ENABLED", "false").casefold() != "true" or _tracer:
        return

    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "").strip()
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError("PHOENIX_COLLECTOR_ENDPOINT must be an HTTP(S) URL")

    project_name = os.getenv("PHOENIX_PROJECT_NAME", "clinical-document-review")
    resource = Resource.create({SERVICE_NAME: "clinical-review-api", "openinference.project.name": project_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    _provider = provider
    _tracer = provider.get_tracer("clinical_review.semantic")


def record_phoenix_call(call: dict) -> None:
    """Export safe model-call metadata without inputs, outputs, or patient data."""
    if _tracer is None:
        return
    try:
        with _tracer.start_as_current_span("llm.diagnosis_semantic_comparison") as span:
            for name, value in phoenix_attributes(call).items():
                span.set_attribute(name, value)
    except Exception:
        _logger.warning("Phoenix export preparation failed", exc_info=True)


def phoenix_attributes(call: dict) -> dict[str, str | int | float | bool]:
    """Map one local usage row to monitoring fields safe to leave the process."""
    attributes: dict[str, str | int | float | bool] = {
        "openinference.span.kind": "LLM",
        "llm.model_name": str(call["model"]),
        "llm.provider": str(call["provider"]),
        "llm.invocation_parameters": '{"temperature":0,"max_tokens":256}',
        "clinical_review.call_id": str(call["call_id"]),
        "clinical_review.request_id": str(call.get("request_id") or ""),
        "clinical_review.review_id": str(call.get("review_id") or ""),
        "clinical_review.purpose": str(call["purpose"]),
        "clinical_review.runtime": str(call["runtime"]),
        "clinical_review.outcome": str(call["outcome"]),
        "clinical_review.retries": int(call["retries"]),
        "clinical_review.cache_status": str(call["cache_status"]),
        "clinical_review.cost_basis": str(call.get("cost_basis") or "unknown"),
        "clinical_review.cost_is_estimate": bool(call.get("is_estimate")),
        "clinical_review.cost_known": call.get("cost_usd") is not None,
        "gen_ai.usage.input_tokens": int(call["input_tokens"] or 0),
        "gen_ai.usage.output_tokens": int(call["output_tokens"] or 0),
        "llm.token_count.prompt": int(call["input_tokens"] or 0),
        "llm.token_count.completion": int(call["output_tokens"] or 0),
        "llm.latency_ms": float(call["latency_ms"]),
    }
    if call.get("cost_usd") is not None:
        attributes["llm.cost.total"] = float(call["cost_usd"])
    if call.get("error_category"):
        attributes["clinical_review.error_category"] = str(call["error_category"])
    return attributes


def shutdown_phoenix() -> None:
    """Flush buffered spans before the application process exits."""
    if _provider is not None:
        _provider.force_flush(timeout_millis=5_000)

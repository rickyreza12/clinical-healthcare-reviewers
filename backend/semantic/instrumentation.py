from time import perf_counter
from backend.observability.models import LLMCall


def instrument_compare(provider, clinical: str, claim: str, call_id: str):
    start = perf_counter()
    result = provider.compare(clinical, claim)
    elapsed = (perf_counter() - start) * 1000
    call = LLMCall(call_id=call_id, purpose="diagnosis_comparison", provider=provider.__class__.__name__,
                   runtime="local", model="mock", latency_ms=elapsed, outcome=result.outcome)
    return result, call

from backend.observability.models import LLMCall


def make_call(**values) -> LLMCall:
    return LLMCall(**values)

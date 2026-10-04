from backend.semantic.router import compare_diagnoses


class BrokenProvider:
    def compare(self, clinical, claim):
        raise RuntimeError("offline")


def test_semantic_unavailable_never_fabricates_answer():
    result, reason, calls = compare_diagnoses("condition alpha", "condition beta", BrokenProvider())
    assert result == "uncertain" and "unavailable" in reason and calls == 1

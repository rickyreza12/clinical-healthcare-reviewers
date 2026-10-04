from backend.cost.self_hosted import projected_cost


def test_projected_cost_marked_estimate():
    result = projected_cost(2.0, 60)
    assert result == {"amount_usd": 2 / 60, "is_estimate": True, "basis": "assumed_runtime", "runtime_seconds": 60}

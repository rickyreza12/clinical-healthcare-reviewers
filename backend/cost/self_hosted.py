def allocated_cost(hourly_rate_usd: float, runtime_seconds: float) -> float:
    if hourly_rate_usd < 0 or runtime_seconds < 0:
        raise ValueError("rate and runtime must be nonnegative")
    return hourly_rate_usd * runtime_seconds / 3600


def projected_cost(hourly_rate_usd: float, assumed_runtime_seconds: float) -> dict:
    return {"amount_usd": allocated_cost(hourly_rate_usd, assumed_runtime_seconds),
            "is_estimate": True, "basis": "assumed_runtime", "runtime_seconds": assumed_runtime_seconds}

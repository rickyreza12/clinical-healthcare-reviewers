def cache_status(hit: bool | None) -> str:
    return "not_used" if hit is None else ("hit" if hit else "miss")

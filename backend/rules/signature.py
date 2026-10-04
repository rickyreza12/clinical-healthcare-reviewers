def is_valid_signature(value: str | None) -> bool:
    return bool(value and value.strip().casefold() in {"signed", "yes", "true", "present"})

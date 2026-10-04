from datetime import date


def parse_date(value: str | None):
    try:
        return date.fromisoformat(value.strip()) if value else None
    except ValueError:
        return None


def chronology_invalid(admission: str | None, discharge: str | None) -> bool:
    a, d = parse_date(admission), parse_date(discharge)
    return bool(a and d and d < a)

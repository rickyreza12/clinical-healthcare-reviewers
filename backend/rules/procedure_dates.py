from backend.rules.chronology import parse_date


def outside_stay(procedure: str | None, admission: str | None, discharge: str | None) -> bool:
    p, a, d = parse_date(procedure), parse_date(admission), parse_date(discharge)
    return bool(p and a and d and not a <= p <= d)

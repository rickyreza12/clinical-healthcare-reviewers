from backend.normalization.names import normalize_name


def identity_mismatches(facts):
    result = []
    for field in ("patient_id", "dob"):
        values = [fact for fact in facts.values(field) if fact.value]
        if len({v.value.strip().casefold() for v in values}) > 1:
            result.append((field, values))
    # Name comparison deliberately informational only: SOP-02 says name alone cannot trigger mismatch.
    _ = [normalize_name(f.value) for f in facts.values("patient_name")]
    return result

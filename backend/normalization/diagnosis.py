import re


def normalize_diagnosis(value: str) -> str:
    text = value.casefold().replace("type 2 diabetes mellitus", "t2dm")
    text = re.sub(r"without (?:documented )?complications", "uncomplicated", text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return " ".join(text.split())


def deterministic_comparison(clinical: str, claim: str) -> str:
    a, b = normalize_diagnosis(clinical), normalize_diagnosis(claim)
    equivalents = {frozenset(("t2dm uncomplicated", "t2dm"))}
    if a == b or frozenset((a, b)) in equivalents:
        return "equivalent"
    conflicts = (("pneumonia", "bronchitis"), ("appendicitis", "gastroenteritis"))
    if any(x in a and y in b or y in a and x in b for x, y in conflicts):
        return "conflict"
    return "uncertain"

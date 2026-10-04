import re

UNCERTAIN_CUES = re.compile(r"\b(suspected|possible|possibly|rule[- ]out|not confirmed|not definitive|differential includes|cannot exclude)\b", re.I)


def is_uncertain(value: str) -> bool:
    return bool(UNCERTAIN_CUES.search(value or ""))

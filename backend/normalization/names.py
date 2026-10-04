import re
import unicodedata


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    value = re.sub(r"\b(dr|doctor|mr|mrs|ms|miss)\.?\b", " ", value)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", value).split())

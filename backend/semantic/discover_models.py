"""List model IDs without displaying credentials or server file paths."""

import json
from pathlib import Path

from dotenv import load_dotenv
import httpx

from backend.semantic.settings import semantic_settings


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
    settings = semantic_settings()
    try:
        response = httpx.get(
            settings.base_url + "/models",
            headers={"Authorization": "Bearer " + settings.api_key.get_secret_value()},
            timeout=settings.timeout_seconds,
            follow_redirects=False,
        )
        response.raise_for_status()
        print(json.dumps([row["id"] for row in response.json()["data"]], indent=2))
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise SystemExit("Model discovery failed; check endpoint and credentials.") from None


if __name__ == "__main__":
    main()

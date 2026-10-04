"""Run one explicitly requested, synthetic semantic fallback through the router."""

import json
from pathlib import Path

from dotenv import load_dotenv

from backend.observability.journal import record_calls
from backend.observability.phoenix import configure_phoenix, shutdown_phoenix
from backend.semantic.remote_provider import configured_provider
from backend.semantic.router import compare_diagnoses


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
    configure_phoenix()
    provider = configured_provider("INTEGRATION-SMOKE")
    if provider is None:
        raise SystemExit("Enable SEMANTIC_ENABLED to run the live smoke test.")
    relation, rationale, _ = compare_diagnoses("essential hypertension", "primary hypertension", provider)
    record_calls(provider.calls)
    shutdown_phoenix()
    print(json.dumps({"relation": relation, "rationale": rationale,
                      "telemetry": provider.calls}, indent=2))


if __name__ == "__main__":
    main()

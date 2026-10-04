"""Append prompt-free model usage records for local cost reporting."""

import json
import logging
import os
from pathlib import Path
from threading import Lock

from backend.observability.phoenix import record_phoenix_call


_lock = Lock()
_logger = logging.getLogger(__name__)


def record_calls(calls: list[dict]) -> None:
    if not calls:
        return
    for call in calls:
        record_phoenix_call(call)
    app_root = Path(__file__).resolve().parents[2]
    destination = Path(os.getenv("BITHEALTH_TELEMETRY_PATH", app_root / "data" / "telemetry.jsonl"))
    try:
        with _lock:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("a", encoding="utf-8") as stream:
                for call in calls:
                    stream.write(json.dumps(call) + "\n")
    except OSError:
        _logger.error("Model telemetry persistence failed; usage remains in response metadata")

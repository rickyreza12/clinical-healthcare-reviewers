import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: str | None = None
    telemetry_path: str = "data/telemetry.jsonl"
    self_hosted_hourly_usd: float | None = None


def get_settings() -> Settings:
    return Settings(host=os.getenv("BITHEALTH_HOST", "0.0.0.0"), port=int(os.getenv("BITHEALTH_PORT", "8000")),
                    data_dir=os.getenv("BITHEALTH_DATA_DIR"), telemetry_path=os.getenv("BITHEALTH_TELEMETRY_PATH", "data/telemetry.jsonl"),
                    self_hosted_hourly_usd=float(os.getenv("SELF_HOSTED_HOURLY_USD")) if os.getenv("SELF_HOSTED_HOURLY_USD") else None)

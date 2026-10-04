"""Environment configuration for the optional self-hosted semantic fallback."""

import os

from pydantic import BaseModel, Field, SecretStr, ValidationError, model_validator


class SemanticSettings(BaseModel):
    enabled: bool = False
    base_url: str = ""
    api_key: SecretStr = SecretStr("")
    model: str = ""
    timeout_seconds: float = Field(default=60, gt=0, le=300)
    hourly_rate_usd: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_enabled(self):
        if self.enabled and (not self.model or not self.api_key.get_secret_value()
                             or not self.base_url.startswith(("http://", "https://"))):
            raise ValueError("Enabled semantic fallback requires URL, API key, and model")
        return self


def semantic_settings() -> SemanticSettings:
    rate = os.getenv("SELF_HOSTED_HOURLY_USD", "").strip()
    try:
        return SemanticSettings(
            enabled=os.getenv("SEMANTIC_ENABLED", "false"),
            base_url=os.getenv("LLM_BASE_URL", "").rstrip("/"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", ""),
            timeout_seconds=os.getenv("LLM_TIMEOUT_SECONDS", "60"),
            hourly_rate_usd=rate if rate else None,
        )
    except ValidationError:
        # Validation error input dictionaries may contain the raw API key.
        raise ValueError("Invalid semantic configuration; check URL, model, key, timeout and hourly rate") from None

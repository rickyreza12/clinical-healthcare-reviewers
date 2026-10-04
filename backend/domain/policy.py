from pydantic import BaseModel, ConfigDict


class PolicyReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str
    title: str
    rule: str
    section: str | None = None
    version: str = "1.0"

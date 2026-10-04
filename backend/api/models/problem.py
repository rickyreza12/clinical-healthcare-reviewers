from pydantic import BaseModel, ConfigDict


class Problem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
    trace_id: str | None = None

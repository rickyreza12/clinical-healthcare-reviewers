from pydantic import BaseModel, ConfigDict


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    document_name: str
    field: str | None = None
    section: str | None = None
    value: str
    locator: str | None = None

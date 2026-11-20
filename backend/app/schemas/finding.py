"""Finding request/response schemas."""

from pydantic import BaseModel, ConfigDict


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: int
    tool: str
    severity: str
    title: str
    description: str | None = None
    package_name: str | None = None
    package_version: str | None = None
    fixed_version: str | None = None
    advisory_id: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    is_redacted: bool = False
    references: list[str] | None = None

"""Scan request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScanBase(BaseModel):
    trigger: str = Field(default="manual", min_length=1, max_length=32)


class ScanCreate(ScanBase):
    pass


class ScanRead(ScanBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repository_id: int
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    summary: dict[str, Any] | None = None


class ScanListItem(ScanRead):
    pass

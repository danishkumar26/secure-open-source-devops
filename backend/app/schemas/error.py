"""Standard API error response schema."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Consistent error body for all API error responses."""

    model_config = ConfigDict(from_attributes=True)

    detail: str
    error_code: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

"""Repository request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RepositoryBase(BaseModel):
    github_owner: str = Field(..., min_length=1, max_length=255)
    github_repo: str = Field(..., min_length=1, max_length=255)
    html_url: HttpUrl
    description: str | None = Field(default=None, max_length=2000)
    default_branch: str = Field(default="main", min_length=1, max_length=255)
    is_private: bool = False


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryRead(RepositoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    last_scanned_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RepositoryListItem(RepositoryRead):
    pass

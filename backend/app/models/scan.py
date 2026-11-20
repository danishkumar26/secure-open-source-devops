"""Scan domain model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.repository import Repository


class ScanStatus(enum.StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Scan(Base):
    """A security scan run against a repository."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(
        sa.ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[ScanStatus] = mapped_column(
        sa.Enum(ScanStatus), nullable=False, server_default="pending"
    )
    trigger: Mapped[str] = mapped_column(sa.String(32), nullable=False, server_default="manual")
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    summary: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="scans")
    findings: Mapped[list["Finding"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

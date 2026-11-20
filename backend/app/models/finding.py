"""Finding domain model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.scan import Scan


class Severity(enum.StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class Finding(Base):
    """A single security finding produced by a scanner integration."""

    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        sa.ForeignKey("scans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tool: Mapped[str] = mapped_column(sa.String(64), index=True, nullable=False)
    severity: Mapped[Severity] = mapped_column(sa.Enum(Severity), nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    package_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    package_version: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    fixed_version: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    advisory_id: Mapped[str | None] = mapped_column(sa.String(128), nullable=True, index=True)
    file_path: Mapped[str | None] = mapped_column(sa.String(1024), nullable=True)
    line_number: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    is_redacted: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())
    references: Mapped[list[str] | None] = mapped_column(sa.JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    scan: Mapped["Scan"] = relationship(back_populates="findings")

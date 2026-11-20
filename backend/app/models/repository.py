"""Repository domain model."""

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.scan import Scan


class Repository(Base):
    """A monitored open-source repository."""

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    github_owner: Mapped[str] = mapped_column(sa.String(255), index=True, nullable=False)
    github_repo: Mapped[str] = mapped_column(sa.String(255), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(512), unique=True, index=True, nullable=False)
    html_url: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(
        sa.String(255), nullable=False, server_default="main"
    )
    is_private: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())
    last_scanned_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )

    scans: Mapped[list["Scan"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )

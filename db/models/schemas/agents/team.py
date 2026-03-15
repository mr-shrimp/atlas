from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("department_id", "name", name="uq_department_team"),
        Index("idx_teams_department", "department_id"),
        {"schema": "agents"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    department_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.departments.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    department = relationship("Department")

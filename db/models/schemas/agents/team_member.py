from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        Index("idx_team_members_agent", "agent_id"),
        {"schema": "agents"},
    )

    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.teams.id", ondelete="CASCADE"),
        primary_key=True,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.agents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    team_role_id: Mapped[int] = mapped_column(
        ForeignKey("agents.team_roles.id"),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

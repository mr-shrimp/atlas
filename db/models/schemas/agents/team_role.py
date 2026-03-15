from datetime import datetime

from sqlalchemy import DateTime, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class TeamRole(Base):
    __tablename__ = "team_roles"
    __table_args__ = {"schema": "agents"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

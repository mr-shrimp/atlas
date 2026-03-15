from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {"schema": "agents"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

from datetime import datetime

from sqlalchemy import DateTime, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class Model(Base):
    __tablename__ = "models"
    __table_args__ = {"schema": "agents"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    provider: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

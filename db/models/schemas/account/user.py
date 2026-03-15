from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "account"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    being_id: Mapped[UUID] = mapped_column(
        ForeignKey("identity.beings.id"), nullable=False
    )

    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    being = relationship("Being")

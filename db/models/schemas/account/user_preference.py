from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"
    __table_args__ = {"schema": "account"}

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    preference_type_id: Mapped[int] = mapped_column(
        ForeignKey("account.preference_types.id"),
        primary_key=True,
    )

    value: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    user = relationship("User")

    preference_type = relationship("PreferenceType")

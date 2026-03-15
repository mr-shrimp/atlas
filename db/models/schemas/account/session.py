from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "account"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(Text, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(INET)

    user_agent: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    user = relationship("User")

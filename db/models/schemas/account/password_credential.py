from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class PasswordCredential(Base):
    __tablename__ = "password_credentials"
    __table_args__ = (
        Index("idx_password_credentials_user", "user_id"),
        {"schema": "account"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.users.id", ondelete="CASCADE"),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    algorithm: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="argon2id",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship("User")

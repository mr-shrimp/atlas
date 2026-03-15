from sqlalchemy import SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class AutonomyLevel(Base):
    __tablename__ = "autonomy_levels"
    __table_args__ = {"schema": "agents"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

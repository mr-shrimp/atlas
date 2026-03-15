from sqlalchemy import Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class BeingType(Base):
    """
    Represents a type or category of being in the identity schema.
    Attributes:
        id (int): Primary key identifier for the being type.
        name (str): Name of the being type.
        description (str): Description of the being type.
        beings (list[Being]): List of beings associated with this being type.
    Relationships:
        beings: One-to-many relationship to the `Being` class, representing all beings of this type.
    """

    __tablename__ = "being_types"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    beings = relationship("Being", back_populates="being_type")

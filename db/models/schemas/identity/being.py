from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from db.models.base import Base


class Being(Base):
    """
    Represents a being entity in the identity schema.
    Attributes:
        id (UUID): Primary key identifier for the being.
        being_type_id (int): Foreign key referencing the being type.
        being_role_id (int): Foreign key referencing the being role.
        name (str): Name of the being.
        being_type (BeingType): Relationship to the BeingType entity.
        being_role (BeingRole): Relationship to the BeingRole entity.
    """

    __tablename__ = "beings"
    __table_args__ = {"schema": "identity"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    being_type_id: Mapped[int] = mapped_column(
        ForeignKey("identity.being_types.id"), nullable=False
    )

    being_role_id: Mapped[int] = mapped_column(
        ForeignKey("identity.being_roles.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    being_type = relationship("BeingType", back_populates="beings")
    being_role = relationship("BeingRole", back_populates="beings")

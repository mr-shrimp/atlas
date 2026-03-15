from sqlalchemy import Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class BeingRole(Base):
    """
    Represents a role that can be assigned to a being within the identity schema.
    Attributes:
        id (int): The unique identifier for the being role.
        name (str): The name of the role.
        description (str): A detailed description of the role.
        beings (list[Being]): List of beings associated with this role.
    """

    __tablename__ = "being_roles"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    beings = relationship("Being", back_populates="being_role")

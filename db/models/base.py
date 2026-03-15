from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    This class serves as the declarative base for SQLAlchemy models in the project.
    All model classes should inherit from this base to ensure consistent metadata and
    declarative behavior.

    Attributes:
        __abstract__ (bool): Indicates that this class is intended to be used as a base class only.
    """

    pass

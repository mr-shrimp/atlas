from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from infrastructure.config import config
from infrastructure.logging import get_logger

logger = get_logger(__name__)
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Returns a singleton SQLAlchemy Engine instance for database connections.
    Initializes the engine if it does not already exist, using configuration
    parameters such as database URL, host, and database name. The engine is
    configured with a connection pool and pre-ping enabled.
    Returns:
        Engine: A SQLAlchemy Engine object for database operations.
    """

    global _engine

    if _engine is None:
        db_url = config.database_url()

        logger.info(
            "database_engine_initializing",
            host=config.get("database.host"),
            database=config.get("database.name"),
        )

        _engine = create_engine(
            db_url, pool_size=10, max_overflow=20, pool_pre_ping=True, echo=False
        )

    return _engine

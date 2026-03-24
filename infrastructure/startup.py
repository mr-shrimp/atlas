import time
from sqlalchemy import text

from infrastructure.session import get_session
from infrastructure.logging import get_logger

logger = get_logger("atlas.statup")


def wait_for_db():
    """Blocks execution until the database becomes available.

    Continuously attempts to establish a database session and execute a
    lightweight query (`SELECT 1`) until successful. Logs progress and
    retries at a fixed interval.

    Returns:
        None

    Raises:
        Exception: This function does not raise exceptions directly. All
            connection errors are caught and retried indefinitely.

    Behavior:
        - Attempts to connect to the database in a loop.
        - Executes a simple query to validate connectivity.
        - If successful, logs readiness and exits.
        - If unsuccessful, logs a warning and retries after a delay.

    Side Effects:
        - Performs repeated database connection attempts.
        - Emits log entries for each retry and upon success.
        - Introduces a blocking wait until the database is ready.

    Notes:
        - Uses a fixed retry interval of 2 seconds.
        - Intended for use during application startup to ensure
          database availability before proceeding.
    """
    logger.info("waiting_for_database")

    while True:
        try:
            with get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("database_ready")
            return
        except Exception as e:
            logger.warning("database_not_ready", error=str(e))
            time.sleep(2)


def wait_for_tables():
    """Blocks execution until required database tables are available.

    Continuously attempts to query a known table (`automation.scheduled_tasks`)
    to verify that database migrations have been applied and the schema is ready.

    Returns:
        None

    Raises:
        Exception: This function does not raise exceptions directly. All
            errors are caught and retried indefinitely.

    Behavior:
        - Attempts to query a specific table in a loop.
        - If the table exists and is accessible, logs readiness and exits.
        - If the query fails (e.g., table not created yet), logs a warning
          and retries after a delay.

    Side Effects:
        - Performs repeated database queries.
        - Emits log entries for each retry and upon success.
        - Introduces a blocking wait until required tables are ready.

    Notes:
        - Uses a fixed retry interval of 2 seconds.
        - Assumes that the presence of `automation.scheduled_tasks` implies
          that all required migrations have been applied.
        - Typically used during service initialization after database readiness.
    """
    logger.info("waiting_for_tables")

    while True:
        try:
            with get_session() as session:
                session.execute(
                    text("SELECT 1 FROM automation.scheduled_tasks LIMIT 1")
                )
            logger.info("tables_ready")
            return
        except Exception as e:
            logger.warning("tables_not_ready", error=str(e))
            time.sleep(2)

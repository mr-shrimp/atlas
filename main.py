import subprocess
import threading
import time
import uuid

from sqlalchemy import select

from db.models.schemas.identity.being import Being
from db.models.schemas.identity.being_role import BeingRole
from db.models.schemas.identity.being_type import BeingType
from infrastructure.bus.event_bus import publish, subscribe
from infrastructure.bus.event_router import register, route_event
from infrastructure.bus.event_schema import Event, create_event
from infrastructure.config import config
from infrastructure.logging import configure_logging, get_logger
from infrastructure.session import get_session

logger = get_logger("atlas.startup")

configure_logging(
    level=config.get("logging.level"),
    console=config.get("logging.console"),
    json_logs=config.get("logging.json"),
    log_dir=config.get("logging.log_dir"),
)


@register("system.start.test")
def handle_system_start_test(event: dict):
    logger.info(
        "system_start_test_handled",
        message=event["payload"].get("message"),
        source=event.get("source"),
    )


def start_listener():
    subscribe(event_handler)


def event_handler(event: Event):
    route_event(event)


def main():
    run_migrations()
    test_database()
    test_event_bus()

    while True:
        time.sleep(1)


def run_migrations():
    try:
        logger.info("running_migrations")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("migrations_success")
        return
    except Exception as e:
        logger.critical("migrations_failure", error=str(e))
    raise


def test_database():

    logger.info("testing_database_with_rollback")

    with get_session() as session:
        trans = session.begin()

        try:
            # --- 1. INSERT LOOKUP DATA (if needed) ---
            being_type = BeingType(
                id=1,
                name="system",
                description="System-level entity",
            )

            being_role = BeingRole(
                id=1,
                name="orchestrator",
                description="Controls system operations",
            )

            session.add_all([being_type, being_role])
            session.flush()

            # --- 2. INSERT MAIN ENTITY ---
            test_being = Being(
                id=uuid.uuid4(),
                name="Terry",
                being_type_id=being_type.id,
                being_role_id=being_role.id,
            )

            session.add(test_being)
            session.flush()

            # --- 3. VERIFY ---
            beings = session.execute(select(Being)).scalars().all()

            logger.info(
                "test_being_inserted",
                count=len(beings),
                test_being_id=str(test_being.id),
            )

            for being in beings:
                logger.info("being_output", id=str(being.id), name=being.name)

        finally:
            # --- 4. ROLLBACK ---
            trans.rollback()
            logger.info("test_transaction_rolled_back")


def test_event_bus():
    logger.info("starting_event_bus_test")

    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    time.sleep(1)

    event = create_event(
        event_type="system.start.test",
        source="atlas.main",
        payload={"message": "Atlas system online"},
    )

    logger.info(
        "publishing_test_event",
        event_type=event.type,
        source=event.source,
    )

    publish(event=event)

    time.sleep(2)

    logger.info("event_bus_test_complete")


if __name__ == "__main__":
    main()


# docker compose --env-file ../.env up --build

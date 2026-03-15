from infrastructure.config import config
from infrastructure.logging import configure_logging, get_logger

from sqlalchemy import select

from infrastructure.session import get_session

from db.models.schemas.identity.being import Being
from db.models.schemas.account.user import User
from db.models.schemas.agents.agent import Agent
from db.models.schemas.agents.model import Model


def test_database():

    with get_session() as session:
        print("\n--- BEINGS ---")

        beings = session.execute(select(Being)).scalars().all()

        for being in beings:
            print(f"Being: {being.id} | {being.name}")

        print("\n--- USERS ---")

        users = session.execute(select(User)).scalars().all()

        for user in users:
            print(f"User: {user.username} | {user.email}")

        print("\n--- AGENTS ---")
        agents = session.execute(select(Agent)).scalars().all()

        for agent in agents:
            print(f"Agent: {agent.name} | Being ID: {agent.being_id}")

        print("\n--- MODELS ---")
        models = session.execute(select(Model)).scalars().all()

        for model in models:
            print(f"Model: {model.name} ({model.provider})")


configure_logging(
    level=config.get("logging.level"),
    console=config.get("logging.console"),
    json_logs=config.get("logging.json"),
    log_dir=config.get("logging.log_dir"),
)

log = get_logger("atlas.startup")

log.info("atlas_starting", environment=config.env)

log.debug("test_debug")

log.info(
    "config_loaded", database=config.get("database.name"), debug=config.get("app.debug")
)

log.error("test_error")

test_database()

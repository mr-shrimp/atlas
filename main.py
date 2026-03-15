from infrastructure.config import config
from infrastructure.logging import configure_logging, get_logger

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

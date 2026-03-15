from infrastructure.logging import configure_logging, get_logger

# SET UP LOGGING
configure_logging(debug=True)
logger = get_logger(__name__)
logger.info("atlas_starting")
logger.error("error_occured")
logger.critical("critical_error")
logger.debug("debug_test")

# EXAMPLE AGENT LOGGER
agent_logger = get_logger("agent").bind(agent_id="news_scanner", department="news")
agent_logger.info("scan_started")

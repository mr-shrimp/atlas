import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def configure_logging(
    level: str = "INFO",
    console: bool = True,
    json_logs: bool = False,
    log_dir: str = "logs",
):
    """
    Configure Atlas logging system.

    Supports:
        - Console logging (optional)
        - JSON or human-readable console output
        - Rotating file logs
        - Separate error log file
        - Structured logging using structlog

    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console (bool): Enable console logging
        json_logs (bool): Use JSON format for console logs
        log_dir (str): Directory for log files
    """

    # Create log directory
    log_directory = Path(log_dir)
    log_directory.mkdir(parents=True, exist_ok=True)

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Choose console renderer
    if json_logs:
        console_renderer = structlog.processors.JSONRenderer()
    else:
        console_renderer = structlog.dev.ConsoleRenderer()

    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=console_renderer,
        foreign_pre_chain=shared_processors,
    )

    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # Main log file
    file_handler = RotatingFileHandler(
        log_directory / "atlas.log",
        maxBytes=10_000_000,
        backupCount=5,
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Error log file
    error_handler = RotatingFileHandler(
        log_directory / "errors.log",
        maxBytes=10_000_000,
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)


def get_logger(name: str = None):
    """
    Return a structured logger instance.

    Args:
        name (str): Logger name

    Returns:
        structlog.BoundLogger
    """
    return structlog.get_logger(name)

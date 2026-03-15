import logging
import sys
import structlog
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def configure_logging(debug: bool = True):
    """
    Set up application-wide logging using structlog and the standard logging module.

    This function configures logging handlers for:
      - Console output (human-readable if debug is True, JSON if False)
      - Rotating file logging (JSON format)
      - Rotating error file logging (JSON format, only for errors and above)

    Log processors add structured context, timestamps, log levels, stack info, and exception formatting.
    Log files are rotated when they reach 10MB, keeping up to 5 backups.

    Args:
        debug (bool, optional): If True, enables debug-level logging and human-readable console output.
                               If False, sets info-level logging and JSON console output. Defaults to True.

    Raises:
        OSError: If log files cannot be created or written to.
    """
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

    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(),
        foreign_pre_chain=shared_processors,
    )

    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # CONSOLE
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # FILE
    file_handler = RotatingFileHandler(
        LOG_DIR / "atlas.log", maxBytes=10_000_000, backupCount=5
    )
    file_handler.setFormatter(file_formatter)

    # ERROR FILE
    error_handler = RotatingFileHandler(
        LOG_DIR / "errors.log", maxBytes=10_000_000, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)


def get_logger(name: str = None):
    """
    Creates and returns a structlog logger instance with the specified name.

    Args:
        name (str, optional): The name of the logger. Defaults to None.

    Returns:
        structlog.BoundLogger: A logger instance configured with the given name.
    """
    logger = structlog.get_logger(name)
    return logger

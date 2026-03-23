import subprocess
import threading
import time
from datetime import datetime, timezone

from sqlalchemy import text

import events.email_handlers  # noqa: F401
from infrastructure.bus.event_bus import get_redis, publish, subscribe
from infrastructure.bus.event_router import register, route_event
from infrastructure.bus.event_schema import Event, create_event
from infrastructure.config import config
from infrastructure.database import get_engine
from infrastructure.diagnostics.evaluator import evaluate
from infrastructure.diagnostics.health_registry import run_all_checks
from infrastructure.diagnostics.reporter import report_diagnostics
from infrastructure.logging import configure_logging, get_logger
from services.alert_service import evaluate_system_health

SEND_TEST_EMAIL: bool = True

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


def run_start_up_diagnostics():
    import infrastructure.diagnostics.health_checks.database_check  # noqa
    import infrastructure.diagnostics.health_checks.logging_check  # noqa
    import infrastructure.diagnostics.health_checks.redis_check  # noqa

    results = run_all_checks()
    report = evaluate(results)

    return report


def main():
    run_migrations()

    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    report = run_start_up_diagnostics()

    send_startup_email(report)

    report_diagnostics(report)

    time.sleep(1)

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


def send_startup_email(report: dict):
    event = create_event(
        event_type="email.send",
        source="atlas.startup",
        payload={
            "to": config.get("email.default_email_to"),
            "subject": f"[Atlas] System Online ({config.env.upper()})",
            "template": "system_startup.html",
            "context": {
                "environment": config.env,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "main.py",
                "services": report["services"],
                "severity": report["severity"],
                "status": report["status"],
            },
        },
    )

    publish(event)


if __name__ == "__main__":
    main()


# docker compose --env-file ../.env up --build

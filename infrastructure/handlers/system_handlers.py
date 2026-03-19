from infrastructure.bus.event_router import register
from infrastructure.bus.event_schema import Event
from infrastructure.logging import get_logger

logger = get_logger(__name__)


@register("system.start")
def handler_system_start(event: Event):
    logger.info("system_started", message=event.payload.message, source=event.source)

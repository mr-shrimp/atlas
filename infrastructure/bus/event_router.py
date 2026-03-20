from infrastructure.logging import get_logger

logger = get_logger(__name__)

ROUTES = {}


def register(event_type: str):
    """Decorator to register an event handler for a specific event type.
    This decorator registers a function as a handler for the specified event type
    in the ROUTES dictionary, enabling the event router to dispatch events to
    the appropriate handler functions.
    Args:
        event_type (str): The type of event to register the handler for.
    Returns:
        callable: A decorator function that registers the provided function
            as the handler for the specified event type and returns it unchanged.
    Example:
        @register('user.created')
        def handle_user_created(event):
            # Handle the user.created event
            pass
    """

    def decorator(fn):
        ROUTES[event_type] = fn
        return fn

    return decorator


def route_event(event: dict):
    """Routes an event to the appropriate handler based on the event type.
    Looks up the event type in the ROUTES dictionary and calls the corresponding
    handler function. If no handler is found for the event type, a warning is logged.
    Args:
        event (dict): The event dictionary containing at minimum a "type" key that
            identifies which handler should process the event.
    Returns:
        None
    Raises:
        AttributeError: If the handler is not callable or if the event is None.
        KeyError: If the handler raises a KeyError while processing the event.
    Note:
        A warning is logged if no handler is found for the given event type,
        but execution continues and the handler is still called (which may result
        in a NoneType error).
    """
    event_type = event.get("type")

    handler = ROUTES.get(event_type)

    if not handler:
        logger.warning("no_handler_found", event_type=event_type)
        return

    try:
        handler(event)
    except Exception as e:
        logger.error("event_handler_failure", event_type=event_type, error=str(e))

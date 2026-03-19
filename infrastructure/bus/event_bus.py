import json

import redis

from infrastructure.bus.event_schema import Event
from infrastructure.config import config
from infrastructure.logging import get_logger

logger = get_logger(__name__)
_redis = None


def get_redis():
    """
    Returns a singleton Redis client instance.
    If the Redis client does not exist, it initializes a new instance using
    configuration values for host and port, and sets decode_responses to True.
    Logs a message when a new connection is established.
    Returns:
        redis.Redis: The singleton Redis client instance.
    """

    global _redis

    if _redis is None:
        _redis = redis.Redis(
            host=config.env_var("REDIS_HOST"),
            port=config.env_var("REDIS_PORT"),
            decode_responses=True,
        )

        logger.info("redis_connected")

    return _redis


def publish(event: Event):
    """
    Publishes an event to the "atlas.events" Redis channel.

    Serializes the given event and sends it to the Redis event bus. Logs the publication
    with the event type and source.

    Args:
        event (Event): The event object to be published. Must have "type" and "source" attributes.

    Raises:
        KeyError: If the event does not contain the required "type" or "source" attributes.
        redis.exceptions.RedisError: If there is an error publishing to Redis.

    Logs:
        Logs the event publication with event type and source.
    """

    r = get_redis()

    r.publish("atlas.events", event.to_json())

    logger.info(
        "event_published",
        event_type=event.type,
        source=event.source,
    )


def subscribe(handler):
    """
    Subscribes a handler function to the "atlas.events" Redis channel and processes incoming events.
    Listens for messages published to the "atlas.events" channel using Redis Pub/Sub. For each message
    received, the event data is deserialized from JSON and passed to the provided handler function.
    Args:
        handler (Callable[[dict], None]): A function that takes a deserialized event dictionary as its only argument.
    Raises:
        redis.exceptions.ConnectionError: If unable to connect to the Redis server.
        json.JSONDecodeError: If a received message cannot be decoded from JSON.
    """

    r = get_redis()

    pubsub = r.pubsub()
    pubsub.subscribe("atlas.events")

    logger.info("event_bus_subscribed")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        event = json.loads(message["data"])

        handler(event)

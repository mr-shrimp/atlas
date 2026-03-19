import json
import uuid
from datetime import datetime, timezone


class Event:
    """
    Converts the Event instance into a dictionary.
    Returns:
        dict: A dictionary representation of the Event, containing the event ID, type, timestamp, source, and payload.
    """

    def __init__(self, event_type: str, source: str, payload: dict):
        self.event_id = str(uuid.uuid4())
        self.type = event_type
        self.timestamp = datetime.now(timezone.utc)
        self.source = source
        self.payload = payload

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "payload": self.payload,
        }


def create_event(event_type: str, source: str, payload: dict) -> Event:
    """
    Creates an Event object with a unique ID, type, timestamp, source, and payload.
    Args:
        event_type (str): The type of the event.
        source (str): The source of the event.
        payload (dict): The payload data associated with the event.
    Returns:
        Event: An Event object.
    """
    return Event(event_type, source, payload)

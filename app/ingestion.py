from typing import Any, Dict

from app.models import Event, create_event
from app.states import EventState

class IngestionResult:
    def __init__(self, accepted: bool, reason: str = ""):
        self.accepted = accepted
        self.reason = reason


def ingest_event(
    producer_timestamp: float,
    payload: Dict[str, Any],
) -> Event:
    """
    Ingests raw producer data and establishes the acceptance boundary.
    Once this function successfully returns, Chronos guarantees apply.
    """

    # Minimal validation (v1)
    if producer_timestamp <= 0:
        raise ValueError("Invalid producer timestamp")

    if payload is None:
        raise ValueError("Payload cannot be null")

    # Create event (state = RECEIVED)
    event = create_event(
        producer_timestamp=producer_timestamp,
        payload=payload,
    )

    # Acceptance boundary — guarantee starts here
    event.transition_to(EventState.ACCEPTED)

    return event

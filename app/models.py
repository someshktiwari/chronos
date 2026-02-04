from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from app.states import EventState, validate_transition

@dataclass
class Event:
    event_id: str
    producer_timestamp: float
    payload: Any
    state: EventState = field(default=EventState.RECEIVED)
    error_reason: Optional[str] = None

    def transition_to(self, new_state: EventState) -> None:
        validate_transition(self.state, new_state)
        self.state = new_state

    def mark_failed(self, reason: str, terminal: bool = False) -> None:
        self.error_reason = reason
        if terminal:
            self.transition_to(EventState.FAILED_TERMINAL)
        else:
            self.transition_to(EventState.FAILED_RETRYABLE)

def create_event(
    producer_timestamp: float,
    payload: Any,
) -> Event:
    return Event(
        event_id=str(uuid4()),
        producer_timestamp=producer_timestamp,
        payload=payload,
    )

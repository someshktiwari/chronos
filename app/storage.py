from typing import List

from app.models import Event
from app.states import EventState

class InMemoryStorage:
    def __init__(self) -> None:
        self._events: List[Event] = []

    def persist(self, event: Event) -> None:
        if event.state != EventState.PROCESSED:
            raise ValueError(
                f"Storage can only persist PROCESSED events, got {event.state.name}"
            )

        # Storage does NOT mutate state
        self._events.append(event)


    def all_events(self) -> List[Event]:
        return list(self._events)

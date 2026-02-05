from typing import Callable

from app.buffer import EventBuffer
from app.models import Event
from app.states import EventState

class Worker:
    def __init__(self, buffer: EventBuffer, processor: Callable[[Event], None]) -> None:
        self._buffer = buffer
        self._processor = processor

    def process_once(self) -> None:
        event = self._buffer.dequeue()
        if event is None:
            return

        if event.state != EventState.BUFFERED:
            raise ValueError(
                f"Worker can only process BUFFERED events, got {event.state.name}"
            )

        # Worker owns this transition
        event.transition_to(EventState.PROCESSING)

        try:
            self._processor(event)
            event.transition_to(EventState.PROCESSED)

        except Exception as exc:
            # Default behavior: retryable failure
            event.mark_failed(
                reason=str(exc),
                terminal=False,
            )

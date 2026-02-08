from typing import Callable, Optional

from app.buffer import EventBuffer
from app.models import Event
from app.states import EventState


class Worker:
    def __init__(
        self,
        buffer: EventBuffer,
        processor: Callable[[Event], None],
    ) -> None:
        self._buffer = buffer
        self._processor = processor

    def process_once(self) -> Optional[Event]:
        event = self._buffer.dequeue()
        if event is None:
            return None

        if event.state != EventState.BUFFERED:
            raise ValueError(
                f"Worker can only process BUFFERED events, got {event.state.name}"
            )

        self._process_event(event)
        return event

    def _process_event(self, event: Event) -> None:
        # ===== First attempt =====
        event.transition_to(EventState.PROCESSING)

        try:
            self._processor(event)
            event.transition_to(EventState.PROCESSED)
            return

        except Exception as exc:
            # First failure → retryable
            event.mark_failed(reason=str(exc), terminal=False)

        # ===== Retry attempt =====
        event.transition_to(EventState.PROCESSING)

        try:
            self._processor(event)
            event.transition_to(EventState.PROCESSED)

        except Exception as exc:
            # Second failure → retryable again
            event.mark_failed(reason=str(exc), terminal=False)

            # Explicit escalation (RFC rule)
            event.transition_to(EventState.FAILED_TERMINAL)

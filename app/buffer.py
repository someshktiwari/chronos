from collections import deque
from typing import Deque, Optional

from app.models import Event
from app.states import EventState

class EventBuffer:
    def __init__(self) -> None:
        self._queue: Deque[Event] = deque()

    def enqueue(self, event: Event) -> None:
        if event.state != EventState.ACCEPTED:
            raise ValueError(
                f"Only ACCEPTED events can be buffered, got {event.state.name}"
            )

        # Buffer owns this transition
        event.transition_to(EventState.BUFFERED)
        self._queue.append(event)

    def dequeue(self) -> Optional[Event]:
        if not self._queue:
            return None

        return self._queue.popleft()


    def size(self) -> int:
        return len(self._queue)

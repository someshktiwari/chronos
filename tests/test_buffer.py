import pytest
from app.buffer import EventBuffer
from app.models import create_event
from app.states import EventState

def test_buffer_rejects_non_accepted_events():
    buffer = EventBuffer()
    event = create_event(123.0, {"x": 1})  # RECEIVED

    with pytest.raises(ValueError):
        buffer.enqueue(event)

def test_buffer_accepts_accepted_event():
    buffer = EventBuffer()
    event = create_event(123.0, {"x": 1})
    event.transition_to(EventState.ACCEPTED)

    buffer.enqueue(event)
    assert event.state == EventState.BUFFERED

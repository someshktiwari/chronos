from app.buffer import EventBuffer
from app.worker import Worker
from app.models import create_event
from app.states import EventState

def test_worker_processes_buffered_event():
    buffer = EventBuffer()
    event = create_event(123.0, {"x": 1})
    event.transition_to(EventState.ACCEPTED)
    buffer.enqueue(event)

    worker = Worker(buffer, lambda e: None)
    worker.process_once()

    assert event.state == EventState.PROCESSED

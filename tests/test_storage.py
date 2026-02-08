import pytest
from app.storage import InMemoryStorage
from app.models import create_event
from app.states import EventState

def test_storage_rejects_non_processed_event():
    storage = InMemoryStorage()
    event = create_event(123.0, {"x": 1})

    with pytest.raises(ValueError):
        storage.persist(event)

def test_storage_persists_processed_event():
    storage = InMemoryStorage()
    event = create_event(123.0, {"x": 1})
    event.transition_to(EventState.ACCEPTED)
    event.transition_to(EventState.BUFFERED)
    event.transition_to(EventState.PROCESSING)
    event.transition_to(EventState.PROCESSED)

    storage.persist(event)
    assert len(storage.all_events()) == 1

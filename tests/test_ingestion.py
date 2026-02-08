from app.ingestion import ingest_event
from app.states import EventState

def test_event_is_accepted_on_ingestion():
    event = ingest_event(123.0, {"x": 1})
    assert event.state == EventState.ACCEPTED

from app.ingestion import ingest_event
from app.buffer import EventBuffer
from app.worker import Worker
from app.storage import InMemoryStorage
from app.models import Event
from app.states import EventState


def example_processor(event: Event) -> None:
    # Simulated processing logic
    # Real systems would transform / validate / enrich data here
    if not event.payload:
        raise ValueError("Invalid payload")

def main():
    buffer = EventBuffer()
    storage = InMemoryStorage()

    worker = Worker(
        buffer=buffer,
        processor=example_processor
    )


    # Ingest event (acceptance boundary)
    event = ingest_event(
        producer_timestamp=1234567890.0,
        payload={"speed": 320, "rpm": 12000}
    )

    # Buffer the accepted event
    buffer.enqueue(event)

    # Process one event
    worker.process_once()

    # Persist only if processed
    if event.state == EventState.PROCESSED:
        storage.persist(event)

    # Verify outcome
    print("Final event state:", event.state)
    print("Stored events:", storage.all_events())


if __name__ == "__main__":
    main()

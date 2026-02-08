import time
import random

from app.ingestion import ingest_event
from app.buffer import EventBuffer
from app.worker import Worker
from app.storage import InMemoryStorage
from app.models import Event
from app.states import EventState


def example_processor(event: Event) -> None:
    """
    Simulated processing logic.
    Intentionally slow and occasionally failing
    to demonstrate buffering and retries.
    """
    time.sleep(0.3)

    if random.random() < 0.2:
        raise ValueError("Simulated processing failure")


def main():
    buffer = EventBuffer()
    storage = InMemoryStorage()

    worker = Worker(
        buffer=buffer,
        processor=example_processor,
    )

    print("Starting Chronos simulation...\n")

    # Producer loop (fast)
    for i in range(10):
        event = ingest_event(
            producer_timestamp=time.time(),
            payload={"event_number": i, "speed": random.randint(200, 350)},
        )

        buffer.enqueue(event)
        print(f"[PRODUCER] Ingested event {event.event_id} (state={event.state.name})")

        time.sleep(0.05)

    print("\n--- Processing loop starts ---\n")

    # Consumer loop (slow)
    while buffer.size() > 0:
        event = worker.process_once()

        if event and event.state == EventState.PROCESSED:
            storage.persist(event)
            print(f"[STORAGE] Persisted event {event.event_id}")

        print(
            f"[STATUS] Buffer size={buffer.size()} | "
            f"Stored={len(storage.all_events())}"
        )

        time.sleep(0.1)

    print("\nSimulation complete.")
    print(f"Total persisted events: {len(storage.all_events())}")


if __name__ == "__main__":
    main()

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
    Intentionally fails sometimes to demonstrate
    retry and terminal failure behavior.
    """
    time.sleep(0.2)

    # Increase probability temporarily to force failures for demo
    if random.random() < 0.6:
        raise ValueError("Simulated processing failure")


def main():
    buffer = EventBuffer()
    storage = InMemoryStorage()
    all_events: list[Event] = []

    worker = Worker(
        buffer=buffer,
        processor=example_processor,
    )

    print("Starting Chronos simulation...\n")

    # ---------- Producer loop (fast) ----------
    for i in range(10):
        event = ingest_event(
            producer_timestamp=time.time(),
            payload={"event_number": i, "speed": random.randint(200, 350)},
        )

        all_events.append(event)
        buffer.enqueue(event)

        print(
            f"[PRODUCER] Ingested event {event.event_id} "
            f"(state={event.state.name})"
        )

        time.sleep(0.05)

    print("\n--- Processing loop starts ---\n")

    # ---------- Consumer loop (slow) ----------
    while buffer.size() > 0:
        event = worker.process_once()
        if event is None:
            continue

        if event.state == EventState.PROCESSED:
            storage.persist(event)
            print(f"[STORAGE] Persisted event {event.event_id}")

        elif event.state == EventState.FAILED_TERMINAL:
            print(
                f"[FAILURE] Event {event.event_id} "
                f"entered FAILED_TERMINAL (reason={event.error_reason})"
            )

        print(
            f"[STATUS] Buffer size={buffer.size()} | "
            f"Stored={len(storage.all_events())}"
        )

        time.sleep(0.1)

    # ---------- Final summary ----------
    processed = [e for e in all_events if e.state == EventState.PROCESSED]
    failed = [e for e in all_events if e.state == EventState.FAILED_TERMINAL]
    retried = [e for e in all_events if e.error_reason is not None]

    print("\n--- Final Summary ---")
    print(f"Total events ingested   : {len(all_events)}")
    print(f"Processed successfully : {len(processed)}")
    print(f"Retried at least once   : {len(retried)}")
    print(f"Terminal failures       : {len(failed)}")

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()

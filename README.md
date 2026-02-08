# Chronos

Chronos is a backend system for ingesting and processing time-ordered telemetry data in environments where producers and consumers operate at different and unpredictable speeds.

The system is intentionally small and rigorously defined. It focuses on **explicit guarantees, clear ownership boundaries, and failure semantics**, rather than infrastructure scale or real-time promises.

---

## Core Guarantee

Once an event is accepted by Chronos, its fate is never silent.

An accepted event is guaranteed to reach one of the following explicit outcomes:
- Processed successfully, or
- Failed explicitly (retryable or terminal)

Chronos prioritizes **data integrity and observability** over latency or availability.

---

## Problem Statement

In real-world backend systems, data ingestion and data processing often operate at mismatched speeds:

- Telemetry streams may arrive in bursts
- Producers may outpace consumers
- Consumers may slow down or fail independently

These conditions frequently lead to:
- Backpressure issues
- Silent data loss
- Implicit or undefined failure behavior

Chronos explores how to design a system that:
- Decouples ingestion from processing
- Preserves data integrity under load
- Makes failures explicit and explainable
- Avoids hidden or implicit behavior

---

## High-Level Architecture

Chronos is structured as a simple pipeline with clearly defined responsibilities:

Producer → Ingestion → Buffer → Worker → Storage

Each component owns a specific part of the event lifecycle and enforces explicit state transitions.

```mermaid
flowchart LR
    P[Producer]
    I[Ingestion]
    B[Buffer]
    W[Worker]
    S[Storage]

    P --> I
    I -->|ACCEPTED| B
    B -->|BUFFERED| W
    W -->|PROCESSED| S
````

---

## Component Responsibilities

### Ingestion (Acceptance Boundary)

* Receives raw data from producers
* Performs minimal validation
* Establishes the **acceptance boundary**
* Transitions events from `RECEIVED → ACCEPTED`

Chronos guarantees begin **only after an event is accepted**.
Events that fail to reach or cross this boundary are out of scope.

---

### Buffer

* Temporarily holds accepted events
* Decouples producer speed from consumer speed
* Owns the transition `ACCEPTED → BUFFERED`
* Preserves FIFO ordering on a best-effort basis

The buffer absorbs bursty load and prevents ingestion from blocking on downstream processing.

---

### Worker

* Dequeues buffered events
* Owns processing transitions:

  * `BUFFERED → PROCESSING`
  * `PROCESSING → PROCESSED` or `FAILED`
* Handles failures explicitly as retryable or terminal
* Does not hide, swallow, or auto-retry failures

All processing logic is isolated within the worker.

---

### Storage

* Persists only successfully processed events
* Accepts events exclusively in the `PROCESSED` state
* Does not mutate event state
* Acts as a terminal sink, not a coordinator

Storage is intentionally kept simple to preserve ownership clarity.

---

## Event Lifecycle

Chronos models each event using an explicit state machine.

Every state transition:

* Has a single owning component
* Is enforced in code
* Is observable and intentional

Terminal states cannot be exited.

```mermaid
stateDiagram-v2
    RECEIVED --> ACCEPTED
    ACCEPTED --> BUFFERED
    BUFFERED --> PROCESSING
    PROCESSING --> PROCESSED
    PROCESSING --> FAILED_RETRYABLE
    FAILED_RETRYABLE --> PROCESSING
    PROCESSED --> [*]
    FAILED_TERMINAL --> [*]
```

---

## Design Principles

* **Explicit over implicit**
  All behavior, transitions, and failures are intentional and visible.

* **Clear ownership boundaries**
  Each component owns exactly one segment of the event lifecycle.

* **Correctness before scale**
  Chronos v1 prioritizes reasoning and guarantees over throughput claims.

* **Fail fast, fail visibly**
  Silent data loss is treated as a system failure.

---

## Non-Goals

Chronos v1 intentionally does not attempt to provide:

* Real-time or low-latency guarantees
* Exactly-once delivery semantics
* Global ordering across producers
* Infinite or unbounded scalability

These tradeoffs are explicit and documented.

---

## Running the System

From the project root, run:

```
python -m app.main
```

This executes a minimal end-to-end pipeline:

Ingestion → Buffer → Worker → Storage

---

## Simulation Behavior

Chronos includes a deterministic producer–consumer simulation designed to demonstrate system behavior under load.

In the simulation:
- The producer intentionally generates events faster than the worker can process them.
- The buffer absorbs bursty load without blocking ingestion.
- The worker processes one event at a time, with explicit retry semantics on failure.
- Storage persists only terminal success states and never mutates event state.

This allows the system to degrade predictably by increasing latency and backlog, rather than silently dropping or corrupting data.


## Testing

Chronos includes invariant-focused tests that enforce:

* Illegal state transitions fail
* Ownership boundaries are respected
* Storage only persists terminal success states

Run all tests with:

```
pytest
```

---

## Why This Project Exists

Chronos was built as a learning and reasoning artifact, not as a production service.

The goal is to deeply understand:

* Backend system guarantees
* Failure handling under load
* Tradeoffs between throughput, latency, and reliability

---

## Summary

Chronos demonstrates how a small, disciplined system can:

* Make strong guarantees
* Fail predictably
* Remain explainable under pressure

**Status:** Chronos v1 is complete and frozen.  
* Future work (durability, UDP ingestion, Redis buffering) will be explored in v2.

from enum import Enum, auto


class EventState(Enum):
    RECEIVED = auto()
    ACCEPTED = auto()
    BUFFERED = auto()
    PROCESSING = auto()
    PROCESSED = auto()          # terminal success
    FAILED_RETRYABLE = auto()
    FAILED_TERMINAL = auto()    # terminal failure

LEGAL_STATE_TRANSITIONS = {
    EventState.RECEIVED: {EventState.ACCEPTED},
    EventState.ACCEPTED: {EventState.BUFFERED},
    EventState.BUFFERED: {EventState.PROCESSING},
    EventState.PROCESSING: {
        EventState.PROCESSED,
        EventState.FAILED_RETRYABLE,
    },
    EventState.FAILED_RETRYABLE: {EventState.PROCESSING},
    EventState.PROCESSED: set(),         # terminal
    EventState.FAILED_TERMINAL: set(),    # terminal
}

def is_valid_transition(from_state: EventState, to_state: EventState) -> bool:
    allowed = LEGAL_STATE_TRANSITIONS.get(from_state, set())
    return to_state in allowed

def validate_transition(from_state: EventState, to_state: EventState) -> None:
    if not is_valid_transition(from_state, to_state):
        raise ValueError(
            f"Illegal state transition: {from_state.name} → {to_state.name}"
        )

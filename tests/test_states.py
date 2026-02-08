import pytest
from app.states import EventState, validate_transition

def test_illegal_transition_raises():
    with pytest.raises(ValueError):
        validate_transition(EventState.RECEIVED, EventState.PROCESSING)

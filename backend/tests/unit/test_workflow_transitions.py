import pytest

from app.domain.workflow import RequestStatus, can_transition


def test_linear_lifecycle_allows_only_next_state():
    assert can_transition(RequestStatus.OPEN, RequestStatus.ASSIGNED)
    assert can_transition(RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS)
    assert can_transition(RequestStatus.IN_PROGRESS, RequestStatus.RESOLVED)
    assert can_transition(RequestStatus.RESOLVED, RequestStatus.CLOSED)


@pytest.mark.parametrize(
    ("current", "requested"),
    [
        (RequestStatus.OPEN, RequestStatus.RESOLVED),
        (RequestStatus.ASSIGNED, RequestStatus.CLOSED),
        (RequestStatus.IN_PROGRESS, RequestStatus.ASSIGNED),
        (RequestStatus.CLOSED, RequestStatus.OPEN),
    ],
)
def test_shortcut_and_backward_transitions_are_rejected(current, requested):
    assert not can_transition(current, requested)

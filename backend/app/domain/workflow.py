from .models import RequestStatus


def can_transition(current: RequestStatus, requested: RequestStatus) -> bool:
    transitions = {
        RequestStatus.OPEN: RequestStatus.ASSIGNED,
        RequestStatus.ASSIGNED: RequestStatus.IN_PROGRESS,
        RequestStatus.IN_PROGRESS: RequestStatus.RESOLVED,
        RequestStatus.RESOLVED: RequestStatus.CLOSED,
    }
    return transitions.get(current) == requested
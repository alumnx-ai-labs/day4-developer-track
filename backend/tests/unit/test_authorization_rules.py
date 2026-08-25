from app.application.authorization import Action, Role, UserContext, is_allowed


def test_role_permissions_are_resource_scoped():
    requester = UserContext(user_id=1, role=Role.REQUESTER)
    assignee = UserContext(user_id=2, role=Role.ASSIGNEE)
    lead = UserContext(user_id=3, role=Role.TEAM_LEAD)
    approver = UserContext(user_id=4, role=Role.APPROVER)

    assert is_allowed(requester, Action.CREATE, created_by_id=1)
    assert is_allowed(assignee, Action.UPDATE_STATUS, assigned_to_id=2)
    assert not is_allowed(assignee, Action.UPDATE_STATUS, assigned_to_id=9)
    assert is_allowed(lead, Action.UPDATE_OWNER)
    assert is_allowed(approver, Action.UPDATE_PRIORITY)
    assert not is_allowed(approver, Action.UPDATE_OWNER)
    assert not is_allowed(requester, Action.UPDATE_PRIORITY)

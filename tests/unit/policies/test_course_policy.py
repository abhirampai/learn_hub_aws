import pytest

from core.exceptions import ForbiddenActionError
from models.authenticated_user import AuthenticatedUser
from policies.course_policy import CoursePolicy


def authenticated_user(role: str) -> AuthenticatedUser:
    return AuthenticatedUser(
        id="user_123",
        cognito_sub="cognito-sub-123",
        email="user@example.com",
        display_name="Test User",
        role=role,
        status="active",
        avatar_url=None,
    )


@pytest.mark.parametrize("role", ["instructor", "admin"])
def test_authorize_create_allows_creator_roles(role: str) -> None:
    policy = CoursePolicy(authenticated_user(role))

    assert policy.authorize_create() is None


@pytest.mark.parametrize("role", ["student", "viewer", ""])
def test_authorize_create_rejects_non_creator_roles(role: str) -> None:
    policy = CoursePolicy(authenticated_user(role))

    with pytest.raises(ForbiddenActionError) as exc_info:
        policy.authorize_create()

    assert exc_info.value.action == "create"
    assert exc_info.value.resource == "course"
    assert str(exc_info.value) == "User is not allowed to create course"

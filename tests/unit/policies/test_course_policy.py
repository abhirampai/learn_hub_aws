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


def course(instructor_id: str = "user_123") -> dict:
    return {"instructor_id": instructor_id}


def test_authorize_update_allows_admin() -> None:
    policy = CoursePolicy(authenticated_user("admin"), course("another-user"))

    assert policy.authorize_update() is None


def test_authorize_update_allows_course_instructor() -> None:
    policy = CoursePolicy(authenticated_user("instructor"), course("user_123"))

    assert policy.authorize_update() is None


@pytest.mark.parametrize(
    ("role", "instructor_id"),
    [
        ("instructor", "another-user"),
        ("student", "user_123"),
        ("viewer", "user_123"),
    ],
)
def test_authorize_update_rejects_unauthorized_user(
    role: str, instructor_id: str
) -> None:
    policy = CoursePolicy(authenticated_user(role), course(instructor_id))

    with pytest.raises(ForbiddenActionError) as exc_info:
        policy.authorize_update()

    assert exc_info.value.action == "update"
    assert exc_info.value.resource == "course"
    assert str(exc_info.value) == "User is not allowed to update course"


def test_authorize_update_requires_course() -> None:
    policy = CoursePolicy(authenticated_user("admin"))

    with pytest.raises(ValueError, match="Course is required"):
        policy.authorize_update()

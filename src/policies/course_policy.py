from typing import Any

from core.exceptions import ForbiddenActionError
from models.authenticated_user import AuthenticatedUser


class CoursePolicy:
    CREATOR_ROLES = {"instructor", "admin"}

    def __init__(self, user: AuthenticatedUser, course: dict[str, Any] | None = None) -> None:
        self.user = user
        self.course = course

    def authorize_create(self) -> None:
        if self.user.role not in self.CREATOR_ROLES:
            self._forbid("create")

    def authorize_update(self) -> None:
        if self.course is None:
            raise ValueError("Course is required for update authorization")

        is_admin = self.user.role == "admin"
        is_course_instructor = (
            self.user.role == "instructor" and self.course["instructor_id"] == self.user.id
        )

        if is_admin or is_course_instructor:
            return

        self._forbid("update")

    def _forbid(self, action: str) -> None:
        raise ForbiddenActionError(
            action=action,
            resource="course",
        )

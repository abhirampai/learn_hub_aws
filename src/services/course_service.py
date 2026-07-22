from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from core.constants import COURSE_STATUS_DRAFT
from core.exceptions import CourseNotFoundError
from models.authenticated_user import AuthenticatedUser
from policies.course_policy import CoursePolicy
from utils.slugify import slugify


class CourseService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_course(self, current_user: AuthenticatedUser, payload: dict) -> dict:
        CoursePolicy(current_user).authorize_create()

        now = datetime.now(UTC).isoformat()

        course = {
            "id": f"course_{uuid4()}",
            "instructor_id": current_user.id,
            "title": payload["title"],
            "description": payload["description"],
            "difficulty": payload["difficulty"],
            "tags": payload.get("tags", []),
            "slug": slugify(payload["title"]),
            "thumbnail_url": None,
            "status": COURSE_STATUS_DRAFT,
            "created_at": now,
            "updated_at": now,
        }

        return self.repository.create(course)

    def update_course(
        self,
        current_user: AuthenticatedUser,
        slug: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        course = self.repository.find_by_slug(slug)

        if course is None:
            raise CourseNotFoundError(slug)

        CoursePolicy(user=current_user, course=course).authorize_update()

        updated_course = {
            **course,
            **updates,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        return self.repository.update(updated_course)

from datetime import UTC, datetime
from uuid import uuid4

from core.constants import COURSE_STATUS_DRAFT
from policies.course_policy import CoursePolicy
from utils.slugify import slugify


class CourseService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_course(self, current_user, payload: dict) -> dict:
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

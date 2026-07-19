from datetime import UTC, datetime
from uuid import uuid4

from core.constants import COURSE_STATUS_DRAFT
from utils.slugify import slugify


class CourseService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_course(self, payload: dict) -> dict:
        now = datetime.now(UTC).isoformat()
        course = {
            "id": f"course_{uuid4()}",
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

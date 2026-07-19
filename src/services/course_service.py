import uuid
from core.exceptions import DuplicateCourseError
from utils.slugify import slugify
from datetime import datetime, UTC


class CourseService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_course(self, payload: dict) -> dict:
        course = {
            "id": f"course_#{uuid.uuid4()}",
            "title": payload["title"],
            "description": payload["description"],
            "difficulty": payload["difficulty"],
            "tags": payload.get("tags", []),
            "slug": slugify(payload["title"]),
            "thumbnail_url": None,
            "status": "draft",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

        self.repository.create(course)
        return course

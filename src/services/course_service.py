from utils.slugify import slugify
from datetime import datetime, UTC

COURSES = []


class CourseService:
    def __init__(self) -> None:
        self._courses = []

    def create_course(self, payload: dict) -> dict:
        course = {
            "id": f"course_{len(COURSES) + 1}",
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

        self._courses.append(course)
        return course

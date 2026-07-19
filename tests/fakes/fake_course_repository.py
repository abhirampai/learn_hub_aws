from copy import deepcopy

from core.exceptions import DuplicateCourseError


class FakeCourseRepository:
    def __init__(self) -> None:
        self.courses_by_slug: dict[str, dict] = {}

    def create(self, course: dict) -> dict:
        slug = course["slug"]
        if slug in self.courses_by_slug:
            raise DuplicateCourseError(slug)

        stored_course = deepcopy(course)
        self.courses_by_slug[slug] = stored_course
        return deepcopy(stored_course)

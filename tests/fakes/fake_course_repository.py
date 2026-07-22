from copy import deepcopy

from core.exceptions import CourseNotFoundError, DuplicateCourseError


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

    def find_by_slug(self, slug: str) -> dict | None:
        course = self.courses_by_slug.get(slug)
        return deepcopy(course) if course is not None else None

    def update(self, course: dict) -> dict:
        slug = course["slug"]
        if slug not in self.courses_by_slug:
            raise CourseNotFoundError(slug)

        stored_course = deepcopy(course)
        self.courses_by_slug[slug] = stored_course
        return deepcopy(stored_course)

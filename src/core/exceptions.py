class DuplicateCourseError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Course already exists: {slug}")


class CourseNotFoundError(Exception):
    pass


class UnauthorizedCourseAccessError(Exception):
    pass

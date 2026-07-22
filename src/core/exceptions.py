class DuplicateCourseError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Course already exists: {slug}")

class UserProvisioningPendingError(Exception):
    def __init__(self, sub: str) -> None:
        self.sub = sub
        super().__init__(f"User provisioning is pending: {sub}")


class InactiveUserError(Exception):
    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(f"User is not active: {status}")

class CourseNotFoundError(Exception):
    pass


class UnauthorizedCourseAccessError(Exception):
    pass

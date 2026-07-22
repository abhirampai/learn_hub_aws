from core.exceptions import ForbiddenActionError
from models.authenticated_user import AuthenticatedUser


class CoursePolicy:
    CREATOR_ROLES = {"instructor", "admin"}

    def __init__(self, user: AuthenticatedUser) -> None:
        self.user = user

    def authorize_create(self) -> None:
        if self.user.role not in self.CREATOR_ROLES:
            raise ForbiddenActionError(
                action="create",
                resource="course",
            )

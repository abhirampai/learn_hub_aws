from core.cognito_identity import CognitoIdentity
from core.exceptions import InactiveUserError, UserProvisioningPendingError
from models.authenticated_user import AuthenticatedUser


class AuthenticationService:
    def __init__(self, user_repository) -> None:
        self.user_repository = user_repository

    def authenticate(
        self,
        identity: CognitoIdentity,
    ) -> AuthenticatedUser:
        user = self.user_repository.find_by_sub(identity.sub)

        if user is None:
            raise UserProvisioningPendingError(identity.sub)

        if user["status"] != "active":
            raise InactiveUserError(user["status"])

        return AuthenticatedUser(
            id=user["id"],
            cognito_sub=user["cognito_sub"],
            email=user["email"],
            display_name=user.get("display_name"),
            role=user["role"],
            status=user["status"],
            avatar_url=user.get("avatar_url"),
        )

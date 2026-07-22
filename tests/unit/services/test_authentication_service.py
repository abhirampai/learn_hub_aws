from unittest.mock import Mock

import pytest

from core.cognito_identity import CognitoIdentity
from core.exceptions import InactiveUserError, UserProvisioningPendingError
from models.authenticated_user import AuthenticatedUser
from services.authentication_service import AuthenticationService


@pytest.fixture
def repository() -> Mock:
    return Mock()


@pytest.fixture
def service(repository: Mock) -> AuthenticationService:
    return AuthenticationService(repository)


@pytest.fixture
def identity() -> CognitoIdentity:
    return CognitoIdentity(
        sub="cognito-sub-123",
        email="identity@example.com",
    )


@pytest.fixture
def active_user() -> dict:
    return {
        "id": "user_123",
        "cognito_sub": "cognito-sub-123",
        "email": "profile@example.com",
        "display_name": "Learner",
        "role": "student",
        "status": "active",
        "avatar_url": "https://example.com/avatar.png",
    }


def test_authenticate_returns_user_profile(
    service: AuthenticationService,
    repository: Mock,
    identity: CognitoIdentity,
    active_user: dict,
) -> None:
    repository.find_by_sub.return_value = active_user

    result = service.authenticate(identity)

    repository.find_by_sub.assert_called_once_with(identity.sub)
    assert result == AuthenticatedUser(
        id="user_123",
        cognito_sub="cognito-sub-123",
        email="profile@example.com",
        display_name="Learner",
        role="student",
        status="active",
        avatar_url="https://example.com/avatar.png",
    )


def test_authenticate_defaults_optional_profile_fields_to_none(
    service: AuthenticationService,
    repository: Mock,
    identity: CognitoIdentity,
    active_user: dict,
) -> None:
    repository.find_by_sub.return_value = {
        key: value
        for key, value in active_user.items()
        if key not in {"display_name", "avatar_url"}
    }

    result = service.authenticate(identity)

    assert result.display_name is None
    assert result.avatar_url is None


def test_authenticate_raises_when_user_provisioning_is_pending(
    service: AuthenticationService,
    repository: Mock,
    identity: CognitoIdentity,
) -> None:
    repository.find_by_sub.return_value = None

    with pytest.raises(UserProvisioningPendingError) as exc_info:
        service.authenticate(identity)

    repository.find_by_sub.assert_called_once_with(identity.sub)
    assert exc_info.value.sub == identity.sub


@pytest.mark.parametrize("status", ["pending", "disabled", "suspended"])
def test_authenticate_rejects_inactive_user(
    service: AuthenticationService,
    repository: Mock,
    identity: CognitoIdentity,
    active_user: dict,
    status: str,
) -> None:
    repository.find_by_sub.return_value = {**active_user, "status": status}

    with pytest.raises(InactiveUserError) as exc_info:
        service.authenticate(identity)

    repository.find_by_sub.assert_called_once_with(identity.sub)
    assert exc_info.value.status == status

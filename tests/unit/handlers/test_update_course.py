import json
import os
from unittest.mock import Mock, patch

import pytest

from core.exceptions import (
    CourseNotFoundError,
    ForbiddenActionError,
    InactiveUserError,
    UserProvisioningPendingError,
)
from models.authenticated_user import AuthenticatedUser

os.environ.setdefault("TABLE_NAME", "learn-hub-test")

with patch("boto3.resource"):
    from handlers import update_course


@pytest.fixture
def event() -> dict:
    return {
        "body": json.dumps(
            {
                "description": "Updated course description.",
                "tags": ["aws", "updated"],
            }
        ),
        "pathParameters": {"slug": "aws-fundamentals"},
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "cognito-sub-123",
                    "email": "instructor@example.com",
                }
            }
        },
    }


@pytest.fixture
def current_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id="user_123",
        cognito_sub="cognito-sub-123",
        email="instructor@example.com",
        display_name="Instructor",
        role="instructor",
        status="active",
        avatar_url=None,
    )


def test_update_course_returns_updated_course(event: dict, current_user: AuthenticatedUser) -> None:
    authentication_service = Mock()
    authentication_service.authenticate.return_value = current_user
    course_service = Mock()
    course = {
        "id": "course_123",
        "slug": "aws-fundamentals",
        "description": "Updated course description.",
    }
    course_service.update_course.return_value = course

    with (
        patch.object(update_course, "authentication_service", authentication_service),
        patch.object(update_course, "course_service", course_service),
    ):
        response = update_course.lambda_handler(event, None)

    identity = authentication_service.authenticate.call_args.args[0]
    assert identity.sub == "cognito-sub-123"
    course_service.update_course.assert_called_once_with(
        current_user=current_user,
        slug="aws-fundamentals",
        updates={
            "description": "Updated course description.",
            "tags": ["aws", "updated"],
        },
    )
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == course


def test_update_course_rejects_invalid_json(event: dict) -> None:
    event["body"] = "not-json"
    authentication_service = Mock()

    with patch.object(update_course, "authentication_service", authentication_service):
        response = update_course.lambda_handler(event, None)

    authentication_service.authenticate.assert_not_called()
    assert response["statusCode"] == 400
    assert json.loads(response["body"])["error"]["code"] == "INVALID_JSON"


def test_update_course_returns_validation_error_for_empty_update(
    event: dict, current_user: AuthenticatedUser
) -> None:
    event["body"] = "{}"
    authentication_service = Mock()
    authentication_service.authenticate.return_value = current_user
    course_service = Mock()

    with (
        patch.object(update_course, "authentication_service", authentication_service),
        patch.object(update_course, "course_service", course_service),
    ):
        response = update_course.lambda_handler(event, None)

    course_service.update_course.assert_not_called()
    assert response["statusCode"] == 422
    assert json.loads(response["body"])["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    ("service_error", "status_code", "error_code"),
    [
        (CourseNotFoundError("aws-fundamentals"), 404, "COURSE_NOT_FOUND"),
        (ForbiddenActionError("update", "course"), 403, "FORBIDDEN"),
    ],
)
def test_update_course_translates_course_errors(
    event: dict,
    current_user: AuthenticatedUser,
    service_error: Exception,
    status_code: int,
    error_code: str,
) -> None:
    authentication_service = Mock()
    authentication_service.authenticate.return_value = current_user
    course_service = Mock()
    course_service.update_course.side_effect = service_error

    with (
        patch.object(update_course, "authentication_service", authentication_service),
        patch.object(update_course, "course_service", course_service),
    ):
        response = update_course.lambda_handler(event, None)

    assert response["statusCode"] == status_code
    assert json.loads(response["body"])["error"]["code"] == error_code


@pytest.mark.parametrize(
    ("authentication_error", "status_code", "error_code"),
    [
        (
            UserProvisioningPendingError("cognito-sub-123"),
            503,
            "USER_PROVISIONING_PENDING",
        ),
        (InactiveUserError("disabled"), 403, "USER_INACTIVE"),
    ],
)
def test_update_course_translates_authentication_errors(
    event: dict,
    authentication_error: Exception,
    status_code: int,
    error_code: str,
) -> None:
    authentication_service = Mock()
    authentication_service.authenticate.side_effect = authentication_error
    course_service = Mock()

    with (
        patch.object(update_course, "authentication_service", authentication_service),
        patch.object(update_course, "course_service", course_service),
    ):
        response = update_course.lambda_handler(event, None)

    course_service.update_course.assert_not_called()
    assert response["statusCode"] == status_code
    assert json.loads(response["body"])["error"]["code"] == error_code

    if isinstance(authentication_error, UserProvisioningPendingError):
        assert response["headers"]["Retry-After"] == "3"

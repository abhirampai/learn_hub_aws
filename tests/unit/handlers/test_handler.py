import json
import os
from unittest.mock import Mock, patch

import pytest

from core.exceptions import DuplicateCourseError, ForbiddenActionError
from models.authenticated_user import AuthenticatedUser

os.environ.setdefault("TABLE_NAME", "learn-hub-test")

with patch("boto3.resource"):
    from handlers import courses


@pytest.fixture
def event() -> dict:
    return {
        "body": json.dumps(
            {
                "title": "AWS Fundamentals",
                "description": "Learn the AWS fundamentals.",
                "difficulty": "beginner",
                "tags": ["aws", "cloud"],
            }
        ),
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


def test_create_course_returns_created_course(
    event: dict, current_user: AuthenticatedUser
) -> None:
    authentication_service = Mock()
    authentication_service.authenticate.return_value = current_user
    course_service = Mock()
    course = {
        "id": "course_123",
        "instructor_id": "user_123",
        "slug": "aws-fundamentals",
    }
    course_service.create_course.return_value = course

    with (
        patch.object(courses, "authentication_service", authentication_service),
        patch.object(courses, "course_service", course_service),
    ):
        response = courses.lambda_handler(event, None)

    identity = authentication_service.authenticate.call_args.args[0]
    assert identity.sub == "cognito-sub-123"
    assert identity.email == "instructor@example.com"
    course_service.create_course.assert_called_once_with(
        current_user=current_user,
        payload={
            "title": "AWS Fundamentals",
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
            "tags": ["aws", "cloud"],
        },
    )
    assert response["statusCode"] == 201
    assert json.loads(response["body"]) == course


@pytest.mark.parametrize(
    ("service_error", "status_code", "error_code"),
    [
        (DuplicateCourseError("aws-fundamentals"), 409, "COURSE_ALREADY_EXISTS"),
        (ForbiddenActionError("create", "course"), 403, "FORBIDDEN"),
    ],
)
def test_create_course_translates_domain_errors(
    event: dict,
    current_user: AuthenticatedUser,
    service_error: Exception,
    status_code: int,
    error_code: str,
) -> None:
    authentication_service = Mock()
    authentication_service.authenticate.return_value = current_user
    course_service = Mock()
    course_service.create_course.side_effect = service_error

    with (
        patch.object(courses, "authentication_service", authentication_service),
        patch.object(courses, "course_service", course_service),
    ):
        response = courses.lambda_handler(event, None)

    assert response["statusCode"] == status_code
    assert json.loads(response["body"])["error"]["code"] == error_code

import json

from pydantic import ValidationError

from core.cognito_identity import CognitoIdentity
from core.exceptions import (
    CourseNotFoundError,
    ForbiddenActionError,
    InactiveUserError,
    UserProvisioningPendingError,
)
from core.responses import error, success, validation_error
from repositories.course_repository import CourseRepository
from repositories.user_repository import UserRepository
from schemas.course import UpdateCourseRequest
from services.authentication_service import AuthenticationService
from services.course_service import CourseService

course_service = CourseService(CourseRepository())
authentication_service = AuthenticationService(UserRepository())


def lambda_handler(
    event,
    context,
):
    try:
        payload = json.loads(event.get("body") or "")
    except json.JSONDecodeError:
        return error(
            status_code=400,
            error_code="INVALID_JSON",
            message="Request body must contain valid JSON.",
        )

    try:
        identity = CognitoIdentity.from_event(event)
        current_user = authentication_service.authenticate(identity)

        request = UpdateCourseRequest.model_validate(payload)
        slug = event["pathParameters"]["slug"]

        course = course_service.update_course(
            current_user=current_user,
            slug=slug,
            updates=request.model_dump(exclude_unset=True),
        )

        return success(body=course)
    except ValidationError as exc:
        return validation_error(exc.errors())
    except CourseNotFoundError:
        return error(
            status_code=404,
            error_code="COURSE_NOT_FOUND",
            message="Course does not exist.",
        )
    except ForbiddenActionError:
        return error(
            status_code=403,
            error_code="FORBIDDEN",
            message="You are not allowed to update this course.",
        )
    except UserProvisioningPendingError:
        return error(
            status_code=503,
            error_code="USER_PROVISIONING_PENDING",
            message=("Your LearnHub account is still being prepared. Please retry shortly."),
            headers={"Retry-After": "3"},
        )
    except InactiveUserError:
        return error(
            status_code=403,
            error_code="USER_INACTIVE",
            message="Your LearnHub account is not active.",
        )

import json

from pydantic import ValidationError

from core.cognito_identity import CognitoIdentity
from core.constants import (
    COURSE_ALREADY_EXISTS_CODE,
    COURSE_ALREADY_EXISTS_MESSAGE,
    DEFAULT_ERROR_CODE,
    INVALID_JSON_MESSAGE,
)
from core.exceptions import DuplicateCourseError
from core.responses import error, success, validation_error
from repositories.course_repository import CourseRepository
from repositories.user_repository import UserRepository
from schemas.course import CreateCourseRequest
from services.authentication_service import AuthenticationService
from services.course_service import CourseService

repository = CourseRepository()
course_service = CourseService(repository)

user_repository = UserRepository()
authentication_service = AuthenticationService(user_repository)


def lambda_handler(event, context):
    try:
        request = CreateCourseRequest.model_validate_json(event["body"])
        payload = request.model_dump()

        identity = CognitoIdentity.from_event(event)
        current_user = authentication_service.authenticate(identity)

        course = course_service.create_course(current_user=current_user, payload=payload)
        return success(status_code=201, body=course)
    except ValidationError as exc:
        return validation_error(exc.errors())
    except DuplicateCourseError:
        return error(
            status_code=409,
            error_code=COURSE_ALREADY_EXISTS_CODE,
            message=COURSE_ALREADY_EXISTS_MESSAGE,
        )
    except json.JSONDecodeError:
        return error(
            status_code=422,
            error_code=DEFAULT_ERROR_CODE,
            message=INVALID_JSON_MESSAGE,
        )

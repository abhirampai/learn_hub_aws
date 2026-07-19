import json
from core.exceptions import DuplicateCourseError
from core.responses import success, error, validation_error
from repositories.course_repository import CourseRepository
from schemas.course import CreateCourseRequest
from services.course_service import CourseService
from pydantic import ValidationError

repository = CourseRepository()
course_service = CourseService(repository)


def lambda_handler(event, context):
    try:
        request = CreateCourseRequest.model_validate_json(event["body"])
        payload = request.model_dump()

        course = course_service.create_course(payload)
        return success(status_code=201, body=course)
    except ValidationError as exc:
        return validation_error(exc.json())
    except DuplicateCourseError:
        return error(
            status_code=409,
            error_code="COURSE_ALREADY_EXISTS",
            message="A Course with this slug already exists.",
        )
    except json.JSONDecodeError:
        return error(
            status_code=422,
            error_code="INVALID_JSON",
            message="Request body must contain valid JSON.",
        )

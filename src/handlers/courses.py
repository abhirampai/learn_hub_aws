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
        return success(status_code=201, message=json.dumps(course))
    except ValidationError as exec:
        return validation_error(exec.json())
    except DuplicateCourseError as exec:
        print(exec)
        return error(
            status_code=422,
            error_code="DUPLICATE_RESOURCE",
            message="Course already exists"
        )
    except json.JSONDecodeError:
        return error(
            status_code=400,
            error_code="INVALID_JSON",
            message="Request body must contain valid JSON.",
        )

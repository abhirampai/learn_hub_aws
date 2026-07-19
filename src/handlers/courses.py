import json
from core.responses import success, error, validation_error
from services.course_service import CourseService

course_service = CourseService()


def validate_required_fields(payload):
    required_fields = ["title", "description", "difficulty"]

    missing = [field for field in required_fields if not payload.get(field)]

    return missing


def validate_fields(payload):
    possible_difficulties = ["beginner", "intermediate", "advanced"]

    if payload["difficulty"] not in possible_difficulties:
        return validation_error(payload["difficulty"], "difficulty")

    return {"valid": True, "error_message": ""}


def lambda_handler(event, context):
    try:
        payload = json.loads(event["body"])

        missing = validate_required_fields(payload)
        if missing:
            return error(
                status_code=400,
                error_code="VALIDATION_ERROR",
                message=f"Missing required fields: {', '.join(missing)}",
            )

        course_valid = validate_fields(payload)
        if not course_valid["valid"]:
            return error(
                status_code=400,
                error_code="VALIDATION_ERROR",
                message=course_valid["error_message"],
            )

        course = course_service.create_course(payload)
        return success(status_code=201, message=json.dumps(course))
    except json.JSONDecodeError:
        return error(
            status_code=400,
            error_code="INVALID_JSON",
            message="Request body must contain valid JSON.",
        )

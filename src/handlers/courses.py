import json
from utils.slugify import slugify
from utils.responses import success_handler, error_handler, validation_error
from datetime import datetime, UTC

COURSES = []


def validate_required_fields(payload):
    required_fields = ["title", "description", "difficulty"]

    missing = [field for field in required_fields if not payload.get(field)]

    return missing


def validate_fields(payload):
    possible_difficulties = ["beginner", "intermediate", "advanced"]

    if payload["difficulty"] not in possible_difficulties:
        return validation_error(payload["difficulty"], "difficulty")

    return {"valid": True, "error_message": ""}


def handle_course_creation(payload):
    course = {
        "id": f"course_{len(COURSES) + 1}",
        "title": payload["title"],
        "description": payload["description"],
        "difficulty": payload["difficulty"],
        "tags": payload.get("tags", []),
        "slug": slugify(payload["title"]),
        "thumbnail_url": None,
        "status": "draft",
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    COURSES.append(course)

    return course


def lambda_handler(event, context):
    try:
        payload = json.loads(event["body"])

        missing = validate_required_fields(payload)
        if missing:
            return error_handler(
                status_code=400,
                error_code="VALIDATION_ERROR",
                message=f"Missing required fields: {', '.join(missing)}",
            )

        course_valid = validate_fields(payload)
        if not course_valid["valid"]:
            return error_handler(
                status_code=400,
                error_code="VALIDATION_ERROR",
                message=course_valid["error_message"],
            )

        course = handle_course_creation(payload)
        return success_handler(status_code=201, message=json.dumps(course))
    except json.JSONDecodeError:
        return error_handler(
            status_code=400,
            error_code="INVALID_JSON",
            message="Request body must contain valid JSON.",
        )

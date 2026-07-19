from typing import Final, Literal

JSON_HEADERS: Final[dict[str, str]] = {"Content-Type": "application/json"}

DEFAULT_SUCCESS_MESSAGE: Final = "Operation successful"
DEFAULT_ERROR_CODE: Final = "INVALID_JSON"
DEFAULT_ERROR_MESSAGE: Final = "Something went wrong, Please try later"

VALIDATION_ERROR_CODE: Final = "VALIDATION_ERROR"
VALIDATION_ERROR_MESSAGE: Final = "The request is invalid."
INVALID_JSON_MESSAGE: Final = "Request body must contain valid JSON."
COURSE_ALREADY_EXISTS_CODE: Final = "COURSE_ALREADY_EXISTS"
COURSE_ALREADY_EXISTS_MESSAGE: Final = "A Course with this slug already exists."

CourseDifficulty = Literal["beginner", "intermediate", "advanced"]
COURSE_STATUS_DRAFT: Final = "draft"
COURSE_ENTITY_TYPE: Final = "COURSE"
COURSE_METADATA_SORT_KEY: Final = "METADATA"

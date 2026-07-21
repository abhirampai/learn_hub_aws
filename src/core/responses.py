import json
from typing import Any, TypedDict

from core.constants import (
    DEFAULT_ERROR_CODE,
    DEFAULT_ERROR_MESSAGE,
    DEFAULT_SUCCESS_MESSAGE,
    JSON_HEADERS,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
)


class LambdaResponse(TypedDict):
    statusCode: int
    body: str
    headers: dict[str, str]


def success(status_code: int = 200, body: dict[str, Any] | None = None) -> LambdaResponse:
    if body is None:
        body = {"message": DEFAULT_SUCCESS_MESSAGE}

    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": JSON_HEADERS.copy(),
    }


def error(
    status_code: int = 404,
    error_code: str = DEFAULT_ERROR_CODE,
    message: str = DEFAULT_ERROR_MESSAGE,
    headers: dict[str, str] | None = None
) -> LambdaResponse:
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": {"code": error_code, "message": message}}),
        "headers": { **JSON_HEADERS.copy(), **(headers or {}) },
    }


def validation_error(errors: list[dict[str, Any]]) -> LambdaResponse:
    return {
        "statusCode": 422,
        "body": json.dumps(
            {
                "error": {
                    "code": VALIDATION_ERROR_CODE,
                    "message": VALIDATION_ERROR_MESSAGE,
                    "details": errors,
                }
            },
            default=str,
        ),
        "headers": JSON_HEADERS.copy(),
    }

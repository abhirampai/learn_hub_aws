import json
from typing import Any


def success(status_code=200, body: dict[str, Any] | None = None):
    if body is None:
        body = {"message": "Operation successful"}

    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }


def error(
    status_code=404, error_code="INVALID_JSON", message="Something went wrong, Please try later"
):
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": {"code": error_code, "message": message}}),
        "headers": {"Content-Type": "application/json"},
    }


def validation_error(errors):
    return {
        "statusCode": 422,
        "body": json.dumps(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The request is invalid.",
                    "details": json.loads(errors),
                }
            }
        ),
        "headers": {"Content-Type": "application/json"},
    }

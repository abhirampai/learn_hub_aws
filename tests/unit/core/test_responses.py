import json
from datetime import UTC, datetime

from core.responses import error, success, validation_error

JSON_HEADERS = {"Content-Type": "application/json"}


def test_success_returns_default_response() -> None:
    response = success()

    assert response["statusCode"] == 200
    assert response["headers"] == JSON_HEADERS
    assert json.loads(response["body"]) == {"message": "Operation successful"}


def test_success_returns_custom_status_and_body() -> None:
    body = {"id": "course_123", "title": "AWS Fundamentals"}

    response = success(status_code=201, body=body)

    assert response["statusCode"] == 201
    assert response["headers"] == JSON_HEADERS
    assert json.loads(response["body"]) == body


def test_error_returns_default_response() -> None:
    response = error()

    assert response["statusCode"] == 404
    assert response["headers"] == JSON_HEADERS
    assert json.loads(response["body"]) == {
        "error": {
            "code": "INVALID_JSON",
            "message": "Something went wrong, Please try later",
        }
    }


def test_error_returns_custom_status_code_and_details() -> None:
    response = error(
        status_code=409,
        error_code="COURSE_ALREADY_EXISTS",
        message="A course with this slug already exists.",
    )

    assert response["statusCode"] == 409
    assert response["headers"] == JSON_HEADERS
    assert json.loads(response["body"]) == {
        "error": {
            "code": "COURSE_ALREADY_EXISTS",
            "message": "A course with this slug already exists.",
        }
    }


def test_validation_error_returns_details() -> None:
    errors = [
        {
            "type": "missing",
            "loc": ["title"],
            "msg": "Field required",
            "input": {},
        }
    ]

    response = validation_error(errors)

    assert response["statusCode"] == 422
    assert response["headers"] == JSON_HEADERS
    assert json.loads(response["body"]) == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "The request is invalid.",
            "details": errors,
        }
    }


def test_validation_error_serializes_non_json_values_as_strings() -> None:
    invalid_value = datetime(2026, 7, 19, 12, 30, tzinfo=UTC)

    response = validation_error([{"loc": ["created_at"], "input": invalid_value}])

    details = json.loads(response["body"])["error"]["details"]
    assert details == [{"loc": ["created_at"], "input": "2026-07-19 12:30:00+00:00"}]

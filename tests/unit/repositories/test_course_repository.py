import os
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from core.exceptions import CourseNotFoundError, DuplicateCourseError

os.environ.setdefault("TABLE_NAME", "learn-hub-test")

from repositories.course_repository import CourseRepository  # noqa: E402


@pytest.fixture
def course() -> dict:
    return {
        "id": "course_123",
        "instructor_id": "user_123",
        "title": "AWS Fundamentals",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
        "tags": ["aws", "cloud"],
        "slug": "aws-fundamentals",
        "thumbnail_url": None,
        "status": "draft",
        "created_at": "2026-07-19T10:00:00+00:00",
        "updated_at": "2026-07-19T10:00:00+00:00",
    }


@pytest.fixture
def table() -> Mock:
    return Mock()


@pytest.fixture
def repository(table: Mock) -> CourseRepository:
    repository = CourseRepository.__new__(CourseRepository)
    repository.table = table
    return repository


def client_error(code: str) -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "DynamoDB error"}},
        operation_name="PutItem",
    )


def test_repository_uses_configured_dynamodb_table() -> None:
    table = Mock()
    dynamodb = Mock()
    dynamodb.Table.return_value = table

    with patch("repositories.course_repository.boto3.resource", return_value=dynamodb) as resource:
        repository = CourseRepository()

    resource.assert_called_once_with("dynamodb")
    dynamodb.Table.assert_called_once_with("learn-hub-test")
    assert repository.table is table


def test_create_writes_course_item_conditionally(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    result = repository.create(course)

    table.put_item.assert_called_once_with(
        Item={
            "PK": "COURSE#aws-fundamentals",
            "SK": "METADATA",
            "id": "course_123",
            "instructor_id": "user_123",
            "title": "AWS Fundamentals",
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
            "tags": ["aws", "cloud"],
            "thumbnail_url": None,
            "status": "draft",
            "created_at": "2026-07-19T10:00:00+00:00",
            "updated_at": "2026-07-19T10:00:00+00:00",
            "slug": "aws-fundamentals",
            "entity_type": "COURSE",
            "GSI1PK": "STATUS#draft",
            "GSI1SK": "CREATED_AT#2026-07-19T10:00:00+00:00#COURSE#aws-fundamentals",
            "GSI2PK": "DIFFICULTY#beginner",
            "GSI2SK": "CREATED_AT#2026-07-19T10:00:00+00:00#COURSE#aws-fundamentals",
        },
        ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
    )
    assert result is course


def test_create_translates_conditional_failure_to_duplicate_error(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    table.put_item.side_effect = client_error("ConditionalCheckFailedException")

    with pytest.raises(DuplicateCourseError) as exc_info:
        repository.create(course)

    assert exc_info.value.slug == "aws-fundamentals"
    assert isinstance(exc_info.value.__cause__, ClientError)


def test_create_propagates_unexpected_client_error(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    error = client_error("ProvisionedThroughputExceededException")
    table.put_item.side_effect = error

    with pytest.raises(ClientError) as exc_info:
        repository.create(course)

    assert exc_info.value is error


def test_find_by_slug_returns_course(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    table.get_item.return_value = {
        "Item": {
            "PK": "COURSE#aws-fundamentals",
            "SK": "METADATA",
            "entity_type": "COURSE",
            **course,
        }
    }

    result = repository.find_by_slug("aws-fundamentals")

    table.get_item.assert_called_once_with(
        Key={"PK": "COURSE#aws-fundamentals", "SK": "METADATA"}
    )
    assert result == course


def test_find_by_slug_returns_none_when_course_does_not_exist(
    repository: CourseRepository, table: Mock
) -> None:
    table.get_item.return_value = {}

    result = repository.find_by_slug("missing-course")

    assert result is None


def test_update_replaces_existing_course_conditionally(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    updated_course = {
        **course,
        "description": "Updated description.",
        "updated_at": "2026-07-22T10:00:00+00:00",
    }

    result = repository.update(updated_course)

    call = table.put_item.call_args
    assert call.kwargs["Item"]["description"] == "Updated description."
    assert call.kwargs["Item"]["updated_at"] == "2026-07-22T10:00:00+00:00"
    assert call.kwargs["ConditionExpression"] == (
        "attribute_exists(PK) AND attribute_exists(SK)"
    )
    assert result is updated_course


def test_update_translates_conditional_failure_to_not_found_error(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    table.put_item.side_effect = client_error("ConditionalCheckFailedException")

    with pytest.raises(CourseNotFoundError) as exc_info:
        repository.update(course)

    assert exc_info.value.args == ("aws-fundamentals",)
    assert isinstance(exc_info.value.__cause__, ClientError)


def test_update_propagates_unexpected_client_error(
    repository: CourseRepository, table: Mock, course: dict
) -> None:
    error = client_error("ProvisionedThroughputExceededException")
    table.put_item.side_effect = error

    with pytest.raises(ClientError) as exc_info:
        repository.update(course)

    assert exc_info.value is error

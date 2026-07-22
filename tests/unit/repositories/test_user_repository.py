import os
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

os.environ.setdefault("TABLE_NAME", "learn-hub-test")

from repositories.user_repository import UserRepository  # noqa: E402


@pytest.fixture
def table() -> Mock:
    return Mock()


@pytest.fixture
def repository(table: Mock) -> UserRepository:
    repository = UserRepository.__new__(UserRepository)
    repository.table = table
    return repository


@pytest.fixture
def user() -> dict:
    return {
        "id": "user_123",
        "cognito_sub": "cognito-sub-123",
        "email": "learner@example.com",
        "display_name": "learner",
        "role": "student",
        "status": "active",
        "avatar_url": None,
        "created_at": "2026-07-21T10:00:00+00:00",
        "updated_at": "2026-07-21T10:00:00+00:00",
    }


def client_error(code: str, operation_name: str = "PutItem") -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "DynamoDB error"}},
        operation_name=operation_name,
    )


def test_duplicate_user_delivery_succeeds(
    repository: UserRepository, table: Mock, user: dict
) -> None:
    table.put_item.side_effect = client_error("ConditionalCheckFailedException")

    assert repository.create_if_absent(user) is None


def test_unexpected_dynamodb_error_propagates(
    repository: UserRepository, table: Mock, user: dict
) -> None:
    error = client_error("ProvisionedThroughputExceededException")
    table.put_item.side_effect = error

    with pytest.raises(ClientError) as exc_info:
        repository.create_if_absent(user)

    assert exc_info.value is error


def test_find_by_sub_returns_item(repository: UserRepository, table: Mock) -> None:
    item = {
        "PK": "USER#cognito-sub-123",
        "SK": "PROFILE",
        "email": "learner@example.com",
    }
    table.get_item.return_value = {"Item": item}

    result = repository.find_by_sub("cognito-sub-123")

    table.get_item.assert_called_once_with(Key={"PK": "USER#cognito-sub-123", "SK": "PROFILE"})
    assert result is item


def test_find_by_sub_returns_none(repository: UserRepository, table: Mock) -> None:
    table.get_item.return_value = {}

    result = repository.find_by_sub("missing-sub")

    table.get_item.assert_called_once_with(Key={"PK": "USER#missing-sub", "SK": "PROFILE"})
    assert result is None

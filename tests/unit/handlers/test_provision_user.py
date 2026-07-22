import json
import os
from unittest.mock import Mock, patch

os.environ.setdefault("TABLE_NAME", "learn-hub-test")

with patch("boto3.resource"):
    from handlers import provision_user


def sqs_record(message_id: str, *, schema_version: int = 1) -> dict:
    return {
        "messageId": message_id,
        "body": json.dumps(
            {
                "source": "learnhub.identity",
                "detail-type": "UserConfirmed",
                "detail": {
                    "schema_version": schema_version,
                    "user_sub": f"sub-{message_id}",
                    "email": f"{message_id}@example.com",
                },
            }
        ),
    }


def test_processes_valid_user_confirmed_record() -> None:
    service = Mock()

    with patch.object(provision_user, "service", service):
        result = provision_user.lambda_handler({"Records": [sqs_record("message-1")]}, None)

    service.provision.assert_called_once_with(
        {
            "schema_version": 1,
            "user_sub": "sub-message-1",
            "email": "message-1@example.com",
        }
    )
    assert result == {"batchItemFailures": []}


def test_rejects_unsupported_schema_version() -> None:
    service = Mock()

    with patch.object(provision_user, "service", service):
        result = provision_user.lambda_handler(
            {"Records": [sqs_record("message-1", schema_version=2)]}, None
        )

    service.provision.assert_not_called()
    assert result == {
        "batchItemFailures": [{"itemIdentifier": "message-1"}],
    }


def test_returns_one_batch_failure_when_one_message_fails() -> None:
    service = Mock()
    service.provision.side_effect = RuntimeError("provisioning failed")

    with patch.object(provision_user, "service", service):
        result = provision_user.lambda_handler({"Records": [sqs_record("message-1")]}, None)

    assert result == {
        "batchItemFailures": [{"itemIdentifier": "message-1"}],
    }


def test_continues_processing_remaining_records() -> None:
    service = Mock()
    service.provision.side_effect = [RuntimeError("first failed"), None]

    with patch.object(provision_user, "service", service):
        result = provision_user.lambda_handler(
            {
                "Records": [
                    sqs_record("message-1"),
                    sqs_record("message-2"),
                ]
            },
            None,
        )

    assert service.provision.call_count == 2
    assert result == {
        "batchItemFailures": [{"itemIdentifier": "message-1"}],
    }

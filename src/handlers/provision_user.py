import json
import logging
from typing import Any

from repositories.user_repository import UserRepository
from services.user_provisioning_service import UserProvisioningService

logger = logging.getLogger(__name__)

repository = UserRepository()
service = UserProvisioningService(repository)


def process_record(record: dict[str, Any]) -> None:
    eventbridge_event = json.loads(record["body"])
    detail = eventbridge_event["detail"]

    if detail.get("schema_version") != 1:
        raise ValueError(
            f"Unsupported UserConfirmed schema version: {detail.get('schema_version')}"
        )

    service.provision(detail)


def lambda_handler(
    event: dict[str, Any],
    context: Any,
) -> dict[str, list[dict[str, str]]]:
    batch_item_failures: list[dict[str, str]] = []

    for record in event["Records"]:
        try:
            process_record(record)
        except Exception:
            logger.exception(
                "Failed to provision user",
                extra={
                    "message_id": record["messageId"],
                },
            )

            batch_item_failures.append(
                {
                    "itemIdentifier": record["messageId"],
                }
            )

    return {
        "batchItemFailures": batch_item_failures,
    }

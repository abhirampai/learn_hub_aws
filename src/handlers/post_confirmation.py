import json
import logging
from datetime import UTC, datetime
import os

import boto3

logger = logging.getLogger(__name__)

_EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

events = boto3.client("events")

def build_user_confirmed_detail(event):
    user_attributes = event["request"]["userAttributes"]

    detail = {
        "schema_version": 1,
        "user_sub": user_attributes["sub"],
        "email": user_attributes["email"],
        "confirmed_at": user_attributes.get(
            "updated_at",
            datetime.now(UTC).isoformat(),
        ),
    }

    return detail


def lambda_handler(event, context):
    user_detail = build_user_confirmed_detail(event)

    response = events.put_events(
        Entries=[
            {
                "Source": "learnhub.identity",
                "DetailType": "UserConfirmed",
                "EventBusName": _EVENT_BUS_NAME,
                "Detail": json.dumps(user_detail),
            }
        ]
    )

    if response.get("FailedEntryCount", 0) > 0:
        logger.error("Failed to publish user confirmation event: %s", response)
        raise RuntimeError("Failed to publish UserConfirmed event")

    return event

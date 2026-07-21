import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

_TABLE_NAME = os.environ["TABLE_NAME"]


class UserRepository:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(_TABLE_NAME)

    def create_if_absent(self, user: dict[str, Any]):
        item = {
            "PK": f"USER#{user['cognito_sub']}",
            "SK": "PROFILE",
            "entity_type": "USER",
            "id": user["id"],
            "cognito_sub": user["cognito_sub"],
            "email": user["email"],
            "display_name": user["display_name"],
            "role": user["role"],
            "status": user["status"],
            "avatar_url": user["avatar_url"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }

        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=("attribute_not_exists(PK) AND attribute_not_exists(SK)"),
            )
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]

            if error_code == "ConditionalCheckFailedException":
                return user

            raise

        return user

    def find_by_sub(self, sub: str):
        response = self.table.get_item(
            Key={
                "PK": f"USER#{sub}",
                "SK": "PROFILE",
            }
        )

        return response.get("Item")

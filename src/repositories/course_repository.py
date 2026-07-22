import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from core.constants import COURSE_ENTITY_TYPE, COURSE_METADATA_SORT_KEY
from core.exceptions import CourseNotFoundError, DuplicateCourseError


class CourseRepository:
    def __init__(self):
        table_name = os.environ["TABLE_NAME"]
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def create(self, course: dict) -> dict:
        item = self._to_item(course)

        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=("attribute_not_exists(PK) AND attribute_not_exists(SK)"),
            )
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]

            if error_code == "ConditionalCheckFailedException":
                raise DuplicateCourseError(course["slug"]) from exc

            raise

        return course

    def update(self, course: dict[str, Any]) -> dict[str, Any]:
        item = self._to_item(course)

        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=("attribute_exists(PK) AND attribute_exists(SK)"),
            )
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]

            if error_code == "ConditionalCheckFailedException":
                raise CourseNotFoundError(course["slug"]) from exc

            raise

        return course

    def _to_item(self, course: dict[str, Any]) -> dict[str, Any]:
        return {
            "PK": f"COURSE#{course['slug']}",
            "SK": COURSE_METADATA_SORT_KEY,
            "id": course["id"],
            "instructor_id": course["instructor_id"],
            "title": course["title"],
            "description": course["description"],
            "difficulty": course["difficulty"],
            "tags": course["tags"],
            "thumbnail_url": course["thumbnail_url"],
            "status": course["status"],
            "created_at": course["created_at"],
            "updated_at": course["updated_at"],
            "slug": course["slug"],
            "entity_type": COURSE_ENTITY_TYPE,
            "GSI1PK": f"STATUS#{course['status']}",
            "GSI1SK": (f"CREATED_AT#{course['created_at']}#COURSE#{course['slug']}"),
            "GSI2PK": f"DIFFICULTY#{course['difficulty']}",
            "GSI2SK": (f"CREATED_AT#{course['created_at']}#COURSE#{course['slug']}"),
        }

    def _from_item(self, item: dict):
        return {
            "id": item["id"],
            "instructor_id": item["instructor_id"],
            "slug": item["slug"],
            "title": item["title"],
            "description": item["description"],
            "difficulty": item["difficulty"],
            "tags": item["tags"],
            "thumbnail_url": item.get("thumbnail_url"),
            "status": item["status"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
        }

    def find_by_slug(
        self,
        slug: str,
    ) -> dict[str, Any] | None:
        response = self.table.get_item(
            Key={
                "PK": f"COURSE#{slug}",
                "SK": "METADATA",
            }
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._from_item(item)

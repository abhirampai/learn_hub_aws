import os

import boto3
from botocore.exceptions import ClientError

from core.constants import COURSE_ENTITY_TYPE, COURSE_METADATA_SORT_KEY
from core.exceptions import DuplicateCourseError


class CourseRepository:
    def __init__(self):
        table_name = os.environ["TABLE_NAME"]
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def create(self, course: dict) -> dict:
        item = {
            "PK": f"COURSE#{course['slug']}",
            "SK": COURSE_METADATA_SORT_KEY,
            "id": course["id"],
            "created_by": course["created_by"],
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

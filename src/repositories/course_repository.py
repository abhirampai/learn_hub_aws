import os
import boto3

_TABLE_NAME = os.environ["TABLE_NAME"]

class CourseRepository:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(_TABLE_NAME)

    def create(self, course: dict) -> dict:
        item = {
            "PK": f"COURSE#{course['slug']}",
            "SK": "METADATA",
            "title": course["title"],
            "description": course["description"],
            "difficulty": course["difficulty"],
            "tags": course["tags"],
            "thumbnail_url": course["thumbnail_url"],
            "status": course["status"],
            "created_at": course["created_at"],
            "updated_at": course["updated_at"],

            "GSI1PK": f"STATUS#{course['status']}",
            "GSI1SK": (
                f"CREATED_AT#{course['created_at']}#"
                f"Course#{course['slug']}"
            ),

            "GSI2PK": f"Difficulty#{course['difficulty']}",
            "GSI2SK": (
                f"CREATED_AT#{course['created_at']}#"
                f"Course#{course['slug']}"
            )
        }

        self.table.put_item(Items=item)

        return course

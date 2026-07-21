from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class UserProvisioningService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def provision(
        self,
        detail: dict[str, Any],
    ) -> None:
        now = datetime.now(UTC).isoformat()

        user = {
            "id": f"user_{uuid4()}",
            "cognito_sub": detail["user_sub"],
            "email": detail["email"],
            "display_name": detail["email"].split("@", maxsplit=1)[0],
            "role": "student",
            "status": "active",
            "avatar_url": None,
            "created_at": now,
            "updated_at": now,
        }

        return self.repository.create_if_absent(user)

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CurrentUser:
    sub: str
    email: str | None = None

    @classmethod
    def from_event(
        cls,
        event: dict[str, Any],
    ) -> "CurrentUser":
        claims = event["requestContext"]["authorizer"]["claims"]

        return cls(
            sub=claims["sub"],
            email=claims.get("email"),
        )

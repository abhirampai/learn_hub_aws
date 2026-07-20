from dataclasses import dataclass

@dataclass(frozen=True)
class CurrentUser:
    sub: str
    email: str

    @classmethod
    def from_event(cls, event):
        claims = (
            event["requestContext"]
            ["authorizer"]
            ["jwt"]
            ["claims"]
        )

        return cls(
            sub=claims["sub"],
            email=claims["email"]
        )

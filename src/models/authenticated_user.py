from dataclasses import dataclass


@dataclass
class AuthenticatedUser:
    id: str
    cognito_sub: str
    email: str
    role: str
    status: str
    display_name: str
    avatar_url: str

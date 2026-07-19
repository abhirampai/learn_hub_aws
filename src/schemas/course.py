from typing import Literal

from pydantic import BaseModel, ConfigDict


class CreateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    description: str

    difficulty: Literal["beginner", "intermediate", "advanced"]

    tags: list[str] = []

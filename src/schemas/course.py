from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

NonEmptyString = Annotated[str, Field(min_length=1)]


class CreateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str
    description: str

    difficulty: Literal["beginner", "intermediate", "advanced"]

    tags: list[NonEmptyString] = Field(default_factory=list)

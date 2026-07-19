from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from core.constants import CourseDifficulty

NonEmptyString = Annotated[str, Field(min_length=1)]


class CreateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: NonEmptyString
    description: NonEmptyString

    difficulty: CourseDifficulty

    tags: list[NonEmptyString] = Field(default_factory=list)

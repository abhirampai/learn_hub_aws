from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.constants import CourseDifficulty

NonEmptyString = Annotated[str, Field(min_length=1)]


class CreateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: NonEmptyString
    description: NonEmptyString

    difficulty: CourseDifficulty

    tags: list[NonEmptyString] = Field(default_factory=list)


class UpdateCourseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: NonEmptyString | None = None
    description: NonEmptyString | None = None
    difficulty: CourseDifficulty | None = None

    tags: list[NonEmptyString] | None = None

    @model_validator(mode="after")
    def require_atleast_one_field(self) -> "UpdateCourseRequest":
        if not self.model_fields_set:
            raise ValueError("Atleast one field must be provided.")

        return self

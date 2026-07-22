import pytest
from pydantic import ValidationError

from schemas.course import CreateCourseRequest, UpdateCourseRequest


def valid_course_data(**overrides):
    data = {
        "title": "AWS Fundamentals",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
    }
    data.update(overrides)
    return data


def error_types(exc: ValidationError) -> set[str]:
    return {error["type"] for error in exc.errors()}


def test_course_schema_accepts_valid_input_and_defaults_tags() -> None:
    request = CreateCourseRequest.model_validate(valid_course_data())

    assert request.model_dump() == {
        "title": "AWS Fundamentals",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
        "tags": [],
    }


def test_course_requests_do_not_share_default_tags_list() -> None:
    first_request = CreateCourseRequest.model_validate(valid_course_data())
    second_request = CreateCourseRequest.model_validate(valid_course_data())

    first_request.tags.append("aws")

    assert first_request.tags == ["aws"]
    assert second_request.tags == []
    assert first_request.tags is not second_request.tags


def test_course_schema_strips_whitespace_from_strings() -> None:
    request = CreateCourseRequest.model_validate(
        valid_course_data(
            title="  AWS Fundamentals  ",
            description="  Learn the AWS fundamentals.  ",
            tags=["  aws  ", " cloud "],
        )
    )

    assert request.model_dump() == {
        "title": "AWS Fundamentals",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
        "tags": ["aws", "cloud"],
    }


@pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
def test_course_schema_accepts_supported_difficulties(difficulty: str) -> None:
    request = CreateCourseRequest.model_validate(valid_course_data(difficulty=difficulty))

    assert request.difficulty == difficulty


@pytest.mark.parametrize("field", ["title", "description", "difficulty"])
def test_course_schema_requires_mandatory_fields(field: str) -> None:
    data = valid_course_data()
    del data[field]

    with pytest.raises(ValidationError) as exc_info:
        CreateCourseRequest.model_validate(data)

    assert "missing" in error_types(exc_info.value)
    assert exc_info.value.errors()[0]["loc"] == (field,)


def test_course_schema_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateCourseRequest.model_validate(valid_course_data(author="Learn Hub"))

    assert "extra_forbidden" in error_types(exc_info.value)
    assert exc_info.value.errors()[0]["loc"] == ("author",)


@pytest.mark.parametrize("difficulty", ["expert", "BEGINNER", "  beginner  ", "", None])
def test_course_schema_rejects_unsupported_difficulty(difficulty) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateCourseRequest.model_validate(valid_course_data(difficulty=difficulty))

    assert "literal_error" in error_types(exc_info.value)


@pytest.mark.parametrize("tags", [[""], ["   "]])
def test_course_schema_rejects_empty_tags(tags: list[str]) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateCourseRequest.model_validate(valid_course_data(tags=tags))

    assert "string_too_short" in error_types(exc_info.value)
    assert exc_info.value.errors()[0]["loc"] == ("tags", 0)


@pytest.mark.parametrize("tags", ["aws", None, [1]])
def test_course_schema_rejects_invalid_tag_types(tags) -> None:
    with pytest.raises(ValidationError):
        CreateCourseRequest.model_validate(valid_course_data(tags=tags))


def test_course_schema_validates_json_input() -> None:
    request = CreateCourseRequest.model_validate_json(
        '{"title":"AWS","description":"Cloud basics","difficulty":"beginner","tags":["cloud"]}'
    )

    assert request.title == "AWS"
    assert request.tags == ["cloud"]


def test_course_schema_rejects_malformed_json() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateCourseRequest.model_validate_json('{"title":')

    assert "json_invalid" in error_types(exc_info.value)


def test_update_course_schema_accepts_partial_update() -> None:
    request = UpdateCourseRequest.model_validate(
        {
            "description": "  Updated description.  ",
            "tags": ["  aws  ", " updated "],
        }
    )

    assert request.model_dump(exclude_unset=True) == {
        "description": "Updated description.",
        "tags": ["aws", "updated"],
    }


@pytest.mark.parametrize("field", ["title", "description", "difficulty", "tags"])
def test_update_course_schema_tracks_only_provided_field(field: str) -> None:
    values = {
        "title": "Updated title",
        "description": "Updated description.",
        "difficulty": "advanced",
        "tags": ["updated"],
    }

    request = UpdateCourseRequest.model_validate({field: values[field]})

    assert request.model_dump(exclude_unset=True) == {field: values[field]}


def test_update_course_schema_rejects_empty_update() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UpdateCourseRequest.model_validate({})

    assert "value_error" in error_types(exc_info.value)


def test_update_course_schema_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UpdateCourseRequest.model_validate({"instructor_id": "another-user"})

    assert "extra_forbidden" in error_types(exc_info.value)


@pytest.mark.parametrize(
    "updates",
    [
        {"title": ""},
        {"description": "   "},
        {"difficulty": "expert"},
        {"tags": [""]},
    ],
)
def test_update_course_schema_rejects_invalid_field_values(updates: dict) -> None:
    with pytest.raises(ValidationError):
        UpdateCourseRequest.model_validate(updates)

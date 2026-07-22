import pytest

from core.exceptions import (
    CourseNotFoundError,
    DuplicateCourseError,
    ForbiddenActionError,
)
from models.authenticated_user import AuthenticatedUser
from services.course_service import CourseService

from ...fakes.fake_course_repository import FakeCourseRepository


@pytest.fixture
def repository() -> FakeCourseRepository:
    return FakeCourseRepository()


@pytest.fixture
def service(repository: FakeCourseRepository) -> CourseService:
    return CourseService(repository)


@pytest.fixture
def current_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        id="user_123",
        cognito_sub="cognito-sub-123",
        email="learner@example.com",
        display_name="Learner",
        role="admin",
        status="active",
        avatar_url=None,
    )


def test_create_course_stores_and_returns_course(
    service: CourseService,
    repository: FakeCourseRepository,
    current_user: AuthenticatedUser,
) -> None:
    course = service.create_course(
        current_user,
        {
            "title": "Introduction to AWS",
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
            "tags": ["aws", "cloud"],
        },
    )

    assert course["id"].startswith("course_")
    assert course["instructor_id"] == current_user.id
    assert course["slug"] == "introduction-to-aws"
    assert course["status"] == "draft"
    assert course["thumbnail_url"] is None
    assert course["created_at"] == course["updated_at"]
    assert repository.courses_by_slug[course["slug"]] == course


def test_create_course_uses_empty_tags_when_omitted(
    service: CourseService, current_user: AuthenticatedUser
) -> None:
    course = service.create_course(
        current_user,
        {
            "title": "AWS Basics",
            "description": "Learn the basics.",
            "difficulty": "beginner",
        },
    )

    assert course["tags"] == []


def test_create_course_rejects_user_without_creator_role(
    service: CourseService,
    repository: FakeCourseRepository,
    current_user: AuthenticatedUser,
) -> None:
    current_user.role = "student"

    with pytest.raises(ForbiddenActionError) as exc_info:
        service.create_course(
            current_user,
            {
                "title": "AWS Basics",
                "description": "Learn the basics.",
                "difficulty": "beginner",
            },
        )

    assert exc_info.value.action == "create"
    assert exc_info.value.resource == "course"
    assert repository.courses_by_slug == {}


@pytest.mark.parametrize(
    ("title", "expected_slug"),
    [
        ("AWS Cloud Fundamentals", "aws-cloud-fundamentals"),
        ("  AWS Cloud Fundamentals  ", "aws-cloud-fundamentals"),
        ("AWS   Cloud    Fundamentals", "aws-cloud-fundamentals"),
        ("AWS: Cloud & Fundamentals!", "aws-cloud-fundamentals"),
        ("AWS_Cloud-Fundamentals", "aws-cloud-fundamentals"),
        ("AWS Cloud 101", "aws-cloud-101"),
        ("aWs cLoUd FuNdAmEnTaLs", "aws-cloud-fundamentals"),
    ],
)
def test_create_course_normalizes_title_into_slug(
    service: CourseService,
    current_user: AuthenticatedUser,
    title: str,
    expected_slug: str,
) -> None:
    course = service.create_course(
        current_user,
        {
            "title": title,
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
        },
    )

    assert course["slug"] == expected_slug


def test_create_course_rejects_duplicate_slug(
    service: CourseService, current_user: AuthenticatedUser
) -> None:
    payload = {
        "title": "Introduction to AWS",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
    }
    service.create_course(current_user, payload)

    with pytest.raises(DuplicateCourseError) as exc_info:
        service.create_course(current_user, payload)

    assert exc_info.value.slug == "introduction-to-aws"


def test_create_course_rejects_differently_formatted_title_with_same_slug(
    service: CourseService, current_user: AuthenticatedUser
) -> None:
    payload = {
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
    }
    service.create_course(current_user, {**payload, "title": "AWS Cloud Fundamentals"})

    with pytest.raises(DuplicateCourseError) as exc_info:
        service.create_course(
            current_user,
            {**payload, "title": "  aws---cloud & fundamentals!  "},
        )

    assert exc_info.value.slug == "aws-cloud-fundamentals"


@pytest.fixture
def stored_course(repository: FakeCourseRepository) -> dict:
    course = {
        "id": "course_123",
        "instructor_id": "user_123",
        "title": "AWS Fundamentals",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
        "tags": ["aws"],
        "slug": "aws-fundamentals",
        "thumbnail_url": None,
        "status": "draft",
        "created_at": "2026-07-19T10:00:00+00:00",
        "updated_at": "2026-07-19T10:00:00+00:00",
    }
    repository.courses_by_slug[course["slug"]] = course
    return course


def test_update_course_merges_updates_and_preserves_course_fields(
    service: CourseService,
    repository: FakeCourseRepository,
    current_user: AuthenticatedUser,
    stored_course: dict,
) -> None:
    result = service.update_course(
        current_user=current_user,
        slug="aws-fundamentals",
        updates={
            "description": "Updated description.",
            "difficulty": "intermediate",
        },
    )

    assert result["description"] == "Updated description."
    assert result["difficulty"] == "intermediate"
    assert result["id"] == stored_course["id"]
    assert result["instructor_id"] == stored_course["instructor_id"]
    assert result["slug"] == stored_course["slug"]
    assert result["created_at"] == stored_course["created_at"]
    assert result["updated_at"] != stored_course["updated_at"]
    assert repository.courses_by_slug["aws-fundamentals"] == result


def test_update_course_allows_owning_instructor(
    service: CourseService,
    current_user: AuthenticatedUser,
    stored_course: dict,
) -> None:
    current_user.role = "instructor"

    result = service.update_course(
        current_user=current_user,
        slug=stored_course["slug"],
        updates={"title": "Updated AWS Fundamentals"},
    )

    assert result["title"] == "Updated AWS Fundamentals"


def test_update_course_raises_when_course_does_not_exist(
    service: CourseService, current_user: AuthenticatedUser
) -> None:
    with pytest.raises(CourseNotFoundError) as exc_info:
        service.update_course(
            current_user=current_user,
            slug="missing-course",
            updates={"description": "Updated description."},
        )

    assert exc_info.value.args == ("missing-course",)


def test_update_course_rejects_non_owner_instructor_without_modifying_course(
    service: CourseService,
    repository: FakeCourseRepository,
    current_user: AuthenticatedUser,
    stored_course: dict,
) -> None:
    current_user.id = "another-user"
    current_user.role = "instructor"

    with pytest.raises(ForbiddenActionError) as exc_info:
        service.update_course(
            current_user=current_user,
            slug=stored_course["slug"],
            updates={"description": "Unauthorized update."},
        )

    assert exc_info.value.action == "update"
    assert repository.courses_by_slug[stored_course["slug"]] == stored_course

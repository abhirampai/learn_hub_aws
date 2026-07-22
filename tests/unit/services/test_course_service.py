import pytest

from core.exceptions import DuplicateCourseError, ForbiddenActionError
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

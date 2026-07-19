import pytest

from core.exceptions import DuplicateCourseError
from services.course_service import CourseService
from tests.fakes.fake_course_repository import FakeCourseRepository


@pytest.fixture
def repository() -> FakeCourseRepository:
    return FakeCourseRepository()


@pytest.fixture
def service(repository: FakeCourseRepository) -> CourseService:
    return CourseService(repository)


def test_create_course_stores_and_returns_course(
    service: CourseService, repository: FakeCourseRepository
) -> None:
    course = service.create_course(
        {
            "title": "Introduction to AWS",
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
            "tags": ["aws", "cloud"],
        }
    )

    assert course["id"].startswith("course_")
    assert course["slug"] == "introduction-to-aws"
    assert course["status"] == "draft"
    assert course["thumbnail_url"] is None
    assert course["created_at"] == course["updated_at"]
    assert repository.courses_by_slug[course["slug"]] == course


def test_create_course_uses_empty_tags_when_omitted(service: CourseService) -> None:
    course = service.create_course(
        {
            "title": "AWS Basics",
            "description": "Learn the basics.",
            "difficulty": "beginner",
        }
    )

    assert course["tags"] == []


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
    service: CourseService, title: str, expected_slug: str
) -> None:
    course = service.create_course(
        {
            "title": title,
            "description": "Learn the AWS fundamentals.",
            "difficulty": "beginner",
        }
    )

    assert course["slug"] == expected_slug


def test_create_course_rejects_duplicate_slug(service: CourseService) -> None:
    payload = {
        "title": "Introduction to AWS",
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
    }
    service.create_course(payload)

    with pytest.raises(DuplicateCourseError) as exc_info:
        service.create_course(payload)

    assert exc_info.value.slug == "introduction-to-aws"


def test_create_course_rejects_differently_formatted_title_with_same_slug(
    service: CourseService,
) -> None:
    payload = {
        "description": "Learn the AWS fundamentals.",
        "difficulty": "beginner",
    }
    service.create_course({**payload, "title": "AWS Cloud Fundamentals"})

    with pytest.raises(DuplicateCourseError) as exc_info:
        service.create_course({**payload, "title": "  aws---cloud & fundamentals!  "})

    assert exc_info.value.slug == "aws-cloud-fundamentals"

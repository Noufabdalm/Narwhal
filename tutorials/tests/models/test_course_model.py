"""Unit tests for the Course model."""
from django.test import TestCase
from tutorials.models import Course, Expertise
from django.core.exceptions import ValidationError


class CourseModelTestCase(TestCase):
    """Unit tests for the Course model."""

    def setUp(self):
        self.expertise = Expertise.objects.create(name='python')
        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn Python from scratch.",
            level="beginner",
            price_per_hour=20.0,
            ProgrammingLanguage=self.expertise
        )

    def test_valid_course(self):
        self._assert_course_is_valid()

    def test_course_name_must_not_be_blank(self):
        self.course.name = ''
        self._assert_course_is_invalid()

    def test_course_level_must_be_valid(self):
        self.course.level = 'invalid_level'
        self._assert_course_is_invalid()

    def test_course_price_per_hour_must_be_positive(self):
        self.course.price_per_hour = -10.0
        self._assert_course_is_invalid()

    def _assert_course_is_valid(self):
        try:
            self.course.full_clean()
        except ValidationError:
            self.fail('Test course should be valid')

    def _assert_course_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.course.full_clean()

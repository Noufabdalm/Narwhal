"""Unit tests for the TutorSession model."""
from django.test import TestCase
from tutorials.models import TutorSession, Tutor, Course, Term, User
from datetime import time, date
from django.core.exceptions import ValidationError

class TutorSessionModelTestCase(TestCase):
    """Unit tests for the TutorSession model."""

    def setUp(self):
        self.user = User.objects.create_user(username='@tutoruser', email='tutor@example.com', password='Password123')
        self.tutor = Tutor.objects.create(user=self.user)
        self.term = Term.objects.create(name="autumn", start_date=date(2024, 9, 1), end_date=date(2024, 12, 20))
        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn Python from scratch.",
            level="beginner",
            price_per_hour=20.0,
            duration_minutes=60,
            frequency="weekly",
            ProgrammingLanguage=None
        )
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            course=self.course,
            time=time(10, 0),
            start_day=0,
            term=self.term
        )

    def test_valid_tutor_session(self):
        self._assert_tutor_session_is_valid()

    def test_duplicate_session_is_invalid(self):
        duplicate_session = TutorSession(
            tutor=self.tutor,
            course=self.course,
            time=self.tutor_session.time,
            start_date=self.tutor_session.start_date,
            term=self.term
        )
        with self.assertRaises(ValidationError):
            duplicate_session.full_clean()

    def _assert_tutor_session_is_valid(self):
        try:
            self.tutor_session.full_clean()
        except ValidationError:
            self.fail('Test tutor session should be valid')

from django.test import TestCase
from tutorials.models import LessonRequest, Student, User, Tutor, Course, Term, TutorSession, Expertise
from datetime import date, timedelta
from django.core.exceptions import ValidationError


class LessonRequestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user for the student
        cls.student_user = User.objects.create_user(
            username="teststudent",
            email="teststudent@example.com",
            password="password123"
        )

        # Create the student
        cls.student = Student.objects.create(
            user=cls.student_user,
            learning_level="beginner"
        )
        # Create an expertise
        cls.expertise = Expertise.objects.create(name='python')
        # Create a course
        cls.course = Course.objects.create(
            name="Python Beginner",
            description="Learn the basics of Python programming.",
            level="beginner",
            price_per_hour=20,
            ProgrammingLanguage=cls.expertise
        )

        # Create a term that starts in more than 14 days
        cls.term = Term.objects.create(
            name="spring",
            start_date=date.today() + timedelta(days=20),  # Starts in 20 days
            end_date=date.today() + timedelta(days=100)  # Ends in 100 days
        )

        # Create a lesson request
        cls.lesson_request = LessonRequest.objects.create(
            student=cls.student,
            course=cls.course,
            frequency="weekly",
            duration_minutes=60,
            term=cls.term,
            status="pending",
            requested_date=date.today()
        )

    def test_lesson_request_creation(self):
        """Test that a lesson request is created successfully."""
        self.assertEqual(self.lesson_request.student, self.student)
        self.assertEqual(self.lesson_request.course, self.course)
        self.assertEqual(self.lesson_request.frequency, "weekly")
        self.assertEqual(self.lesson_request.duration_minutes, 60)
        self.assertEqual(self.lesson_request.term, self.term)
        self.assertEqual(self.lesson_request.status, "pending")
        self.assertFalse(self.lesson_request.is_late)

    def test_check_and_mark_late(self):
        """Test the check_and_mark_late method."""
        # Case 1: Term starts in more than 14 days
        self.lesson_request.term.start_date = date.today() + timedelta(days=20)
        self.lesson_request.term.save()
        self.lesson_request.save()
        self.assertFalse(self.lesson_request.is_late)

        # Case 2: Term starts in less than 14 days
        self.lesson_request.term.start_date = date.today() + timedelta(days=10)
        self.lesson_request.term.save()
        self.lesson_request.save()
        self.assertTrue(self.lesson_request.is_late)

    def test_status_choices(self):
        """Test that the status choices are enforced."""
        # Valid status
        self.lesson_request.status = "allocated"
        self.lesson_request.full_clean()
        self.assertEqual(self.lesson_request.status, "allocated")

        # Invalid status
        with self.assertRaises(ValidationError) as context:
            self.lesson_request.status = "invalid_status"
            self.lesson_request.full_clean()
        self.assertIn("Value 'invalid_status' is not a valid choice.", str(context.exception))


 
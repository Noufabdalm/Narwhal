from django.test import TestCase
from tutorials.forms import CancellationRequestForm
from tutorials.models import User, Student, Tutor, Lesson, Course, Term, LessonRequest, TutorSession
import datetime

class CancellationRequestFormTest(TestCase):
    def setUp(self):
        # Set up unique users
        self.student_user = User.objects.create_user(
            username="studentuser", 
            password="password123", 
            email="student@example.com"
        )
        self.student = Student.objects.create(user=self.student_user, learning_level="beginner")

        self.tutor_user = User.objects.create_user(
            username="tutoruser", 
            password="password123", 
            email="tutor@example.com"
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Set up term and course
        self.term = Term.objects.create(
            name="spring", 
            start_date=datetime.date(2025, 1, 1), 
            end_date=datetime.date(2025, 6, 1)
        )
        self.course = Course.objects.create(
            name="Python Basics",
            description="Intro to Python",
            level="beginner",
            price_per_hour=20,
        )

        # Set up a tutor session
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            time="10:00:00",
            term=self.term,
            start_day=0,
            duration_minutes=60,
            frequency="weekly",
            is_booked=False
        )

        # Set up a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            frequency="weekly",
            duration_minutes=60,
            term=self.term,
            status="pending"
        )

        # Set up lesson
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.tutor_session,
            term=self.term,
            request=self.lesson_request,
        )

    def test_valid_form_for_student(self):
        form_data = {
            "lesson": self.lesson.id,
            "reason": "I need to cancel this lesson due to personal reasons.",
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())
        cancellation_request = form.save(commit=False)
        self.assertEqual(cancellation_request.lesson, self.lesson)
        self.assertEqual(cancellation_request.reason, "I need to cancel this lesson due to personal reasons.")

    def test_valid_form_for_tutor(self):
        form_data = {
            "lesson": self.lesson.id,
            "reason": "Unable to continue with this session.",
        }
        form = CancellationRequestForm(data=form_data, user=self.tutor_user)
        self.assertTrue(form.is_valid())
        cancellation_request = form.save(commit=False)
        self.assertEqual(cancellation_request.lesson, self.lesson)
        self.assertEqual(cancellation_request.reason, "Unable to continue with this session.")

    def test_invalid_form_no_lesson_selected(self):
        form_data = {
            "lesson": "",
            "reason": "I need to cancel this lesson due to personal reasons.",
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn("lesson", form.errors)

    def test_invalid_form_no_reason_provided(self):
        form_data = {
            "lesson": self.lesson.id,
            "reason": "",
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())  # Reason is optional

    def test_lesson_queryset_for_student(self):
        form = CancellationRequestForm(user=self.student_user)
        self.assertIn(self.lesson, form.fields["lesson"].queryset)

    def test_lesson_queryset_for_tutor(self):
        form = CancellationRequestForm(user=self.tutor_user)
        self.assertIn(self.lesson, form.fields["lesson"].queryset)

    
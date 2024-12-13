from django.test import TestCase
from django.urls import reverse
from tutorials.models import (
    User, TutorSession, Admin, Lesson, Term, Tutor, Course, Expertise, LessonRequest, Student
)
from django.utils.timezone import now
from datetime import timedelta


class AllocatedLessonsViewTestCase(TestCase):
    def setUp(self):
        # Create expertise and course
        self.expertise = Expertise.objects.create(name="Python")
        self.course = Course.objects.create(
            name="Python Basics",
            description="An introduction to Python programming.",
            level="beginner",
            price_per_hour=20.00,
            ProgrammingLanguage=self.expertise,
        )

        # Create admin and non-admin users
        self.admin_user = User.objects.create_user(username="admin", password="password123", email="admin@admin.com")
        self.non_admin_user = User.objects.create_user(username="nonadmin", password="password123", email="nonadmin@nonadmin.com")
        Admin.objects.create(user=self.admin_user)

        # Create a tutor
        self.tutor = Tutor.objects.create(user=self.non_admin_user)
        self.tutor.expertise.add(self.expertise)

        # Create a term
        self.term = Term.objects.create(
            name="autumn",
            start_date=now().date() + timedelta(days=14),
            end_date=now().date() + timedelta(days=100),
        )

        # Create a student
        self.student_user = User.objects.create_user(username="student", password="password123", email="student@student.com")
        self.student = Student.objects.create(user=self.student_user, learning_level="beginner")

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            term=self.term,
            frequency="weekly",
            duration_minutes=60,
            status="allocated"
        )

        # Create tutor sessions
        self.allocated_session = TutorSession.objects.create(
            tutor=self.tutor,
            term=self.term,
            time="09:30:00",
            start_day=0,
            duration_minutes=60,
            frequency="weekly",
            is_booked=True,
        )

        # Create a lesson associated with the allocated session and request
        self.allocated_lesson = Lesson.objects.create(
            session=self.allocated_session,
            tutor=self.tutor,
            course=self.course,
            term=self.term,
            student=self.student,
            request=self.lesson_request
        )

        # URL for allocated lessons
        self.url = reverse("allocated_lessons")

    def test_allocated_lessons_admin_access(self):
        # Log in as admin user
        self.client.login(username="admin", password="password123")

        # Make a GET request to the allocated lessons view
        response = self.client.get(self.url)

        # Check response status and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "allocated_lessons.html")

        # Verify allocated lesson is included in the context
        lessons = response.context["lessons"]
        self.assertIn(self.allocated_lesson, lessons)

        # Verify the lesson request status is "allocated"
        self.assertEqual(self.lesson_request.status, "allocated")

    def test_non_admin_user_access_denied(self):
        # Log in as a non-admin user
        self.client.login(username="nonadmin", password="password123")

        # Make a GET request to the allocated lessons view
        response = self.client.get(self.url)

        # Verify the user is redirected to a dashboard or access denied
        self.assertEqual(response.status_code, 302)

    def test_only_allocated_sessions_are_displayed(self):
        # Log in as admin user
        self.client.login(username="admin", password="password123")

        # Make a GET request to the allocated lessons view
        response = self.client.get(self.url)

        # Verify the lesson is included in the allocated lessons
        lessons = response.context["lessons"]
        self.assertEqual(lessons.count(), 1)
        self.assertIn(self.allocated_lesson, lessons)

from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Lesson, Course, Tutor, TutorSession, Term, LessonRequest
from datetime import date, time


class StudentLessonScheduleViewTestCase(TestCase):
    """Tests for the lesson schedule view."""

    def setUp(self):
        self.student_user = User.objects.create_user(
            username='@studentjohndoe',
            first_name='John',
            last_name='Doe',
            email='studentjohndoe@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.student_user, learning_level='beginner')
        self.url = reverse('student_lesson_schedule')

        self.tutor = Tutor.objects.create(user=User.objects.create_user(
            username='@tutorjane',
            first_name='Jane',
            last_name='Doe',
            email='tutorjane@example.com',
            password='Password123'
        ))
        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn the basics of Python programming",
            level="beginner",
            price_per_hour=20.0,
            duration_minutes=60,
            frequency="weekly",
        )
        self.term = Term.objects.create(
            name='autumn',
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15)
        )
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            course=self.course,
            time=time(10, 0),
            start_day=0,
            term=self.term,
            start_date=date(2024, 9, 4)
        )
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            frequency="weekly",
            term=self.term,
            status="allocated"
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.tutor_session,
            term=self.term,
            request=self.lesson_request
        )

    def test_lesson_schedule_url(self):
        """Test that the URL for lesson schedule is correct."""
        self.assertEqual(self.url, '/lesson-schedule/')

    def test_get_lesson_schedule(self):
        """Test that a logged-in student can view their lesson schedule."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_lesson_schedule.html')  # Updated template name
        schedule = response.context['schedule']
        self.assertIsInstance(schedule, list)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]['course_name'], self.course.name)
        self.assertEqual(schedule[0]['tutor_name'], self.tutor.user.full_name())
        self.assertEqual(schedule[0]['date'], '2024-09-04')
        self.assertEqual(schedule[0]['time'], '10:00 AM')
        self.assertEqual(schedule[0]['term'], self.term.name)

    def test_no_lessons(self):
        """Test that a student with no lessons sees an appropriate message."""
        Lesson.objects.filter(student=self.student).delete()
        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url)

        # Check the message is present
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No lessons scheduled.")

        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'student_lesson_schedule.html')
        self.assertEqual(len(response.context['schedule']), 0)

    def test_redirect_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        redirect_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unauthorized_access(self):
        """Test that a non-student user cannot access the schedule."""
        non_student_user = User.objects.create_user(
            username='@nonstudent', password='Password123'
        )
        self.client.login(username=non_student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'))

    def test_multiple_lessons(self):
        """Test that multiple lessons for a student are displayed correctly."""
        additional_session = TutorSession.objects.create(
            tutor=self.tutor,
            course=self.course,
            time=time(11, 0),
            start_day=2,
            term=self.term,
            start_date=date(2024, 9, 6)
        )
        additional_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=additional_session,
            term=self.term,
            request=self.lesson_request
        )
        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['schedule']), 2)

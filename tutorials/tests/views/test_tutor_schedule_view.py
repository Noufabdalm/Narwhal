from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutor, Student, Lesson, Course, TutorSession, Term, LessonRequest
from datetime import date, time

class TutorScheduleViewTestCase(TestCase):
    """Tests for the tutor schedule view."""

    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='@tutorjane',
            first_name='Jane',
            last_name='Doe',
            email='tutorjane@example.com',
            password='Password123'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.url = reverse('tutor_schedule')

        self.student_user = User.objects.create_user(
            username='@studentjohn',
            first_name='John',
            last_name='Doe',
            email='studentjohn@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.student_user)

        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn the basics of Python programming",
            level="beginner",
            price_per_hour=20.0
        )
        self.term = Term.objects.create(
            name='autumn',
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15)
        )
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
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

    def test_tutor_schedule_url(self):
        """Test that the URL for tutor schedule is correct."""
        self.assertEqual(self.url, '/tutor-schedule/')

    def test_get_tutor_schedule(self):
        """Test that a logged-in tutor can view their schedule."""
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_schedule.html')
        schedule = response.context['schedule']
        self.assertIsInstance(schedule, list)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]['course_name'], self.course.name)
        self.assertEqual(schedule[0]['student_name'], self.student.user.full_name())
        self.assertEqual(schedule[0]['date'], '2024-09-04')
        self.assertEqual(schedule[0]['time'], '10:00 AM')
        self.assertEqual(schedule[0]['term'], self.term.name)

    def test_no_lessons(self):
        """Test that a tutor with no lessons sees an appropriate message."""
        Lesson.objects.filter(tutor=self.tutor).delete()
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)

        # Check the message is present
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No lessons scheduled.")

        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'tutor_schedule.html')

    def test_redirect_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        redirect_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, redirect_url)

    # def test_unauthorized_access(self):
    #     """Test that a non-tutor user cannot access the schedule."""
    #     student_user = User.objects.create_user(
    #         username='@studentjane', password='Password123'
    #     )
    #     self.client.login(username=student_user.username, password='Password123')
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, reverse('home'))

    def test_multiple_lessons(self):
        """Test that multiple lessons for a tutor are displayed correctly."""
        # Create an additional session and lesson for the same tutor
        additional_session = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(11, 0),  # A different time
            start_day=1,
            term=self.term,
            start_date=date(2024, 9, 5)
        )
        additional_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=additional_session,
            term=self.term,
            request=self.lesson_request
        )

        # Log in as the tutor and fetch the schedule
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)

        # Ensure the response contains both lessons
        self.assertEqual(response.status_code, 200)
        schedule = response.context['schedule']
        self.assertEqual(len(schedule), 2)  # Should have two lessons

        # Validate details of both lessons
        first_lesson = schedule[0]
        self.assertEqual(first_lesson['course_name'], self.course.name)
        self.assertEqual(first_lesson['student_name'], self.student.user.full_name())
        self.assertEqual(first_lesson['date'], '2024-09-04')
        self.assertEqual(first_lesson['time'], '10:00 AM')
        self.assertEqual(first_lesson['term'], self.term.name)

        second_lesson = schedule[1]
        self.assertEqual(second_lesson['course_name'], self.course.name)
        self.assertEqual(second_lesson['student_name'], self.student.user.full_name())
        self.assertEqual(second_lesson['date'], '2024-09-05')
        self.assertEqual(second_lesson['time'], '11:00 AM')
        self.assertEqual(second_lesson['term'], self.term.name)

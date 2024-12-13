"""Tests for the student courses view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Lesson, Course, Tutor, TutorSession, Term, LessonRequest, Expertise
from datetime import date, time


class StudentCoursesViewTestCase(TestCase):
    """Tests for the student courses view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        self.student_user = User.objects.create_user(
            username='@studentjohndoe', 
            first_name='John', 
            last_name='Doe', 
            email='studentjohndoe@example.com', 
            password='Password123'
        )
        self.student = Student.objects.create(user=self.student_user, learning_level='beginner')
        self.url = reverse('student_courses')

        # Create related data
        self.tutor = Tutor.objects.create(user=User.objects.create_user(
            username='@tutorjane', 
            first_name='Jane', 
            last_name='Doe', 
            email='tutorjane@example.com', 
            password='Password123'
        ))

        self.expertise = Expertise.objects.create(name='python')

        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn the basics of Python programming",
            level="beginner",
            price_per_hour=20.0,
            ProgrammingLanguage=self.expertise,
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

    def test_student_courses_url(self):
        """Test that the URL for student courses is correct."""
        self.assertEqual(self.url, '/my-courses/')

    def test_get_student_courses(self):
        """Test that a logged-in student can view their courses and tutors."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_courses.html')
        courses_and_tutors = response.context['courses_and_tutors']
        self.assertIsInstance(courses_and_tutors, list)
        self.assertEqual(len(courses_and_tutors), 1)
        self.assertEqual(courses_and_tutors[0]['course_name'], self.course.name)
        self.assertEqual(courses_and_tutors[0]['tutor_name'], self.tutor.user.full_name())

    def test_get_student_courses_redirects_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        redirect_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_student_with_no_lessons(self):
        """Test that a student with no lessons sees an appropriate message."""
        # Delete all lessons for this student
        Lesson.objects.filter(student=self.student).delete()

        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url)

        # Check that the message is in the response context
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not enrolled in any courses yet.")

        # Ensure the page renders the correct template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_courses.html')

    # def test_non_student_access(self):
    #     """Test that non-students cannot access the student courses view."""
    #     non_student_user = User.objects.create_user(
    #         username='@nonstudent', password='Password123', first_name='Non', last_name='Student'
    #     )
    #     self.client.login(username=non_student_user.username, password='Password123')
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, reverse('home'))

    def test_student_with_multiple_lessons(self):
        """Test that a student with multiple lessons sees all courses and tutors."""
        # Create another lesson request for the second course
        another_course = Course.objects.create(
            name="Advanced Python",
            description="Learn advanced Python programming",
            level="advanced",
            price_per_hour=40.0,
            ProgrammingLanguage=self.expertise,  # Match the ProgrammingLanguage to avoid validation issues
        )
        another_lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=another_course,
            frequency="weekly",
            term=self.term,
            status="allocated",
        )

        # Create another tutor session for the second lesson
        another_tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            term=self.term,
            time="11:30:00",
            start_day=2,
            duration_minutes=60,
            frequency="weekly",
            is_booked=True,
        )

        # Create another lesson with the new course and lesson request
        another_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=another_course,
            session=another_tutor_session,
            term=self.term,
            request=another_lesson_request,  # Use the correct lesson request
        )

        # Log in as the student
        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url)

        # Check that both lessons are included in the context
        courses_and_tutors = response.context['courses_and_tutors']
        self.assertEqual(len(courses_and_tutors), 2)
        self.assertIn(self.course.name, [item['course_name'] for item in courses_and_tutors])
        self.assertIn(another_course.name, [item['course_name'] for item in courses_and_tutors])

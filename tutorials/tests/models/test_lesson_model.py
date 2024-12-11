from django.test import TestCase
from tutorials.models import (
    Student, Tutor, Course, Term, TutorSession, Lesson, LessonRequest, Expertise, User
)
from django.core.exceptions import ValidationError
from datetime import date, time


class LessonModelTestCase(TestCase):

    def setUp(self):
        # Create Users
        self.student_user = User.objects.create_user(
            username='@student',
            email='student@example.com',
            password='Password123',
            first_name='Student',
            last_name='User'
        )
        self.tutor_user = User.objects.create_user(
            username='@tutor',
            email='tutor@example.com',
            password='Password123',
            first_name='Tutor',
            last_name='User'
        )

        # Create Student and Tutor
        self.student = Student.objects.create(user=self.student_user, learning_level='beginner')
        self.expertise = Expertise.objects.create(name='python')
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.tutor.expertise.add(self.expertise)

        # Create Course
        self.course = Course.objects.create(
            name='Python Basics',
            description='A beginner Python course',
            level='beginner',
            price_per_hour=20.0,
    
            ProgrammingLanguage=self.expertise
        )

        # Create Term
        self.term = Term.objects.create(
            name='spring',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31)
        )

        # Create TutorSession
        self.session = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(10, 0),
            start_day=0,
            term=self.term,
            is_booked=False
        )

        # Create LessonRequest
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            frequency='weekly',
            term=self.term,
            status='pending'
        )

    def test_create_valid_lesson(self):
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.session,
            term=self.term,
            request=self.lesson_request
        )
        self.assertEqual(lesson.student, self.student)
        self.assertEqual(lesson.tutor, self.tutor)
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.session, self.session)
        self.assertEqual(lesson.term, self.term)
        self.assertEqual(lesson.request, self.lesson_request)

    def test_session_marked_as_booked_on_save(self):
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.session,
            term=self.term,
            request=self.lesson_request
        )
        self.session.refresh_from_db()
        self.assertTrue(self.session.is_booked)

    def test_request_status_updated_on_save(self):
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.session,
            term=self.term,
            request=self.lesson_request
        )
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, 'allocated')

    def test_invalid_lesson_with_booked_session(self):
        # Book the session
        self.session.is_booked = True
        self.session.save()

        with self.assertRaises(ValidationError):
            lesson = Lesson(
                student=self.student,
                tutor=self.tutor,
                course=self.course,
                session=self.session,
                term=self.term,
                request=self.lesson_request
            )
            lesson.full_clean()

    def test_invalid_lesson_with_different_course(self):
        # Create a new course
        another_course = Course.objects.create(
            name='Advanced Python',
            description='An advanced Python course',
            level='advanced',
            price_per_hour=60.0,
            ProgrammingLanguage=self.expertise
        )

        with self.assertRaises(ValidationError):
            lesson = Lesson(
                student=self.student,
                tutor=self.tutor,
                course=another_course,
                session=self.session,
                term=self.term,
                request=self.lesson_request
            )
            lesson.full_clean()

    def test_str_method(self):
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.session,
            term=self.term,
            request=self.lesson_request
        )
        expected_str = f"Lesson for {self.student_user.username} with {self.tutor_user.username}"
        self.assertEqual(str(lesson), expected_str)

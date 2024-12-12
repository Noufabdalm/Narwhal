from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from tutorials.models import (
    CancellationRequest, Lesson, Course, Term, TutorSession, Student, Tutor, LessonRequest
)

User = get_user_model()  


class CancellationRequestTestCase(TestCase):
    def setUp(self):
        # Create test user for the tutor
        self.tutor_user = User.objects.create_user(
            username='tutor1', password='password', email='tutor1@example.com'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create test user for the student
        self.student_user = User.objects.create_user(
            username='student1', password='password', email='student1@example.com'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            learning_level='beginner'
        )

        # Create a course
        self.course = Course.objects.create(
            name="Python Programming",
            description="Learn Python basics",
            level="beginner",
            price_per_hour=20.00
        )

        # Create a term
        self.term = Term.objects.create(
            name="autumn",
            start_date=now().date() + timedelta(days=30),
            end_date=now().date() + timedelta(days=120)
        )

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            term=self.term,
            frequency='weekly',
            duration_minutes=60,
            status='allocated',
        )

        # Create a session
        self.session = TutorSession.objects.create(
            tutor=self.tutor,
            time="10:00:00",
            term=self.term,
            start_day=1,
            start_date=self.term.start_date,
            duration_minutes=60,
            frequency="weekly",
            is_booked=False
        )

        # Create a lesson
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.session,
            term=self.term,
            request=self.lesson_request,
            rollover=True
        )

    def test_cancellation_request_creation(self):
        """Test that a cancellation request can be created successfully."""
        cancellation_request = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Need to change my schedule.",
            status="pending"
        )
        self.assertEqual(cancellation_request.user, self.student_user)
        self.assertEqual(cancellation_request.lesson, self.lesson)
        self.assertEqual(cancellation_request.status, "pending")
        self.assertFalse(cancellation_request.is_late)

    def test_check_and_mark_late(self):
        """Test that a cancellation request is marked as late if the term start date is within 14 days."""
        self.term.start_date = now().date() + timedelta(days=10)
        self.term.save()
        cancellation_request = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Need to change my schedule.",
            status="pending"
        )
        cancellation_request.save()
        self.assertTrue(cancellation_request.is_late)

    def test_lesson_cancellation_with_request(self):
        """Test that canceling a lesson updates its status to 'cancelled' and retains the request."""
        cancellation_request = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Change in schedule.",
            status="pending"
        )
        # Approve the cancellation request
        cancellation_request.status = 'approved'
        cancellation_request.save()

        # Update lesson status
        self.lesson.rollover = False
        self.lesson.save()

        # Assertions
        self.assertEqual(cancellation_request.status, "approved")
        self.assertFalse(self.lesson.rollover)
        self.assertEqual(self.lesson.request, self.lesson_request)

    def test_cancellation_request_rejection(self):
        """Test rejecting a cancellation request does not affect the lesson."""
        cancellation_request = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Change in schedule.",
            status="pending"
        )
        # Reject the cancellation request
        cancellation_request.status = "rejected"
        cancellation_request.save()

        # Assertions
        self.assertEqual(cancellation_request.status, "rejected")
        self.assertTrue(self.lesson.rollover)

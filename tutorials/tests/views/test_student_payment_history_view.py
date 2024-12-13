from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student, Invoice, Lesson, Course, Tutor, Term, LessonRequest, TutorSession
from datetime import date, time


class StudentPaymentHistoryViewTestCase(TestCase):
    """Tests for the student_payment_history_view function."""

    def setUp(self):
        # Create a student user
        self.student_user = User.objects.create_user(
            username='@studentjohndoe',
            first_name='John',
            last_name='Doe',
            email='studentjohndoe@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.student_user, learning_level='beginner')

        # Create a tutor and course
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
            price_per_hour=20.0
        )

        # Create a term and session
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

        # Create a lesson and invoice
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
        self.invoice_paid = Invoice.objects.create(
            student=self.student,
            lesson=self.lesson,
            total_amount=100.00,
            due_date=date(2024, 10, 1),
            status="paid"
        )
        self.invoice_unpaid = Invoice.objects.create(
            student=self.student,
            lesson=self.lesson,
            total_amount=150.00,
            due_date=date(2024, 10, 15),
            status="unpaid"
        )

        # URL for student payment history view
        self.url = reverse('student_payment_history')

    def test_payment_history_url(self):
        """Test that the URL for payment history is correct."""
        self.assertEqual(self.url, '/payment-history/')

    def test_get_payment_history(self):
        """Test that a logged-in student can view their payment history."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_payment_history.html')

        invoices = response.context['invoices']
        self.assertEqual(len(invoices), 2)
        self.assertEqual(invoices[0], self.invoice_unpaid)  # Ordered by due date
        self.assertEqual(invoices[1], self.invoice_paid)

    def test_filter_paid_invoices(self):
        """Test that the student can filter to view only paid invoices."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, {'status': 'paid'})
        self.assertEqual(response.status_code, 200)

        invoices = response.context['invoices']
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0], self.invoice_paid)

    def test_filter_unpaid_invoices(self):
        """Test that the student can filter to view only unpaid invoices."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, {'status': 'unpaid'})
        self.assertEqual(response.status_code, 200)

        invoices = response.context['invoices']
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0], self.invoice_unpaid)

    def test_no_invoices(self):
        """Test that a student with no invoices sees an appropriate message."""
        Invoice.objects.filter(student=self.student).delete()
        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url)

        # Check the message is present
        messages = list(response.context.get('messages', []))
        self.assertEqual(len(messages), 0)

        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'student_payment_history.html')
        self.assertEqual(len(response.context['invoices']), 0)

    def test_redirect_when_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        redirect_url = f"{reverse('log_in')}?next={self.url}"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

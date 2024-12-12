from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Invoice, Student, Lesson, Course, Tutor, Term, LessonRequest, TutorSession
from datetime import date, time

class AdminInvoiceViewTestCase(TestCase):
    """Tests for the admin invoice view."""

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='@adminuser',
            email='admin@example.com',
            password='AdminPassword123'
        )

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

        # Create a lesson and invoices
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

        # URL for admin invoice view
        self.url = reverse('admin_invoice_view')

    def test_admin_invoice_view_url(self):
        """Test that the URL for admin invoice view is correct."""
        self.assertEqual(self.url, '/admin-invoices/')

    def test_authenticated_user_can_view_invoices(self):
        """Test that any authenticated user can view invoices."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_invoice_view.html')
        self.assertEqual(len(response.context['invoices']), 2)

    def test_filter_invoices_by_status(self):
        """Test filtering invoices by status."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, {'status': 'paid'})
        self.assertEqual(len(response.context['invoices']), 1)
        self.assertEqual(response.context['invoices'][0], self.invoice_paid)

    def test_filter_invoices_by_student(self):
        """Test filtering invoices by student username."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, {'student': 'johndoe'})
        self.assertEqual(len(response.context['invoices']), 2)

    def test_unauthenticated_user_redirect(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn(reverse('log_in'), response.url)  

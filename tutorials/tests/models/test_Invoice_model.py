from django.test import TestCase
from django.utils.timezone import now
from tutorials.models import Invoice, Student, Lesson, User, Tutor, TutorSession, LessonRequest, Term, Course, Expertise
from datetime import date
from django.core.exceptions import ValidationError


class InvoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user for the tutor
        cls.tutor_user = User.objects.create_user(
            username='testtutor',
            email='testtutor@example.com',
            password='password123'
        )
        # Create the tutor instance
        cls.tutor = Tutor.objects.create(user=cls.tutor_user)

        # Create expertise for the tutor and link it
        cls.expertise = Expertise.objects.create(name="Python")
        cls.tutor.expertise.add(cls.expertise)

        # Create test user for the student
        cls.student_user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='password123'
        )
        # Create the student instance
        cls.student = Student.objects.create(user=cls.student_user, learning_level='beginner')

        # Create a term
        cls.term = Term.objects.create(name='spring', start_date=date(2025, 1, 1), end_date=date(2025, 6, 1))

        # Create a course
        cls.course = Course.objects.create(
            name="Python Beginner",
            description="Introductory course for Python",
            level="beginner",
            price_per_hour=20,
            ProgrammingLanguage=cls.expertise
        )

        # Create a lesson request
        cls.lesson_request = LessonRequest.objects.create(
            student=cls.student,
            course=cls.course,
            frequency="weekly",
            duration_minutes=60,
            term=cls.term,
            status="pending"
        )

        # Create a tutor session
        cls.tutor_session = TutorSession.objects.create(
            course=cls.course,
            term=cls.term,
            tutor=cls.tutor,
            start_date=date(2025, 1, 10),
            start_day=0,  # Monday
            time="09:00",
            duration_minutes=60,
            is_booked=False
        )

        # Create a lesson
        cls.lesson = Lesson.objects.create(
            student=cls.student,
            tutor=cls.tutor,
            course=cls.course,
            start_date=cls.tutor_session.start_date,
            start_day=cls.tutor_session.start_day,
            end_date=cls.term.end_date,
            session=cls.tutor_session,
            term=cls.term,
            request=cls.lesson_request,
            rollover=False
        )

        # Create the invoice
        cls.invoice = Invoice.objects.create(
            student=cls.student,
            lesson=cls.lesson,
            total_amount=240.00,
            due_date=cls.lesson.start_date,
            status='unpaid'
        )

    def test_invoice_creation(self):
        """Test that the invoice is created successfully."""
        invoice = Invoice.objects.get(id=self.invoice.id)
        self.assertEqual(invoice.student, self.student)
        self.assertEqual(invoice.lesson, self.lesson)
        self.assertEqual(invoice.total_amount, 240.00)
        self.assertEqual(invoice.due_date, self.lesson.start_date)
        self.assertEqual(invoice.status, 'unpaid')

    def test_invoice_str_method(self):
        """Test the __str__ method of the Invoice model."""
        invoice = Invoice.objects.get(id=self.invoice.id)
        expected_str = f"Invoice for {self.student.user.username} ({invoice.status})"
        self.assertEqual(str(invoice), expected_str)

    def test_invoice_total_amount_update(self):
        """Test updating the total_amount field."""
        self.invoice.total_amount = 300.00
        self.invoice.save()
        self.assertEqual(self.invoice.total_amount, 300.00)

    def test_invoice_due_date(self):
        """Test the due_date is correctly set."""
        self.assertEqual(self.invoice.due_date, self.lesson.start_date)

    def test_invoice_status_choices(self):
        """Test that the status choices are correctly enforced."""
        # Valid status
        self.invoice.status = 'paid'
        self.invoice.full_clean()  
        self.assertEqual(self.invoice.status, 'paid')

        # Invalid status
        with self.assertRaises(ValidationError) as context:
            self.invoice.status = 'invalid_status'
            self.invoice.full_clean()  

        
        self.assertIn("Value 'invalid_status' is not a valid choice.", str(context.exception))


    def test_related_models(self):
        """Test that related models can be accessed from the invoice."""
        self.assertEqual(self.invoice.student, self.student)
        self.assertEqual(self.invoice.lesson, self.lesson)
        self.assertEqual(self.invoice.lesson.tutor, self.tutor)

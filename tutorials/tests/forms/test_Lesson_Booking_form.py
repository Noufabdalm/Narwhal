from django.test import TestCase
from tutorials.forms import StudentSelectionForm, RequestSelectionForm, SessionSelectionForm
from tutorials.models import Student, LessonRequest, TutorSession, Term, Course, Tutor, User
from datetime import date
from django.urls import reverse

class LessonBookingFormsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user and student
        cls.user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='password123',
            first_name='Test',
            last_name='Student'
        )
        cls.student = Student.objects.create(
            user=cls.user,
            learning_level='beginner'
        )

        # Create term, course, and tutor
        cls.term = Term.objects.create(
            name='spring',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
        )
        cls.course = Course.objects.create(
            name="Python Beginner",
            description="Introductory Python Course",
            level="beginner",
            price_per_hour=20,
        )
        cls.tutor_user = User.objects.create_user(
            username='testtutor',
            email='testtutor@example.com',
            password='password123',
            first_name='Test',
            last_name='Tutor'
        )
        cls.tutor = Tutor.objects.create(user=cls.tutor_user)

        # Create a tutor session
        cls.session = TutorSession.objects.create(
            tutor=cls.tutor,
            term=cls.term,
            time="10:00:00",
            start_day=0,
            start_date=date(2025, 1, 6),
            end_date=date(2025, 6, 1),
            duration_minutes=60,
            frequency="weekly",
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

    def test_student_selection_form_valid(self):
        """Test StudentSelectionForm with valid data."""
        form = StudentSelectionForm(data={'student': self.student.id})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['student'], self.student)

    def test_student_selection_form_invalid(self):
        """Test StudentSelectionForm with invalid data."""
        form = StudentSelectionForm(data={'student': None})
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_request_selection_form_queryset(self):
        """Test RequestSelectionForm populates queryset dynamically."""
        form = RequestSelectionForm()
        form.fields['request'].queryset = LessonRequest.objects.filter(student=self.student, status='pending')
        self.assertIn(self.lesson_request, form.fields['request'].queryset)

    def test_request_selection_form_valid(self):
        """Test RequestSelectionForm with valid data."""
        form = RequestSelectionForm(data={'request': self.lesson_request.id})
        form.fields['request'].queryset = LessonRequest.objects.filter(student=self.student, status='pending')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['request'], self.lesson_request)

    def test_request_selection_form_invalid(self):
        """Test RequestSelectionForm with invalid data."""
        form = RequestSelectionForm(data={'request': None})
        form.fields['request'].queryset = LessonRequest.objects.filter(student=self.student, status='pending')
        self.assertFalse(form.is_valid())
        self.assertIn('request', form.errors)

    def test_session_selection_form_queryset(self):
        """Test SessionSelectionForm populates queryset dynamically."""
        form = SessionSelectionForm()
        form.fields['session'].queryset = TutorSession.objects.filter(
            frequency = self.lesson_request.frequency,
            term=self.lesson_request.term,
            is_booked=False
        )
        self.assertIn(self.session, form.fields['session'].queryset)

    def test_session_selection_form_valid(self):
        """Test SessionSelectionForm with valid data."""
        form = SessionSelectionForm(data={'session': self.session.id})
        form.fields['session'].queryset = TutorSession.objects.filter(
            duration_minutes = self.lesson_request.duration_minutes,
            frequency = self.lesson_request.frequency,
            term=self.lesson_request.term,
            is_booked=False
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['session'], self.session)


        """
        There is no test to assess selection form invalid since selecting a session is not required
        """
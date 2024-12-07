from django.test import TestCase
from tutorials.forms import LessonRequestForm
from tutorials.models import Course, Term, TutorSession

class LessonRequestFormTestCase(TestCase):
    """Unit tests for the LessonRequestForm."""

    def setUp(self):
        self.course = Course.objects.create(name='Math 101', level='beginner', price_per_hour=20.0)
        self.term = Term.objects.create(start_date='2024-01-01', end_date='2024-06-01')

        self.valid_data = {
            'course': self.course.id,
            'frequency': TutorSession.FREQUENCY_CHOICES[0][0], 
            'term': self.term.id,
            'preferred_time': TutorSession.TIME_CHOICES[0][0],  
        }

    def test_form_has_required_fields(self):
        form = LessonRequestForm()
        self.assertIn('course', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('term', form.fields)
        self.assertIn('preferred_time', form.fields)

    def test_form_accepts_valid_data(self):
        form = LessonRequestForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_missing_course(self):
        self.valid_data['course'] = None
        form = LessonRequestForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('course', form.errors)

    def test_form_rejects_invalid_frequency(self):
        self.valid_data['frequency'] = 'invalid_frequency'
        form = LessonRequestForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('frequency', form.errors)

    def test_form_rejects_missing_term(self):
        self.valid_data['term'] = None
        form = LessonRequestForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_form_rejects_invalid_preferred_time(self):
        self.valid_data['preferred_time'] = 'invalid_time'
        form = LessonRequestForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('preferred_time', form.errors)

    def test_form_rejects_blank_data(self):
        form = LessonRequestForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('course', form.errors)
        self.assertIn('frequency', form.errors)
        self.assertIn('term', form.errors)
        self.assertIn('preferred_time', form.errors)
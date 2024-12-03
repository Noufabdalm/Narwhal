from django.test import TestCase
from tutorials.models import Course, Expertise
from tutorials.forms import CourseForm

class CourseFormTestCase(TestCase):

    def setUp(self):
        self.expertise_python = Expertise.objects.create(name="python")

    def test_valid_course_form(self):
        form_data = {
            'name': 'Python Beginner Course',
            'description': 'Learn Python from scratch.',
            'level': 'beginner',
            'price_per_hour': 20.0,
            'ProgrammingLanguage': self.expertise_python.id
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        course = form.save(commit=False)
        self.assertEqual(course.name, form_data['name'])
        self.assertEqual(course.description, form_data['description'])
        self.assertEqual(course.level, form_data['level'])
        self.assertEqual(course.price_per_hour, form_data['price_per_hour'])
        self.assertEqual(course.ProgrammingLanguage, self.expertise_python)

    def test_invalid_course_form_missing_required_fields(self):
        form_data = {
            'name': '',  # Missing name
            'description': '',
            'level': '',
            'price_per_hour': '',
            'ProgrammingLanguage': ''
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('level', form.errors)
        self.assertIn('price_per_hour', form.errors)
        self.assertIn('ProgrammingLanguage', form.errors)

    def test_invalid_course_form_invalid_price(self):
        form_data = {
            'name': 'Invalid Price Course',
            'description': 'Test description',
            'level': 'beginner',
            'price_per_hour': 'invalid',
            'ProgrammingLanguage': self.expertise_python.id
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price_per_hour', form.errors)

    def test_invalid_course_form_invalid_level(self):
        form_data = {
            'name': 'Invalid Level Course',
            'description': 'Test description',
            'level': 'invalid_level',
            'price_per_hour': 20.0,
            'ProgrammingLanguage': self.expertise_python.id
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('level', form.errors)

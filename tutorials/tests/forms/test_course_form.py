from django.test import TestCase
from tutorials.models import Expertise
from tutorials.forms import CourseForm

class CourseFormTestCase(TestCase):

    def setUp(self):
        self.expertise_python = Expertise.objects.create(name="python")
        self.valid_form_data = {
            'name': 'Python Beginner Course',
            'description': 'This is a beginner course for Python.',
            'level': 'beginner',
            'price_per_hour': 20.0,
            'ProgrammingLanguage': self.expertise_python.id
        }

    def test_course_form_valid(self):
        form_data = {
            'level': 'beginner',
            'ProgrammingLanguage': self.expertise_python.id
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        course = form.save(commit=False)
        self.assertEqual(course.name, "Python Beginner Course")
        self.assertEqual(course.description, "This is a beginner course for Python")
        self.assertEqual(course.price_per_hour, 20.0)

    def test_course_form_missing_required_fields(self):
        form_data = {}
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('level', form.errors)
        self.assertIn('ProgrammingLanguage', form.errors)

    def test_course_form_invalid_level(self):
        form_data = self.valid_form_data.copy()
        form_data['level'] = 'invalid_level'
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('level', form.errors)

    def test_course_form_valid_description_generation(self):
        form_data = {
            'level': 'intermediate',
            'ProgrammingLanguage': self.expertise_python.id
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        course = form.save(commit=False)
        self.assertEqual(course.description, "This is an intermediate course for Python")



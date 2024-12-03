from django.test import TestCase
from tutorials.forms import ExpertiseForm
from tutorials.models import Expertise

class ExpertiseFormTestCase(TestCase):
    def test_valid_data(self):
        form = ExpertiseForm(data={"name": "Java"})
        self.assertTrue(form.is_valid())
        expertise = form.save()
        self.assertEqual(expertise.name, "java")

    def test_invalid_data_empty_name(self):
        form = ExpertiseForm(data={"name": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_duplicate_name_case_insensitive(self):
        Expertise.objects.create(name="a")
        form = ExpertiseForm(data={"name": "A"})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn("already exists", str(form.errors["__all__"]))

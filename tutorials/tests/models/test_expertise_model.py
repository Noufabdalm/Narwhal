"""Unit tests for the Expertise model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Expertise


class ExpertiseModelTestCase(TestCase):

    def setUp(self):
        self.expertise = Expertise.objects.create(name='python')

    def test_valid_expertise(self):
        self._assert_expertise_is_valid()

    def test_name_must_not_be_blank(self):
        self.expertise.name = ''
        self._assert_expertise_is_invalid()

    def test_name_must_be_unique(self):
        second_expertise = Expertise(name='python')
        with self.assertRaises(ValidationError):
            second_expertise.full_clean()

    def test_name_is_case_insensitive_unique(self):
        second_expertise = Expertise(name='Python')
        with self.assertRaises(ValidationError):
            second_expertise.full_clean()

    def test_name_can_be_50_characters_long(self):
        self.expertise.name = 'x' * 50
        self._assert_expertise_is_valid()

    def test_name_cannot_be_over_50_characters_long(self):
        self.expertise.name = 'x' * 51
        self._assert_expertise_is_invalid()

    def test_name_is_stored_lowercase(self):
        self.expertise.name = 'Python'
        self.expertise.save()
        self.assertEqual(self.expertise.name, 'python')

    def _assert_expertise_is_valid(self):
        try:
            self.expertise.full_clean()
        except ValidationError:
            self.fail('Test expertise should be valid')

    def _assert_expertise_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.expertise.full_clean()

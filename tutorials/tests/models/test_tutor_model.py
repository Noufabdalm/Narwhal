"""Unit tests for the Tutor model."""
from django.test import TestCase
from tutorials.models import User, Tutor, Expertise
from django.core.exceptions import ValidationError

class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='@tutoruser',
            email='tutor@example.com',
            password='Password123',
            first_name='Tutor',
            last_name='User'
        )
        self.expertise = Expertise.objects.create(name='python')
        self.tutor = Tutor.objects.create(user=self.user)
        self.tutor.expertise.add(self.expertise)

    def test_valid_tutor(self):
        self._assert_tutor_is_valid()

    def test_user_is_associated(self):
        self.assertEqual(self.tutor.user, self.user)

    def test_tutor_can_have_multiple_expertise(self):
        second_expertise = Expertise.objects.create(name='javascript')
        self.tutor.expertise.add(second_expertise)
        self.assertEqual(self.tutor.expertise.count(), 2)

    def test_tutor_str_representation(self):
        self.assertEqual(str(self.tutor), "Tutor: Tutor User")

    def _assert_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail('Test tutor should be valid')

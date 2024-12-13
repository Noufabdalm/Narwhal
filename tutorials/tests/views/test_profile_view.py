"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import UserForm
from tutorials.models import User
from tutorials.tests.helpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        # Create a unique student user for the test
        self.student_user = User.objects.create_user(
            username='@student',
            email='student@example.com',
            password='Password123',
            first_name='StudentFirstName',
            last_name='StudentLastName'
        )

        # Create a conflicting user to test duplicate username errors
        self.duplicate_user = User.objects.create_user(
            username='@duplicate',
            email='duplicate@example.com',
            password='Password123'
        )

        self.url = reverse('profile')
        self.form_input = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'username': 'NewUsername',
            'email': 'newemail@example.com',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.student_user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update_due_to_invalid_data(self):
        self.client.login(username=self.student_user.username, password='Password123')

        # Ensure initial data is correct
        self.assertEqual(self.student_user.first_name, 'StudentFirstName')
        self.assertEqual(self.student_user.last_name, 'StudentLastName')

        # Attempt update with invalid username
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()

        # Check that no new users were created
        self.assertEqual(after_count, before_count)

        # Verify that response renders the profile page with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)

        # Verify that the database has not been updated
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'StudentFirstName')
        self.assertEqual(self.student_user.last_name, 'StudentLastName')
        self.assertEqual(self.student_user.username, '@student')
        self.assertEqual(self.student_user.email, 'student@example.com')

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.student_user.username, password='Password123')

        # Ensure initial data is correct
        self.assertEqual(self.student_user.username, '@student')

        # Attempt to update with a duplicate username
        self.form_input['username'] = self.duplicate_user.username
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()

        # Check that no new users were created
        self.assertEqual(after_count, before_count)

        # Verify that response renders the profile page with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)

        # Verify that the database has not been updated
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@student')
        self.assertEqual(self.student_user.first_name, 'StudentFirstName')
        self.assertEqual(self.student_user.last_name, 'StudentLastName')
        self.assertEqual(self.student_user.email, 'student@example.com')

    def test_successful_profile_update(self):
        self.client.login(username=self.student_user.username, password='Password123')

        # Attempt a valid update
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()

        # Check that no new users were created
        self.assertEqual(after_count, before_count)

        # Verify that the user is redirected to the home page after a successful update
        response_url = reverse('home')  # Ensure this matches the redirect logic in your view
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')  # Ensure the home template is correct

        # Verify that the database has been updated
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, 'NewUsername')
        self.assertEqual(self.student_user.first_name, 'NewFirstName')
        self.assertEqual(self.student_user.last_name, 'NewLastName')
        self.assertEqual(self.student_user.email, 'newemail@example.com')


    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

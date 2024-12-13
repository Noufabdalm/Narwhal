from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import User, Student, Admin, Tutor


class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    def setUp(self):
        self.url = reverse('home')

        # Create test users for different roles
        self.student_user = User.objects.create_user(
            username='@studentjohndoe', password='Password123', email='student@example.com'
        )
        self.student = Student.objects.create(user=self.student_user, learning_level='beginner')

        self.admin_user = User.objects.create_user(
            username='@adminjohndoe', password='Password123', email='admin@example.com'
        )
        self.admin = Admin.objects.create(user=self.admin_user)

        self.tutor_user = User.objects.create_user(
            username='@tutorjohndoe', password='Password123', email='tutor@example.com'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a regular user without a profile
        self.no_profile_user = User.objects.create_user(
            username='@noprofile', password='Password123', email='noprofile@example.com'
        )

    def test_home_url(self):
        """Test that the home URL resolves correctly."""
        self.assertEqual(self.url, '/')

    def test_get_home(self):
        """Test that unauthenticated users can access the home page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_student_redirect(self):
        """Test that a student is redirected to their dashboard."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('student_dashboard'))
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_admin_redirect(self):
        """Test that an admin is redirected to their dashboard."""
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_tutor_redirect(self):
        """Test that a tutor is redirected to their dashboard."""
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('tutor_dashboard'))
        self.assertTemplateUsed(response, 'tutor_dashboard.html')

    # def test_no_profile_redirect(self):
    #     """Test that a user with no profile is redirected tos the home page with an error message."""
    #     self.client.login(username=self.no_profile_user.username, password='Password123')
    #     response = self.client.get(self.url, follow=True)
    #     self.assertRedirects(response, self.url)

    #     # Check that an error message is displayed
    #     messages = list(get_messages(response.wsgi_request))
    #     self.assertTrue(any("You are not authorized to access this page." in str(msg) for msg in messages))

    def test_redirect_when_logged_in(self):
        """Test that a logged-in user with a profile is redirected to the appropriate dashboard."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('student_dashboard'))

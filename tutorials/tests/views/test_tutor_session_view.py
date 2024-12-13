from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Admin, Tutor, Term, TutorSession
from datetime import date, time

User = get_user_model()


class TutorSessionsViewTest(TestCase):
    def setUp(self):
        # Create admin user and admin profile
        self.admin_user = User.objects.create_user(
            username="adminuser", password="password123", email="admin@example.com"
        )
        self.admin = Admin.objects.create(user=self.admin_user)

        # Create another user (non-admin) for authentication testing
        self.non_admin_user = User.objects.create_user(
            username="nonadminuser", password="password123", email="nonadmin@example.com"
        )

        # Create terms
        self.term1 = Term.objects.create(
            name="spring", start_date=date(2025, 1, 1), end_date=date(2025, 6, 1)
        )
        self.term2 = Term.objects.create(
            name="autumn", start_date=date(2025, 9, 1), end_date=date(2025, 12, 1)
        )

       
        self.tutor1_user = User.objects.create_user(
            username="tutor1",
            password="password123",
            email="tutor1@example.com",
            first_name="John",
            last_name="Doe",
        )
        self.tutor1 = Tutor.objects.create(user=self.tutor1_user)

        self.tutor2_user = User.objects.create_user(
            username="tutor2",
            password="password123",
            email="tutor2@example.com",
            first_name="Jane",
            last_name="Smith",
        )
        self.tutor2 = Tutor.objects.create(user=self.tutor2_user)

        # Create tutor sessions
        self.session1 = TutorSession.objects.create(
            tutor=self.tutor1,
            term=self.term1,
            time=time(10, 0),
            start_day=0,
            duration_minutes=60,
            frequency="weekly",
            is_booked=True,
        )

        self.session2 = TutorSession.objects.create(
            tutor=self.tutor2,
            term=self.term2,
            time=time(14, 0),
            start_day=2,
            duration_minutes=120,
            frequency="fortnightly",
            is_booked=False,
        )

        self.tutor_sessions_url = reverse("admin_tutor_sessions")

    def test_view_requires_admin_authentication(self):
        self.client.login(username="nonadminuser", password="password123")
        response = self.client.get(self.tutor_sessions_url)

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(response.status_code, 302)

        self.client.logout()
        response = self.client.get(self.tutor_sessions_url)

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(response.status_code, 302)

    def test_view_all_tutor_sessions_for_admin(self):
        self.client.login(username="adminuser", password="password123")
        response = self.client.get(self.tutor_sessions_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe") 
        self.assertContains(response, "Jane Smith")
        self.assertTemplateUsed(response, "admin_tutor_sessions.html")

    
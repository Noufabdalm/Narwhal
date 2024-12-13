from django.test import TestCase, Client
from django.contrib.auth.models import User
from tutorials.models import Tutor, TutorSession, Term
from datetime import date, time

class TutorSessionsPageTest(TestCase):
    def setUp(self):
        # Create a user and a tutor profile
        self.user = User.objects.create_user(username='test_tutor', password='testpassword')
        self.tutor = Tutor.objects.create(user=self.user)

        # Create a term
        self.term = Term.objects.create(
            name="Test Term",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1)
        )

        # Create some tutor sessions
        self.session1 = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(10, 0),
            term=self.term,
            start_day=0,  # Monday
            duration_minutes=60,
            frequency='weekly',
            is_booked=False
        )
        self.session2 = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(14, 0),
            term=self.term,
            start_day=2,  # Wednesday
            duration_minutes=120,
            frequency='weekly',
            is_booked=True
        )

        # Set up the client for testing
        self.client = Client()

    def test_tutor_sessions_page_access(self):
        # Test access without login
        response = self.client.get('/tutor/sessions/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        # Test access with a logged-in user
        self.client.login(username='test_tutor', password='testpassword')
        response = self.client.get('/tutor/sessions/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_sessions.html')

    def test_tutor_sessions_context(self):
        # Login as tutor
        self.client.login(username='test_tutor', password='testpassword')

        # Get the response
        response = self.client.get('/tutor/sessions/')

        # Check if the sessions are in the context
        self.assertIn('page_obj', response.context)
        self.assertIn('sessions', response.context)

        # Verify the sessions data
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 2)
        self.assertIn(self.session1, sessions)
        self.assertIn(self.session2, sessions)

    def test_tutor_sessions_pagination(self):
        # Create additional sessions to test pagination
        for i in range(15):
            TutorSession.objects.create(
                tutor=self.tutor,
                time=time(9, 0),
                term=self.term,
                start_day=i % 5,  # Distribute across weekdays
                duration_minutes=60,
                frequency='weekly',
                is_booked=False
            )

        # Login as tutor
        self.client.login(username='test_tutor', password='testpassword')

        # Get the first page
        response = self.client.get('/tutor/sessions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sessions']), 10)  # First page should show 10 sessions

        # Get the second page
        response = self.client.get('/tutor/sessions/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sessions']), 7)  # Remaining sessions on the second page

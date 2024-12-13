from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth import get_user_model
from tutorials.models import Tutor, TutorSession, Term
from datetime import date, time, timedelta
import datetime

User = get_user_model()  # Get the custom user model dynamically
start_times = [
        time(8,0),time(9, 0),time(10,00),time(11, 00),time(12,00), time(13, 0),time(14,00), time(15,00),time(16, 00),
        time(17,00),time(18,00),time(19,00),time(20,00), time(21,00), time(22,00)
        ]

        # List of days of the week (0 = Monday, ..., 6 = Sunday)
days_of_week = [0, 1, 2, 3, 4]

class TutorSessionsPageTest(TestCase):
    def setUp(self):
        # Create a user and a tutor profile
        self.user = User.objects.create_user(username='test_tutor', password='testpassword')
        self.tutor = Tutor.objects.create(user=self.user)


        # Create a term
        self.term = Term.objects.create(
            name="spring",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1)
        )

        # Create some tutor sessions
        self.session1 = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(0, 0),
            term=self.term,
            start_day=0,  # Monday
            duration_minutes=60,
            frequency='weekly',
            is_booked=False
        )
        self.session2 = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(4, 0),
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
            session_time = start_times[i % len(start_times)]
            session_day = days_of_week[i % len(days_of_week)]

            # Create the session
            TutorSession.objects.create(
                tutor=self.tutor,
                time=session_time,
                term=self.term,
                start_day=session_day,  # Assign calculated day
                duration_minutes=60,
                frequency='weekly',
                is_booked=(i % 2 == 0)  # Alternate booked status
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

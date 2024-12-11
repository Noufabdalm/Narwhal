from datetime import date, time
from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.models import TutorSession, Tutor, Course, Term, Expertise, User

class TutorSessionModelTestCase(TestCase):
    

    def setUp(self):
        self.term = Term.objects.create(
            name='autumn',
            start_date=date(2024, 9, 2),
            end_date=date(2024, 12, 16)
        )
        self.user = User.objects.create_user(
            username="@tutor1",
            email="tutor1@example.com",
            password="password123",
            first_name="Tutor",
            last_name="One"
        )
        self.tutor = Tutor.objects.create(user=self.user)
        self.expertise = Expertise.objects.create(name="Python")
        self.course = Course.objects.create(
            name="Python for Beginners",
            description="Basics in Python",
            level="beginner",
            price_per_hour=20.0,
            ProgrammingLanguage=self.expertise
        )
        self.session = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(10, 0),
            term=self.term,
            start_day=4,  # Friday
            frequency="weekly",
            duration_minutes=60
        )

    def test_valid_tutor_session(self):
        """Test if a valid TutorSession instance is created successfully."""
        self.assertIsInstance(self.session, TutorSession)
        self.assertEqual(self.session.start_date, self.session.calculate_start_date())
        self.assertEqual(self.session.end_date, self.session.calculate_end_date())

    def test_calculate_start_date(self):
        """Test start date calculation based on term and start day."""
        calculated_start_date = self.session.calculate_start_date()
        self.assertEqual(calculated_start_date, date(2024, 9, 6))  # First Friday in the term

    def test_calculate_end_date(self):
        """Test end date calculation based on term and session frequency."""
        calculated_end_date = self.session.calculate_end_date()
        self.assertEqual(calculated_end_date, date(2024, 12, 13))  # Last valid session in the term

    def test_calculate_term_cost(self):
        """Test term cost calculation based on session details."""
        expected_cost = 12 * (20.0 * (60 / 60.0))  
        self.assertEqual(self.session.calculate_term_cost(self.course), expected_cost)

    def test_duplicate_session_is_invalid(self):
        """Test that creating a duplicate TutorSession raises a ValidationError."""
        with self.assertRaises(ValidationError):
            duplicate_session = TutorSession(
                tutor=self.tutor,
                time=self.session.time,
                term=self.term,
                start_day=self.session.start_day
            )
            duplicate_session.save()

    def test_end_date_is_within_term(self):
        """Test that the end date does not exceed the term end date."""
        self.assertLessEqual(self.session.end_date, self.term.end_date)

    def test_clean_method(self):
        """Test the clean method for duplicate sessions."""
        self.session.clean()  

    def test_save_method_sets_start_and_end_dates(self):
        """Test the save method calculates and sets start and end dates."""
        session = TutorSession.objects.create(
            tutor=self.tutor,
            time=time(11, 0),
            term=self.term,
            start_day=3,  # Thursday
            frequency="fortnightly",
            duration_minutes=60
        )
        self.assertEqual(session.start_date, session.calculate_start_date())
        self.assertEqual(session.end_date, session.calculate_end_date())

    def test_str_method(self):
        """Test the string representation of a TutorSession instance."""
        self.assertEqual(str(self.session), "@tutor1 -(Available)")

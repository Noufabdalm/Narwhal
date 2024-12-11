from django.test import TestCase
from tutorials.models import Term
from datetime import date
from django.core.exceptions import ValidationError

class TermModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a Term instance for testing
        cls.term = Term.objects.create(
            name="spring",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 4, 15),
        )

    def test_term_creation(self):
        """Test that a Term instance is created successfully."""
        term = Term.objects.get(id=self.term.id)
        self.assertEqual(term.name, "spring")
        self.assertEqual(term.start_date, date(2025, 1, 1))
        self.assertEqual(term.end_date, date(2025, 4, 15))
        self.assertEqual(str(term), "January-Easter")  

    def test_term_name_choices(self):
        """Test that the Term name choices are valid."""
        term = Term.objects.get(id=self.term.id)
        valid_choices = [choice[0] for choice in Term.TERM_CHOICES]
        self.assertIn(term.name, valid_choices)

    def test_term_date_constraints(self):
        """Test that the start_date is before the end_date."""
        term = Term.objects.get(id=self.term.id)
        self.assertLess(term.start_date, term.end_date)

    def test_invalid_term_name(self):
        """Test that creating a Term with an invalid name raises an error."""
        with self.assertRaises(ValidationError):
            Term.objects.create(
                name="invalid_name", 
                start_date=date(2025, 1, 1),
                end_date=date(2025, 4, 15),
            )

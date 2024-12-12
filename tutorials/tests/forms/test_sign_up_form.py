"""Unit tests of the sign up forms."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tutorials.forms import SignUpForm, TutorSignUpForm
from tutorials.models import User, Student, Tutor, Expertise


class SignUpFormsTestCase(TestCase):
    """Unit tests of the sign up forms for students and tutors."""

    def setUp(self):
        # Form input for Charlie Johnson (Student)
        self.student_form_input = {
            'first_name': 'Charlie',
            'last_name': 'Johnson',
            'username': '@charliejohnson',
            'email': 'charliejohnson@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'learning_level': 'beginner'
        }

        # Form input for Jane Doe (Tutor)
        self.tutor_form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'expertise': []  # Expertise will be added dynamically
        }

        # Create expertise for tutors
        self.expertise_python = Expertise.objects.create(name='python')
        self.expertise_java = Expertise.objects.create(name='java')

        # Add expertise to the tutor form input
        self.tutor_form_input['expertise'] = [self.expertise_python.id, self.expertise_java.id]

    ### Student Sign-Up Form Tests ###
    def test_valid_student_sign_up_form(self):
        form = SignUpForm(data=self.student_form_input)
        self.assertTrue(form.is_valid())

    def test_student_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('learning_level', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        self.assertTrue(isinstance(form.fields['learning_level'], forms.ChoiceField))

    def test_student_form_must_save_correctly(self):
        form = SignUpForm(data=self.student_form_input)
        before_user_count = User.objects.count()
        before_student_count = Student.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_student_count = Student.objects.count()
        self.assertEqual(after_user_count, before_user_count + 1)
        self.assertEqual(after_student_count, before_student_count + 1)
        user = User.objects.get(username='@charliejohnson')
        self.assertEqual(user.first_name, 'Charlie')
        self.assertEqual(user.last_name, 'Johnson')
        self.assertEqual(user.email, 'charliejohnson@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        student = Student.objects.get(user=user)
        self.assertEqual(student.learning_level, 'beginner')

    ### Tutor Sign-Up Form Tests ###
    def test_valid_tutor_sign_up_form(self):
        form = TutorSignUpForm(data=self.tutor_form_input)
        self.assertTrue(form.is_valid())

    def test_tutor_form_has_necessary_fields(self):
        form = TutorSignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('expertise', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        self.assertTrue(isinstance(form.fields['expertise'], forms.ModelMultipleChoiceField))
        self.assertTrue(isinstance(form.fields['expertise'].widget, forms.CheckboxSelectMultiple))

    def test_tutor_form_must_save_correctly(self):
        form = TutorSignUpForm(data=self.tutor_form_input)
        before_user_count = User.objects.count()
        before_tutor_count = Tutor.objects.count()
        form.save()
        after_user_count = User.objects.count()
        after_tutor_count = Tutor.objects.count()
        self.assertEqual(after_user_count, before_user_count + 1)
        self.assertEqual(after_tutor_count, before_tutor_count + 1)
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        tutor = Tutor.objects.get(user=user)
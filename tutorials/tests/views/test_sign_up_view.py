"""Tests of the sign up views."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import SignUpForm, TutorSignUpForm
from tutorials.models import User, Student, Tutor, Expertise
from tutorials.tests.helpers import LogInTester


class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up views."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        # URL for student sign-up
        self.student_sign_up_url = reverse('sign_up')

        # URL for tutor sign-up
        self.tutor_sign_up_url = reverse('tutor_sign_up')

        # Form input for Charlie Johnson (Student)
        self.student_form_input = {
            'first_name': 'Charlie',
            'last_name': 'Johnson',
            'username': '@charliejohnson',
            'email': 'charliejohnson@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'learning_level': 'beginner',
        }

        # Form input for Jane Doe (Tutor)
        self.tutor_form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'expertise': [],  # Expertise will be added dynamically
        }

        # Create expertise for tutors
        self.expertise_python = Expertise.objects.create(name='python')
        self.expertise_java = Expertise.objects.create(name='java')

        # Add expertise to the tutor form input
        self.tutor_form_input['expertise'] = [self.expertise_python.id, self.expertise_java.id]

        # Existing user for login redirection tests
        self.user = User.objects.get(username='@johndoe')

    ### Student Sign-Up View Tests ###
    def test_student_sign_up_url(self):
        self.assertEqual(self.student_sign_up_url, '/sign_up/')

    def test_get_student_sign_up(self):
        response = self.client.get(self.student_sign_up_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_student_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.student_sign_up_url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccessful_student_sign_up(self):
        self.student_form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.student_sign_up_url, self.student_form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_student_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.student_sign_up_url, self.student_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user = User.objects.get(username='@charliejohnson')
        self.assertEqual(user.first_name, 'Charlie')
        self.assertEqual(user.last_name, 'Johnson')
        self.assertEqual(user.email, 'charliejohnson@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        student = Student.objects.get(user=user)
        self.assertEqual(student.learning_level, 'beginner')
        self.assertTrue(self._is_logged_in())

    ### Tutor Sign-Up View Tests ###
    def test_tutor_sign_up_url(self):
        self.assertEqual(self.tutor_sign_up_url, '/tutor_sign_up/')

    def test_get_tutor_sign_up(self):
        response = self.client.get(self.tutor_sign_up_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorSignUpForm))
        self.assertFalse(form.is_bound)

    def test_tutor_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.tutor_sign_up_url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccessful_tutor_sign_up(self):
        self.tutor_form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.tutor_sign_up_url, self.tutor_form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorSignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_tutor_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.tutor_sign_up_url, self.tutor_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        tutor = Tutor.objects.get(user=user)
        self.assertTrue(self._is_logged_in())

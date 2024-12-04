from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from tutorials.models import Student, Term, Course, LessonRequest
from datetime import timedelta

User = get_user_model()

class LessonRequestViewTest(TestCase):
    def setUp(self):
        # Create a user and student instance for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.student = Student.objects.create(user=self.user, learning_level='beginner')

        # Create a Term instance for testing
        self.term = Term.objects.create(
            name='spring',
            start_date=timezone.now().date() + timedelta(days=14),
            end_date=timezone.now().date() + timedelta(days=90)
        )

        # Create a Course instance for testing
        self.course = Course.objects.create(
            name='Python Basics',
            description='Learn the basics of Python programming.',
            level='beginner',
            price_per_hour=20.0
        )

        # Log in the user
        self.client.login(username='testuser', password='testpassword')

    def test_get_lesson_request_view(self):
        # Test GET request to display the lesson request form
        response = self.client.get(reverse('lesson_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests.html')
        self.assertContains(response, 'Learning Level')
        self.assertContains(response, 'Preferred Time')

    def test_post_lesson_request_view_valid_data(self):
        # Test POST request with valid data
        response = self.client.post(reverse('lesson_requests'), {
            'term': self.term.id,
            'course': self.course.id,
            'preferred_time': '09:00',
            'frequency': 'weekly'
        })
        
        # Check if the lesson request was created
        self.assertEqual(LessonRequest.objects.count(), 1)
        lesson_request = LessonRequest.objects.first()
        self.assertEqual(lesson_request.student, self.student)
        self.assertEqual(lesson_request.course, self.course)
        self.assertEqual(lesson_request.term, self.term)
        self.assertEqual(lesson_request.status, 'pending')

        # Check if the response redirects to the dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_post_lesson_request_view_invalid_student(self):
        # Log out the student and create a new user who is not a student
        self.client.logout()
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.client.login(username='newuser', password='newpassword')

        # Test POST request with valid data but user is not a student
        response = self.client.post(reverse('lesson_requests'), {
            'term': self.term.id,
            'course': self.course.id,
            'preferred_time': '09:00',
            'frequency': 'weekly'
        })

        # Check that no lesson request was created
        self.assertEqual(LessonRequest.objects.count(), 0)

        # Check for the error message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You must be a registered student to request a lesson.")

    def test_post_lesson_request_view_late_request(self):
        # Create a term that has already started to simulate a late request
        late_term = Term.objects.create(
            name='autumn',
            start_date=timezone.now().date() - timedelta(days=7),
            end_date=timezone.now().date() + timedelta(days=60)
        )

        # Test POST request with a late term
        response = self.client.post(reverse('lesson_requests'), {
            'term': late_term.id,
            'course': self.course.id,
            'preferred_time': '09:00',
            'frequency': 'weekly'
        })

        # Check if the lesson request was created
        self.assertEqual(LessonRequest.objects.count(), 1)
        lesson_request = LessonRequest.objects.first()
        self.assertTrue(lesson_request)
        
        # Check if a warning message is displayed
        messages = list(response.context['messages'])
        self.assertTrue(any("Warning: This request was submitted late" in str(message) for message in messages))

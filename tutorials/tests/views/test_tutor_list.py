from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Expertise


class TutorDetailsViewTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        user = User.objects.get(username='@janedoe')
        expertise_python = Expertise.objects.create(name="Python")
        self.tutor = Tutor.objects.create(user=user)
        self.tutor.expertise.add(expertise_python)
        self.url = reverse('tutor_detail', kwargs={'tutor_id': self.tutor.id})

    def test_tutor_details_url(self):
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/')

    def test_get_tutor_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_detail.html')
        tutor = response.context['tutor']
        expertise = response.context['expertise']
        self.assertEqual(tutor.user.first_name, 'Jane')
        self.assertEqual(len(expertise), 1)
        self.assertEqual(expertise.first().name, 'python')

    def test_tutor_details_with_no_sessions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_detail.html')
        self.assertContains(response, "No available sessions.")
        self.assertContains(response, "No booked sessions.")

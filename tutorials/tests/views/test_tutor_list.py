from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Expertise


class TutorListViewTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('tutor_list')
        user1 = User.objects.get(username='@janedoe')
        user2 = User.objects.get(username='@petrapickles')
        user3 = User.objects.get(username='@peterpickles')

        expertise_python = Expertise.objects.create(name="Python")
        expertise_java = Expertise.objects.create(name="Java")

        tutor1 = Tutor.objects.create(user=user1)
        tutor1.expertise.add(expertise_python)

        tutor2 = Tutor.objects.create(user=user2)
        tutor2.expertise.add(expertise_java)

        tutor3 = Tutor.objects.create(user=user3)
        tutor3.expertise.add(expertise_python, expertise_java)

    def test_tutor_list_url(self):
        self.assertEqual(self.url, '/tutors/')

    def test_get_tutor_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_list.html')
        tutors = response.context['tutors']
        self.assertEqual(tutors.count(), 3)

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
        self.assertContains(response, "No booked lessons.")

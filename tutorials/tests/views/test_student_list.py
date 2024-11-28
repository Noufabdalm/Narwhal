from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User

class StudentListViewTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('student_list')
        user1 = User.objects.get(username='@janedoe')
        user2 = User.objects.get(username='@petrapickles')
        user3 = User.objects.get(username='@peterpickles')

        Student.objects.create(user=user1, learning_level='intermediate')
        Student.objects.create(user=user2, learning_level='beginner')
        Student.objects.create(user=user3, learning_level='advanced')

    def test_student_list_url(self):
        self.assertEqual(self.url, '/students/')

    def test_get_student_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_list.html')
        students = response.context['students']
        self.assertEqual(students.count(), 3)

    def test_filter_students_by_learning_level(self):
        response = self.client.get(self.url, {'learning_level': 'advanced'})
        self.assertEqual(response.status_code, 200)
        students = response.context['students']
        self.assertEqual(students.count(), 1)
        self.assertEqual(students.first().user.first_name, 'Peter')


class StudentDetailsViewTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        user = User.objects.get(username='@janedoe')
        self.student = Student.objects.create(user=user, learning_level='intermediate')
        self.url = reverse('student_detail', kwargs={'student_id': self.student.id})

    def test_student_details_url(self):
        self.assertEqual(self.url, f'/students/{self.student.id}/')

    def test_get_student_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_detail.html')
        student = response.context['student']
        self.assertEqual(student.user.first_name, 'Jane')
        self.assertEqual(student.learning_level, 'intermediate')

    def test_student_details_with_no_lessons_or_requests(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_detail.html')
        self.assertContains(response, "No enrolled courses.")
        self.assertContains(response, "No assigned tutors.")
        self.assertContains(response, "No lesson requests.")
        self.assertContains(response, "No scheduled lessons.")




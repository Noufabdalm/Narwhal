from django.test import TestCase
from django.urls import reverse
from tutorials.models import Course, Expertise, User
from tutorials.forms import CourseForm

class CourseViewsTestCase(TestCase):
    def setUp(self):
        self.expertise_python = Expertise.objects.create(name='Python')
        self.expertise_java = Expertise.objects.create(name='Java')

        self.course1 = Course.objects.create(
            name='Python Beginner Course',
            description='Introduction to Python',
            level='beginner',
            price_per_hour=20.0,
            ProgrammingLanguage=self.expertise_python
        )
        self.course2 = Course.objects.create(
            name='Java Advanced Course',
            description='Advanced Java concepts',
            level='advanced',
            price_per_hour=60.0,
            ProgrammingLanguage=self.expertise_java
        )

        self.list_url = reverse('course_list')
        self.add_url = reverse('course_add')
        self.edit_url = reverse('course_edit', kwargs={'course_id': self.course1.id})
        self.delete_url = reverse('course_delete', kwargs={'course_id': self.course1.id})

    def test_course_list_url(self):
        self.assertEqual(self.list_url, '/courses/')

    def test_get_course_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_list.html')
        courses = response.context['courses']
        self.assertEqual(courses.count(), 2)

    def test_filter_course_list_by_name(self):
        response = self.client.get(self.list_url, {'search': 'Python'})
        self.assertEqual(response.status_code, 200)
        courses = response.context['courses']
        self.assertEqual(courses.count(), 1)
        self.assertEqual(courses.first().name, 'Python Beginner Course')

    def test_filter_course_list_by_expertise(self):
        response = self.client.get(self.list_url, {'expertise': 'Java'})
        self.assertEqual(response.status_code, 200)
        courses = response.context['courses']
        self.assertEqual(courses.count(), 1)
        self.assertEqual(courses.first().name, 'Java Advanced Course')

    def test_course_add_url(self):
        self.assertEqual(self.add_url, '/courses/add/')

    def test_get_course_add(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_add.html')
        self.assertTrue(isinstance(response.context['form'], CourseForm))

    def test_post_course_add_valid_data(self):
        data = {
            'name': 'C++ Intermediate Course',
            'description': 'Intermediate level C++',
            'level': 'intermediate',
            'price_per_hour': 40.0,
            'ProgrammingLanguage': self.expertise_python.id
        }
        response = self.client.post(self.add_url, data, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(Course.objects.filter(name='C++ Intermediate Course').exists())

    def test_post_course_add_invalid_data(self):
        data = {'name': ''}
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_add.html')
        self.assertFalse(Course.objects.filter(name='').exists())
        self.assertTrue(response.context['form'].errors)

    def test_course_edit_url(self):
        self.assertEqual(self.edit_url, f'/courses/{self.course1.id}/edit/')

    def test_get_course_edit(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_edit.html')
        self.assertTrue(isinstance(response.context['form'], CourseForm))
        self.assertEqual(response.context['course'], self.course1)

    def test_post_course_edit_invalid_data(self):
        data = {'name': ''}
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_edit.html')
        self.course1.refresh_from_db()
        self.assertNotEqual(self.course1.name, '')

    def test_course_delete_url(self):
        self.assertEqual(self.delete_url, f'/courses/{self.course1.id}/delete/')

    def test_get_course_delete_confirmation(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_delete.html')
        self.assertEqual(response.context['course'], self.course1)

    def test_post_course_delete(self):
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertFalse(Course.objects.filter(id=self.course1.id).exists())

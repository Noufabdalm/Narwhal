from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import User, Student, Term, Course, LessonRequest, TutorSession, Admin,Tutor,Lesson
from django.utils.timezone import now
from datetime import timedelta, date

class LessonRequestViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('lesson_requests')

       
        self.user = User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.user, learning_level='beginner')
        self.client.force_login(self.user)

        
        self.tutor_user = User.objects.create_user(
            username='@tutorsmith',
            email='tutorsmith@example.com',
            password='Password123'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        
        self.term = Term.objects.create(
            name="Fall 2024",
            start_date=now().date() + timedelta(days=14),
            end_date=now().date() + timedelta(days=100)
        )
        print("Term start date:", self.term.start_date)
        print("Term end date:", self.term.end_date)

       
        self.course = Course.objects.create(
            name="Python Basics",
            level="Beginner",
            price_per_hour=50.00
        )

        # Add a TutorSession
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            course=self.course,
            term=self.term,
            time=TutorSession.TIME_CHOICES[0][0],  
            start_day=0,  
            duration_minutes=60,
            frequency='weekly',
            is_booked=False
        )

    
    def test_get_lesson_request_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests.html')
        self.assertContains(response, '<form')

    def test_valid_lesson_request(self):
        form_data = {
            'term': self.term.id,
            'course': self.course.id,
            'preferred_time': '09:00:00',  
            'frequency': 'weekly',  
        }
        response = self.client.post(self.url, data=form_data)

        
        dashboard_url = reverse('dashboard')
        self.assertRedirects(response, dashboard_url)

       
        lesson_request = LessonRequest.objects.filter(student=self.student).first()
        self.assertIsNotNone(lesson_request)
        self.assertFalse(lesson_request.is_late)

    def test_late_lesson_request(self):
    # Adjust the term start date to make the request late
        self.term.start_date = now().date() + timedelta(days=10)
        self.term.save()

        form_data = {
            'term': self.term.id,
            'course': self.course.id,
            'preferred_time': TutorSession.TIME_CHOICES[0][0],  
            'frequency': TutorSession.FREQUENCY_CHOICES[0][0],  
        }
        response = self.client.post(self.url, data=form_data)

       
        dashboard_url = reverse('dashboard')
        self.assertRedirects(response, dashboard_url)

        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Warning: This request was submitted late and may not be prioritized." in str(message) for message in messages))

      
        lesson_request = LessonRequest.objects.filter(student=self.student).first()
        self.assertIsNotNone(lesson_request)
        self.assertTrue(lesson_request.is_late)


    def test_invalid_lesson_request(self):
        form_data = {  # Missing required fields
            'term': '',
            'course': '',
            'preferred_time': '',
            'frequency': '',
        }
        response = self.client.post(self.url, data=form_data)

        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests.html')

       
        self.assertContains(response, 'This field is required.', count=4)

    def test_non_student_submission(self):
        other_user = User.objects.create_user(
            username='not_student',
            email='not_student@example.com',
            password='password123'
        )
        self.client.force_login(other_user)

        form_data = {
            'term': self.term.id,
            'course': self.course.id,
            'preferred_time': '09:00:00',
            'frequency': 'weekly',
        }
        response = self.client.post(self.url, data=form_data)

        
        dashboard_url = reverse('dashboard')
        self.assertRedirects(response, dashboard_url)

        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You must be a registered student" in str(message) for message in messages))

class StudentLessonRequestsViewTestCase(TestCase):
    def setUp(self):
        # Create user and student
        self.user = User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.user, learning_level='beginner')
        self.client.force_login(self.user)

        # Set up term and course
        self.term = Term.objects.create(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1),
        )
        self.course = Course.objects.create(
            name="Python Basics",
            level="Beginner",
            price_per_hour=50.00,
        )

        
        for i in range(3):
            LessonRequest.objects.create(
                student=self.student,
                course=self.course,
                term=self.term,
                status='pending',
                requested_date=date(2024, 1, i + 1),
            )

        self.url = reverse('student_lesson_requests')

    def test_view_as_non_student(self):
        # Log in as a non-student user
        other_user = User.objects.create_user(
            username='not_student',
            email='not_student@example.com',
            password='password123'
        )
        self.client.force_login(other_user)

        response = self.client.get(self.url, follow=True)
        dashboard_url = reverse('dashboard')

        
        self.assertRedirects(response, dashboard_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You must be a student to view this page." in str(message) for message in messages))

    def test_sort_by_valid_field(self):
        response = self.client.get(self.url, {'sort': 'term'})
        self.assertEqual(response.status_code, 200)
        lesson_requests = response.context['lesson_requests']
        self.assertEqual(lesson_requests[0].term, self.term) 

    def test_sort_by_invalid_field(self):
        response = self.client.get(self.url, {'sort': 'invalid_field'})
        self.assertEqual(response.status_code, 200)
        lesson_requests = response.context['lesson_requests']
        self.assertEqual(lesson_requests.count(), 3)  

    def test_view_with_default_sorting(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        lesson_requests = response.context['lesson_requests']
        self.assertEqual(lesson_requests.count(), 3)  


class ManageLessonRequestsViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.com',
            password='Password123'
        )
        self.admin = Admin.objects.create(user=self.user)

        self.student_user = User.objects.create_user(
            username='@charlie',
            email='charlie@example.com',
            password='Password123'
        )
        self.student = Student.objects.create(user=self.student_user)

        self.term = Term.objects.create(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1)
        )
        self.course = Course.objects.create(
            name='Math 101',
            level='beginner',
            price_per_hour=20.0
        )

        frequency_choice = TutorSession.FREQUENCY_CHOICES[0][0]  
        duration_choice = TutorSession.DURATION_CHOICES[0][0]  
        for i in range(15):
            LessonRequest.objects.create(
                student=self.student,
                course=self.course,
                frequency=frequency_choice,
                duration_minutes=duration_choice,
                term=self.term,
                status='pending'
            )

        self.url = reverse('manage_lesson_requests')

    def test_manage_lesson_requests_url(self):
        self.assertEqual(self.url, '/manage-lesson-requests/')

    def test_get_manage_lesson_requests_as_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_lesson_requests.html')
        page_obj = response.context['page_obj']
        self.assertTrue(hasattr(page_obj, 'object_list'))
        self.assertEqual(len(page_obj.object_list), 10)  # Pagination check

    def test_get_manage_lesson_requests_with_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 10)  

    def test_get_manage_lesson_requests_as_non_admin(self):
        other_user = User.objects.create_user(username='@notadmin', password='Password123')
        self.client.force_login(other_user)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You must be an admin to access this page.')

    def test_get_manage_lesson_requests_not_logged_in(self):
        expected_redirect_url = f'/log_in/?next={self.url}'
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, expected_redirect_url)


# class AllocatedLessonsViewTestCase(TestCase):
#     def setUp(self):
#         self.admin_user = User.objects.create_user(username='admin2', password='password123')
#         self.non_admin_user = User.objects.create_user(username='nonadmin', password='password123')
#         Admin.objects.create(user=self.admin_user)

#         
#         self.allocated_session = TutorSession.objects.create(is_booked=True)
#         self.unallocated_session = TutorSession.objects.create(is_booked=False)

#         self.allocated_lesson = Lesson.objects.create(session=self.allocated_session)
#         self.unallocated_lesson = Lesson.objects.create(session=self.unallocated_session)

#         self.url = reverse('allocated_lessons')        
#     def test_allocated_lessons_admin_access(self):
#         # Create an admin user
#         admin_user = User.objects.create_user(username='admin', password='password123')
#         Admin.objects.create(user=admin_user)
#         self.client.force_login(admin_user)

#         
#         lesson = Lesson.objects.create(session=TutorSession.objects.create(is_booked=True))
#         unallocated_lesson = Lesson.objects.create(session=TutorSession.objects.create(is_booked=False))

#         response = self.client.get(reverse('allocated_lessons'))

#         
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'allocated_lessons.html')

#       
#         lessons = response.context['lessons']
#         self.assertIn(lesson, lessons)
#         self.assertNotIn(unallocated_lesson, lessons)

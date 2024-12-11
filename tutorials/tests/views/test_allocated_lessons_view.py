from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import User, TutorSession, Admin,Lesson,Term,Tutor
from django.utils.timezone import now
from datetime import timedelta, date


class AllocatedLessonsViewTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password123', email='admin@admin.com')
        self.non_admin_user = User.objects.create_user(username='nonadmin', password='password123', email='nonadmin@nonadmin.com')
        Admin.objects.create(user=self.admin_user)

        
        #self.allocated_session = TutorSession.objects.create(is_booked=True)
        #self.unallocated_session = TutorSession.objects.create(is_booked=False)

        # Create a TutorSession
        self.tutor = Tutor.objects.create(user=self.admin_user)
        self.term = Term.objects.create(
            name="autumn",
            start_date=now().date() + timedelta(days=14),
            end_date=now().date() + timedelta(days=100)
        )
        self.allocated_session = TutorSession.objects.create(
            tutor=self.tutor,
            #course=self.course,
            term=self.term,
            time='09:30',
            start_day=0,
            duration_minutes=60,
            frequency='weekly',
            is_booked=True
        )
        
        self.unallocated_session = TutorSession.objects.create(
            tutor=self.tutor,
            #course=self.course,
            term=self.term,
            time='09:30',
            start_day=0,
            duration_minutes=60,
            frequency='weekly',
            is_booked=False
        )
        


        self.allocated_lesson = Lesson.objects.create(session=self.allocated_session)
        self.unallocated_lesson = Lesson.objects.create(session=self.unallocated_session)

        self.url = reverse('allocated_lessons')   
             
    def test_allocated_lessons_admin_access(self):
        # Create an admin user
        admin_user = User.objects.create_user(username='admin', password='password123',email='admin@admin.com')
        Admin.objects.create(user=admin_user)
        self.client.force_login(admin_user)

        
        lesson = Lesson.objects.create(session=TutorSession.objects.create(is_booked=True))
        unallocated_lesson = Lesson.objects.create(session=TutorSession.objects.create(is_booked=False))

        response = self.client.get(reverse('allocated_lessons'))

        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'allocated_lessons.html')

      
        lessons = response.context['lessons']
        self.assertIn(lesson, lessons)
        self.assertNotIn(unallocated_lesson, lessons)
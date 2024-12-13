from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Admin, Student, Tutor, Lesson, Course, Term, LessonRequest, TutorSession, CancellationRequest
import datetime
User = get_user_model()

class ManageCancellationRequestsViewTestCase(TestCase):
    def setUp(self):
         # Create an admin user
        self.admin_user = User.objects.create_user(username="adminuser", password="password123", email="admin@example.com")
        self.admin = Admin.objects.create(user=self.admin_user)

        # Create a student and tutor
        self.student_user = User.objects.create_user(username="studentuser", password="password123", email="student@example.com")
        self.student = Student.objects.create(user=self.student_user, learning_level="beginner")

        self.tutor_user = User.objects.create_user(username="tutoruser", password="password123", email="tutor@example.com")
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create a term, course, and lesson
        self.term = Term.objects.create(
            name="spring", 
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 6, 1)
        )
        self.course = Course.objects.create(
            name="Python Basics",
            description="Intro to Python",
            level="beginner",
            price_per_hour=20,
        )

        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            time="10:00:00",
            term=self.term,
            start_day=0,
            duration_minutes=60,
            frequency="weekly",
            is_booked=False
        )

        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            course=self.course,
            frequency="weekly",
            duration_minutes=60,
            term=self.term,
            status="pending"
        )

        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            course=self.course,
            session=self.tutor_session,
            term=self.term,
            request=self.lesson_request,
        )

        # Create cancellation requests
        self.cancellation_request1 = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Need to cancel due to personal reasons.",
            status="pending",
        )

        self.cancellation_request2 = CancellationRequest.objects.create(
            user=self.student_user,
            lesson=self.lesson,
            reason="Another cancellation reason.",
            status="pending",
        )

        self.manage_url = reverse("manage_cancellation_requests")

    def test_admin_access(self):
        """Test if an admin can access the view."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancellation Requests")

    # def test_non_admin_access(self):
    #     """Test if non-admin users are redirected with an error."""
    #     self.client.login(username="studentuser", password="password123")
    #     response = self.client.get(self.manage_url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse("home"))
    #     self.assertIn("You must be an admin to access this page.", [m.message for m in response.wsgi_request._messages])

    def test_sorting_requests(self):
        """Test if sorting by request_date works."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.get(f"{self.manage_url}?sort=request_date")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["page_obj"].object_list),
            list(CancellationRequest.objects.order_by("request_date"))
        )

    def test_post_approve_request(self):
        """Test approving a cancellation request."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.post(self.manage_url, {
            "action": "accept",
            "request_id": self.cancellation_request1.id,
        })
        self.assertRedirects(response, self.manage_url)

        self.cancellation_request1.refresh_from_db()
        self.lesson.refresh_from_db()
        self.assertEqual(self.cancellation_request1.status, "approved")
        self.assertFalse(self.lesson.rollover)
        

    def test_post_reject_request(self):
        """Test rejecting a cancellation request."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.post(self.manage_url, {
            "action": "reject",
            "request_id": self.cancellation_request2.id,
        })
        self.assertRedirects(response, self.manage_url)

        self.cancellation_request2.refresh_from_db()
        self.assertEqual(self.cancellation_request2.status, "rejected")
        

    def test_invalid_action(self):
        """Test submitting an invalid action."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.post(self.manage_url, {
            "action": "invalid_action",
            "request_id": self.cancellation_request1.id,
        })
        self.assertRedirects(response, self.manage_url)
        self.cancellation_request1.refresh_from_db()
        self.assertEqual(self.cancellation_request1.status, "pending")  

    def test_pagination(self):
        """Test if pagination works correctly."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.get(f"{self.manage_url}?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"].object_list), 2) 

    def test_post_missing_action_or_request_id(self):
        """Test if missing action or request ID in POST redirects with an error."""
        self.client.login(username="adminuser", password="password123")
        response = self.client.post(self.manage_url, {"action": ""})
        self.assertRedirects(response, self.manage_url)
        self.assertIn("Invalid action or request ID.", [m.message for m in response.wsgi_request._messages])

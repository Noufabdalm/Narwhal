from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import Student, LessonRequest, TutorSession, Term, Course, Lesson, Invoice, User,Tutor,Expertise
from datetime import date

class LessonBookingViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username="teststudent",
            email="teststudent@example.com",
            password="password123",
            first_name="Test",
            last_name="Student",
        )
        cls.user = User.objects.create_user(
            username="testTutor",
            email="testTutor@example.com",
            password="password123",
            first_name="Test",
            last_name="Tutor",
        )

        #Create Student
        cls.student = Student.objects.create(user=cls.user, learning_level="beginner")

        #Create tutor
        cls.tutor = Tutor.objects.create(user=cls.user)

        #Create Expertise and add it to tutor's expertise
        cls.expertise = Expertise.objects.create(name='python')
        cls.tutor.expertise.add(cls.expertise)

        # Create term
        cls.term = Term.objects.create(
            name="spring",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
        )

        # Create course
        cls.course = Course.objects.create(
            name="Python Beginner",
            description="Introductory Python Course",
            level="beginner",
            price_per_hour=20,
        )

        # Create lesson request
        cls.lesson_request = LessonRequest.objects.create(
            student=cls.student,
            course=cls.course,
            frequency="weekly",
            duration_minutes=60,
            term=cls.term,
            status="pending",
        )

        # Create tutor session
        cls.tutor_session = TutorSession.objects.create(
            tutor=cls.tutor,  
            time="10:00:00",
            term=cls.term,
            start_day=0,
            start_date=date(2025, 1, 10),
            end_date=date(2025, 6, 1),
            duration_minutes=60,
            frequency="weekly",
            is_booked=False,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="teststudent", password="password123")
    
    # Test Step 1: Select Student View
    def test_select_student_view(self):
        response = self.client.get(reverse("select_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "select_student.html")
    
    def test_select_student_form_submission(self):
        response = self.client.post(reverse("select_student"), data={"student": self.student.id})
        self.assertRedirects(response, reverse("select_request"))
    
    # Test Step 2: Select Request View
    def test_select_request_view(self):
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()
        response = self.client.get(reverse("select_request"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "select_request.html")

    def test_select_request_form_submission(self):
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()
        response = self.client.post(reverse("select_request"), data={"request": self.lesson_request.id})
        self.assertRedirects(response, reverse("select_session"))

    # Test Step 3: Select Session View
    def test_select_session_view(self):
        session = self.client.session
        session["request_id"] = self.lesson_request.id
        session.save()
        response = self.client.get(reverse("select_session"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "select_session.html")

    def test_select_session_form_submission(self):
        session = self.client.session
        session["request_id"] = self.lesson_request.id
        session.save()

        response = self.client.post(reverse("select_session"), data={"session": self.tutor_session.id})
        self.assertRedirects(response, reverse("confirm_booking"))

    # Test Step 4a: Confirm Booking View
    def test_confirm_booking_view(self):
        session = self.client.session
        session["student_id"] = self.student.id
        session["request_id"] = self.lesson_request.id
        session["session_id"] = self.tutor_session.id
        session.save()

        response = self.client.get(reverse("confirm_booking"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm_booking.html")
    
    def test_confirm_booking_form_submission(self):
        session = self.client.session
        session["student_id"] = self.student.id
        session["request_id"] = self.lesson_request.id
        session["session_id"] = self.tutor_session.id
        session.save()

        response = self.client.post(reverse("confirm_booking"))
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(Lesson.objects.filter(student=self.student, session=self.tutor_session).exists())
        self.assertTrue(Invoice.objects.filter(student=self.student, lesson__session=self.tutor_session).exists())

    # Test Step 4b: Reject or Book Later View
    def test_reject_or_book_later_view(self):
        session = self.client.session
        session["request_id"] = self.lesson_request.id
        session.save()

        response = self.client.get(reverse("reject_or_book_later"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reject_or_book_later.html")

    def test_reject_request(self):
        session = self.client.session
        session["request_id"] = self.lesson_request.id
        session.save()

        response = self.client.post(reverse("reject_or_book_later"), data={"reject_request": True, "rejection_reason": "No available sessions"})
        self.assertRedirects(response, reverse("dashboard"))
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, "rejected")

    def test_book_later(self):
        session = self.client.session
        session["request_id"] = self.lesson_request.id
        session.save()

        response = self.client.post(reverse("reject_or_book_later"), data={"book_later": True})
        self.assertRedirects(response, reverse("dashboard"))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "The request has been marked for booking later.")



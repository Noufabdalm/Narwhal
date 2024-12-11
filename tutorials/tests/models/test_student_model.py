from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Student, Course, Lesson, LessonRequest, Term, Tutor, TutorSession
from datetime import date

User = get_user_model()

class StudentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = User.objects.create_user(
            username="teststudent",
            email="teststudent@example.com",
            password="password123",
            first_name="Test",
            last_name="Student",
        )
        
        # Create a test student
        cls.student = Student.objects.create(
            user=cls.user,
            learning_level="beginner"
        )
        
        # Create a test term
        cls.term = Term.objects.create(
            name="spring",
            start_date=date(2025,1,1),
            end_date=date(2025,6,1),
        )
        
        # Create a test course
        cls.course = Course.objects.create(
            name="Python Beginner",
            description="Introductory Python Course",
            level="beginner",
            price_per_hour=20,
        )
        
        # Create a test tutor
        cls.tutor_user = User.objects.create_user(
            username="testtutor",
            email="testtutor@example.com",
            password="password123",
            first_name="Test",
            last_name="Tutor",
        )
        cls.tutor = Tutor.objects.create(user=cls.tutor_user)
        
        # Create a test tutor session
        cls.tutor_session = TutorSession.objects.create(
            tutor=cls.tutor,
            time="10:00:00",
            term=cls.term,
            start_day=0,  # Monday
            start_date=date(2025,1,6),
            end_date=date(2025,6,1),
            duration_minutes=60,
            frequency="weekly",
        )
        
        
        # Create an allocated lesson request
        cls.lesson_request = LessonRequest.objects.create(
            student=cls.student,
            course=cls.course,
            frequency="weekly",
            duration_minutes=60,
            term=cls.term,
            status="pending",
        )

        # Create a pending lesson request
        cls.lesson_request2 = LessonRequest.objects.create(
            student=cls.student,
            course=cls.course,
            frequency="fortnightly",
            duration_minutes=60,
            term=cls.term,
            status="pending",
        )

         # Create a test lesson
        cls.lesson = Lesson.objects.create(
            student=cls.student,
            tutor=cls.tutor,
            course=cls.course,
            start_day=0,
            start_date=date(2025,1,6),
            end_date=date(2025,6,1),
            session=cls.tutor_session,
            term=cls.term,
            request = cls.lesson_request
        )

    def test_student_creation(self):
        """Test the creation of a student."""
        self.assertEqual(self.student.user.username, "teststudent")
        self.assertEqual(self.student.learning_level, "beginner")
        self.assertEqual(str(self.student), "Student: Test Student")

    def test_enrolled_courses(self):
        """Test the enrolled_courses method."""
        courses = self.student.enrolled_courses()
        self.assertIn(self.course, courses)

    def test_assigned_tutors_and_sessions(self):
        """Test the assigned_tutors_and_sessions method."""
        assigned = self.student.assigned_tutors_and_sessions()
        self.assertEqual(len(assigned), 1)
        self.assertEqual(assigned[0][0], self.tutor_session)
        self.assertEqual(assigned[0][1], self.tutor)

    def test_pending_requests(self):
        """Test the pending_requests method."""
        pending_requests = self.student.pending_requests()
        self.assertEqual(len(pending_requests), 1) 
        self.assertEqual(pending_requests[0].status, "pending")
        


  
from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student, Expertise, Course, Term, Lesson, LessonRequest, CancellationRequest, TutorSession,Invoice
from datetime import date
from decimal import Decimal
from faker import Faker
from random import randint, choice, sample

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

expertises = [
    "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Swift", "Kotlin", "Go", "Rust", "Ruby", "TypeScript", "SQL",
    "React", "Vue.js", "Angular", "Next.js",
    "Django", "Node.js", "Express.js",
    "React Native", "Flutter"
]

class Command(BaseCommand):
    USER_COUNT = 30
    TUTOR_COUNT = 15
    STUDENT_COUNT = 15
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'
    MAX_SESSIONS_PER_TUTOR = 10
    MAX_REQUESTS_PER_STUDENT = 5
    MAX_ALLOCATED_LESSONS = 3

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_expertise()
        self.create_tutors()
        self.create_students()
        self.create_courses()
        self.create_terms()
        self.create_sessions()
        self.create_lesson_requests()
        self.create_lessons()
        self.create_invoices()
        self.create_cancellation_requests()

    def create_users(self):
        print("Seeding users...")
        # Check if user fixtures already exist
        for data in user_fixtures:
            if not User.objects.filter(username=data['username']).exists():
                self.try_create_user(data)
            else:
                print(f"User fixture {data['username']} already exists. Skipping.")

        self.generate_random_users()
        print("User seeding complete.")

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Error creating user: {e}")

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=self.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_expertise(self):
        print("Seeding expertise...")
        if Expertise.objects.count() == 0:
            for name in expertises:
                Expertise.objects.create(name=name.lower())
        print("Expertise seeding complete.")

    def create_tutors(self):
        print("Seeding tutors...")
        expertise_list = list(Expertise.objects.all())  # Retrieve all expertise from the database
        tutors_created = Tutor.objects.count()
        while tutors_created < self.TUTOR_COUNT:
            user = self.get_unassigned_user()
            if user:
                tutor = Tutor.objects.create(user=user)
                random_skills = self.random_expertise(expertise_list)
                tutor.expertise.add(*random_skills)
                tutors_created += 1
        print("Tutor seeding complete.")

    def create_students(self):
        print("Seeding students...")
        levels = ['beginner', 'intermediate', 'advanced']
        students_created = Student.objects.count()
        while students_created < self.STUDENT_COUNT:
            user = self.get_unassigned_user()
            if user:
                Student.objects.create(user=user, learning_level=choice(levels))
                students_created += 1
        print("Student seeding complete.")

    def create_courses(self):
        print("Seeding courses...")
        LEVELS = {
            'beginner': 20,
            'intermediate': 40,
            'advanced': 60,
        }
        expertise_list = Expertise.objects.all()
        for expertise in expertise_list:
            for level, price in LEVELS.items():
                Course.objects.create(
                    name=f"{expertise.name.capitalize()} {level.capitalize()} Course",
                    description=f"This is a {level} course for {expertise.name.capitalize()}",
                    level=level,
                    price_per_hour=price,
                    ProgrammingLanguage=expertise
                )
        print("Courses seeding complete.")

    def create_terms(self):
        print("Seeding terms...")
        TERM_CHOICES = [
            ('autumn', date(2025, 9, 1), date(2025, 12, 31)),
            ('spring', date(2026, 1, 1), date(2026, 4, 15)),
            ('summer', date(2026, 5, 1), date(2026, 7, 31)),
        ]

        for name, start_date, end_date in TERM_CHOICES:
            if not Term.objects.filter(name=name).exists():
                Term.objects.create(name=name, start_date=start_date, end_date=end_date)
                print(f"Term '{name}' created.")
            else:
                print(f"Term '{name}' already exists.")
        print("Term seeding complete.")

    def random_expertise(self, expertise_list):
        # Choose a random number of skills between 1 and 10
        NumberOfSkills = randint(1, 10)
        return sample(expertise_list, k=NumberOfSkills)  # Sample this number from the full list of expertise
    def create_sessions(self):
        print("Seeding tutor sessions...")
        terms = Term.objects.all()
        tutors = Tutor.objects.all()
        for tutor in tutors:
            for term in terms:
                session_count = randint(1, self.MAX_SESSIONS_PER_TUTOR)
                for _ in range(session_count):
                    TutorSession.objects.create(
                        tutor=tutor,
                        time=self.faker.time(),
                        term=term,
                        start_day=randint(0, 4),  # Monday to Friday
                        duration_minutes=choice([60, 120]),
                        frequency=choice(['weekly', 'fortnightly']),
                        is_booked=False,
                    )
        print("Tutor sessions seeding complete.")

    def create_lesson_requests(self):
        print("Seeding lesson requests...")
        students = Student.objects.all()
        courses = Course.objects.all()
        terms = Term.objects.all()
        for student in students:
            request_count = randint(1, self.MAX_REQUESTS_PER_STUDENT)
            for _ in range(request_count):
                LessonRequest.objects.create(
                    student=student,
                    course=choice(courses),
                    frequency=choice(['weekly', 'fortnightly']),
                    duration_minutes=choice([60, 120]),
                    term=choice(terms),
                    status='pending'
                )
        print("Lesson requests seeding complete.")

    def create_lessons(self):
        print("Seeding lessons...")
        lesson_requests = LessonRequest.objects.all()
        for request in lesson_requests:
            if randint(0, 1):  # Randomly allocate lessons
                session = TutorSession.objects.filter(
                    tutor__expertise=request.course.ProgrammingLanguage,
                    term=request.term,
                    is_booked=False
                ).first()
                if session:
                    Lesson.objects.create(
                        student=request.student,
                        tutor=session.tutor,
                        course=request.course,
                        session=session,
                        term=request.term,
                        request=request,
                        status='active',
                    )
                    session.is_booked = True
                    session.save()
        print("Lessons seeding complete.")

    def create_invoices(self):
        print("Seeding invoices...")
        lessons = Lesson.objects.all()
        for lesson in lessons:
            Invoice.objects.create(
                student=lesson.student,
                lesson=lesson,
                total_amount=Decimal(lesson.session.calculate_term_cost(lesson.course)),
                due_date=lesson.session.start_date,
                status='unpaid'
            )
        print("Invoices seeding complete.")

    def create_cancellation_requests(self):
        print("Seeding cancellation requests...")
        lessons = Lesson.objects.all()
        for lesson in lessons:
            if randint(0, 1):  # Randomly create cancellation requests
                CancellationRequest.objects.create(
                    user=lesson.student.user,
                    lesson=lesson,
                    reason=self.faker.text(max_nb_chars=200),
                    status='pending'
                )
        print("Cancellation requests seeding complete.")

    def get_unassigned_user(self):
        user = User.objects.filter(
            student_profile=None,
            tutor_profile=None,
        ).first()
        return user

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

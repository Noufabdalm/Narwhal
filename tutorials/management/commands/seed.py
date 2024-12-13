from django.core.management.base import BaseCommand
from tutorials.models import User,Admin, Tutor, Student, Expertise, Course, Term, Lesson, LessonRequest, CancellationRequest, TutorSession,Invoice
from datetime import date, timedelta
import datetime
from decimal import Decimal
from faker import Faker
from random import randint, choice, sample
from django.core.exceptions import ValidationError

#Comment to push 
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
LEVELS = {
            'beginner': 20,
            'intermediate': 40,
            'advanced': 60,
        }

class Command(BaseCommand):
    USER_COUNT = 300
    ADMIN_COUNT = 20
    TUTOR_COUNT = 140
    STUDENT_COUNT = 140
    MAX_COURSES = len(expertises)*len(LEVELS)
    MAX_REQUESTS_PER_STUDENT = 10
    MAX_SESSIONS_PER_TUTOR = 15
    MAX_LESSON_REQUESTS = 100
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'
   

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_expertise()
        self.create_terms()
        self.create_courses()
        self.create_users()
        self.users = User.objects.all()
        self.assign_roles_to_fixtures()
        self.create_tutors()
        self.create_students()
        self.create_admins()
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
        expertise_list = list(Expertise.objects.all()) 
        tutors_created = Tutor.objects.count()
        while tutors_created < self.TUTOR_COUNT:
            user = self.get_unassigned_user()
            if user:
                tutor = Tutor.objects.create(user=user)
                random_skills = self.random_expertise(expertise_list)
                tutor.expertise.add(*random_skills)
                tutors_created += 1
        print("Tutor seeding complete.")

    def create_admins(self):
        print("Seeding admins...")
        admins_created = Admin.objects.count()
        while admins_created < self.ADMIN_COUNT:
            user = self.get_unassigned_user()
            if user:
                Admin.objects.create(user=user)
                admins_created += 1
        print("Admin seeding complete.")

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
        expertise_list = Expertise.objects.all()
        if Course.objects.count()< self.MAX_COURSES:
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

    def create_sessions(self):
        print("Seeding tutor sessions...")
        terms = Term.objects.all()
        tutors = Tutor.objects.all()
        time_choices = [
            datetime.time(hour, minute)
            for hour in range(9, 18)  # 9 AM to 6 PM
            for minute in (0, 30)  # Half-hour intervals
        ]

        for tutor in tutors:
            if TutorSession.objects.filter(tutor=tutor).count()<self.MAX_SESSIONS_PER_TUTOR:
                for term in terms:
                    session_count = randint(1, self.MAX_SESSIONS_PER_TUTOR)
                    created_sessions = 0

                    while created_sessions < session_count:
                        start_time = choice(time_choices)
                        start_day = randint(0, 4)  # Monday to Friday
                        duration = choice([60, 120])  # 1 hour or 2 hours
                        frequency = choice(['weekly', 'fortnightly'])

                        try:
                            # Create session if no overlaps found
                            TutorSession.objects.create(
                                tutor=tutor,
                                time=start_time,
                                term=term,
                                start_day=start_day,
                                duration_minutes=duration,
                                frequency=frequency,
                                is_booked=False
                            )
                            created_sessions += 1
                        except (ValueError, ValidationError):
                            continue

        print("Tutor sessions seeding complete.")


    def create_lesson_requests(self):
        print("Seeding lesson requests...")
        students = Student.objects.all()
        courses = Course.objects.all()
        terms = Term.objects.all()
        if LessonRequest.objects.count()< self.MAX_LESSON_REQUESTS:
            for student in students:
                if LessonRequest.objects.filter(student=student).exists()<self.MAX_REQUESTS_PER_STUDENT:
                    request_count = randint(1, self.MAX_REQUESTS_PER_STUDENT)
                    for _ in range(request_count):
                        requests=LessonRequest.objects.filter(
                            student=student,
                            course=choice(courses),
                            frequency=choice(['weekly', 'fortnightly']),
                            duration_minutes=choice([60, 120]),
                            term=choice(terms)
                        )
                        if not requests.exists():
                            LessonRequest.objects.create(
                            student=student,
                            course=choice(courses),
                            frequency=choice(['weekly', 'fortnightly']),
                            duration_minutes=choice([60, 120]),
                            term=choice(terms),
                            status = 'pending'
                            )
        print("Lesson requests seeding complete.")

    def create_lessons(self):
        print("Seeding lessons...")
        lesson_requests = LessonRequest.objects.all()
        for request in lesson_requests:
            if randint(0, 1): 
                session = TutorSession.objects.filter(
                    tutor__expertise=request.course.ProgrammingLanguage,
                    term=request.term,
                    is_booked=False
                ).first()

                if session:
                    
                    lesson, created = Lesson.objects.get_or_create(
                        student=request.student,
                        tutor=session.tutor,
                        course=request.course,
                        session=session,
                        term=request.term,
                        request=request,
                    )
                    if created:
                        session.is_booked = True
                        session.save()

                        request.status = 'allocated'
                        request.save()
        print("Lessons seeding complete.")



    def create_invoices(self):
        print("Seeding invoices...")
        lessons = Lesson.objects.all()
        for lesson in lessons:
            if not Invoice.objects.filter(lesson=lesson).exists():
                Invoice.objects.get_or_create(
                    lesson=lesson,
                    defaults={
                        'student': lesson.student,
                        'total_amount': Decimal(lesson.session.calculate_term_cost(lesson.course)),
                        'due_date': lesson.session.start_date,
                        'status': choice(['paid', 'unpaid']),
                    }
                )
        print("Invoices seeding complete.")

    def create_cancellation_requests(self):
        print("Seeding cancellation requests...")
        lessons = Lesson.objects.filter(rollover =True)
        for lesson in lessons:
            if randint(0, 1): 
                submitter = choice([lesson.student.user, lesson.tutor.user])
                CancellationRequest.objects.get_or_create(
                    lesson=lesson,
                    defaults={
                        'user': submitter,
                        'reason': self.faker.text(max_nb_chars=200),
                        'status': 'pending'
                    }
                )
        print("Cancellation requests seeding complete.")

    def assign_roles_to_fixtures(self):
        """Assign specific roles to user fixtures and establish relationships."""
        for fixture in user_fixtures:
            user = User.objects.filter(username=fixture['username']).first()
            if user:
                # Assign roles based on username
                if fixture['username'] == '@johndoe':
                    if not Admin.objects.filter(user=user).exists():
                        Admin.objects.create(user=user)
                    print(f"Assigned admin role to John doe")
                
                elif fixture['username'] == '@janedoe':
                    if not Tutor.objects.filter(user=user).exists():
                        expertise_list = list(Expertise.objects.all()) 
                        tutor = Tutor.objects.create(user=user)
                        # Assign expertise 
                        random_skills = self.random_expertise(expertise_list)
                        tutor.expertise.add(*random_skills)

                    print("Assigned tutor role to jane doe with expertise")
                
                elif fixture['username'] == '@charlie':
                    if not Student.objects.filter(user=user).exists():
                        student = Student.objects.create(user=user, learning_level='beginner')
                        print("Assigned student role to Charlie Johnson")

                       
                        tutor = Tutor.objects.filter(user__username='@janedoe').first()
                        if tutor:
                             # Establish relationship between @charlie and @janedoe# Create a lesson request for @charlie with @janedoe
                            course = Course.objects.filter(ProgrammingLanguage__in=tutor.expertise.all()).first()
                            if course:
                                term = Term.objects.first()  
                                lesson_request = LessonRequest.objects.create(
                                    student=student,
                                    course=course,
                                    frequency='weekly',
                                    duration_minutes=60,
                                    term=term,
                                    status='pending'
                                )
                                session = TutorSession.objects.filter(
                                    tutor=tutor,
                                    term=term,
                                    is_booked=False
                                ).first()
                                if session:
                                    Lesson.objects.create(
                                        student=student,
                                        tutor=tutor,
                                        course=course,
                                        session=session,
                                        term=term,
                                        request=lesson_request,
                                        rollover=True
                                    )
                                    session.is_booked = True
                                    session.save()
                                    lesson_request.status = 'allocated'
                                    lesson_request.save()
                                    print(f"Created lesson for {student.user.username} with tutor {tutor.user.username}")


    ## HELPER METHODS TO SEED ##
    def random_expertise(self, expertise_list):
        NumberOfSkills = randint(1, 10)
        return sample(expertise_list, k=NumberOfSkills)  

    def get_unassigned_user(self):
        user = User.objects.filter(
            student_profile=None,
            tutor_profile=None,
            admin_profile = None
        ).first()
        return user
    
    def calculate_start_date(self, term, start_day):
        """Calculate the first occurrence of the desired weekday in the term."""
        delta_days = (start_day - term.start_date.weekday()) % 7
        start_date = term.start_date + timedelta(days=delta_days)
        return start_date

    def calculate_end_date(self, start_date, term, frequency):
        """Calculate the end date based on the recurrence."""
        session_interval = 7 if frequency == 'weekly' else 14
        current_date = start_date

        while current_date + timedelta(days=session_interval) <= term.end_date:
            current_date += timedelta(days=session_interval)

        return current_date

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

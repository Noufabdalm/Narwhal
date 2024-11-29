from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student, Expertise, Course
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
    TUTOR_COUNT = 10
    STUDENT_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_expertise()
        self.create_tutors()
        self.create_students()
        self.create_courses()

    def create_users(self):
        if User.objects.count ==0:
            self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        fixturesGenerated = True
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.")

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
                    duration_minutes=choice([60, 120]),
                    frequency=choice(['weekly', 'fortnightly']),
                    ProgrammingLanguage=expertise
                )
        print("Courses seeding complete.")


    def random_expertise(self, expertise_list):
        # Choose a random number of skills between 1 and 10
        NumberOfSkills = randint(1, 10)
        return sample(expertise_list, k=NumberOfSkills)  # Sample this number from the full list of expertise

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

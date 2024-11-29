from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Tutor, Student, Expertise, TutorSession

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write("Starting to unseed the database...")

        # Delete Tutor records
        tutor_count = Tutor.objects.count()
        Tutor.objects.all().delete()
        self.stdout.write(f"Deleted {tutor_count} tutor records.")

        # Delete Student records
        student_count = Student.objects.count()
        Student.objects.all().delete()
        self.stdout.write(f"Deleted {student_count} student records.")

        # Delete Expertise records
        expertise_count = Expertise.objects.count()
        Expertise.objects.all().delete()
        self.stdout.write(f"Deleted {expertise_count} expertise records.")

         # Delete Expertise records
        TutorSession_count = TutorSession.objects.count()
        TutorSession.objects.all().delete()
        self.stdout.write(f"Deleted {TutorSession_count} expertise records.")

        # Delete non-staff users
        user_count = User.objects.filter(is_staff=False).count()
        User.objects.filter(is_staff=False).delete()
        self.stdout.write(f"Deleted {user_count} non-staff user records.")

        self.stdout.write("Database unseeding complete.")
        
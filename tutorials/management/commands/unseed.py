from django.core.management.base import BaseCommand
from tutorials.models import (
    User, Tutor, Student, Expertise, TutorSession, Lesson, 
    LessonRequest, Course, Term, Invoice
)

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Unseeds the database by removing all seeded data'

    def handle(self, *args, **options):
        self.stdout.write("Starting to unseed the database...")

        # Delete Invoice records
        invoice_count = Invoice.objects.count()
        Invoice.objects.all().delete()
        self.stdout.write(f"Deleted {invoice_count} invoice records.")

        # Delete Lesson records
        lesson_count = Lesson.objects.count()
        Lesson.objects.all().delete()
        self.stdout.write(f"Deleted {lesson_count} lesson records.")

        # Delete LessonRequest records
        request_count = LessonRequest.objects.count()
        LessonRequest.objects.all().delete()
        self.stdout.write(f"Deleted {request_count} lesson request records.")

        # Delete TutorSession records
        tutor_session_count = TutorSession.objects.count()
        TutorSession.objects.all().delete()
        self.stdout.write(f"Deleted {tutor_session_count} tutor session records.")

        # Delete Course records
        course_count = Course.objects.count()
        Course.objects.all().delete()
        self.stdout.write(f"Deleted {course_count} course records.")

        # Delete Expertise records
        expertise_count = Expertise.objects.count()
        Expertise.objects.all().delete()
        self.stdout.write(f"Deleted {expertise_count} expertise records.")

        # Delete Tutor records
        tutor_count = Tutor.objects.count()
        Tutor.objects.all().delete()
        self.stdout.write(f"Deleted {tutor_count} tutor records.")

        # Delete Student records
        student_count = Student.objects.count()
        Student.objects.all().delete()
        self.stdout.write(f"Deleted {student_count} student records.")

        # Delete Term records
        term_count = Term.objects.count()
        Term.objects.all().delete()
        self.stdout.write(f"Deleted {term_count} term records.")

        # Delete non-staff User records
        user_count = User.objects.filter(is_staff=False).count()
        User.objects.filter(is_staff=False).delete()
        self.stdout.write(f"Deleted {user_count} non-staff user records.")

        self.stdout.write("Database unseeding complete.")

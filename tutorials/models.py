from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.utils.timezone import now
from datetime import time, timedelta
import datetime
from django.core.exceptions import ValidationError
from decimal import Decimal


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin: {self.user.full_name()}"


class Student(models.Model):
    LEARNING_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    learning_level = models.CharField(max_length=20, choices=LEARNING_LEVEL_CHOICES)

    def __str__(self):
        return f"Student: {self.user.full_name()}"

    def enrolled_courses(self):
        """Get all courses the student is enrolled in via lessons."""
        return Course.objects.filter(lessons__student=self)
        
    def assigned_tutors_and_sessions(self):
        lessons = Lesson.objects.filter(student=self).select_related('session', 'tutor')
        return [(lesson.session, lesson.tutor) for lesson in lessons]

    def pending_requests(self):
        return LessonRequest.objects.filter(status='pending')
    
    def upcoming_lessons(self):
        pass


class Expertise(models.Model):
    """Model to store expertise areas/programming languages."""
    name = models.CharField(max_length=50, unique=True)

    def clean(self):
        """Enforce case-insensitive uniqueness for the name."""
        if Expertise.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(f"Expertise '{self.name}' already exists.")

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.clean
        super().save(*args, **kwargs)

    def __str__(self):
        # Capitalize the first letter for display purposes
        return self.name.capitalize()

    def tutors_with_expertise(self):
     """Return all tutors who have this expertise."""
     pass


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutor_profile")
    expertise = models.ManyToManyField(Expertise, related_name='qualified_tutors')
    def __str__(self):
        return f"Tutor: {self.user.full_name()}"


class Course(models.Model):
    """Model for courses offered by Code Tutors."""
    LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    PRICE_CHOICES = [
    (20.0, "Beginner: £20/hour"),
    (40.0, "Intermediate: £40/hour"),
    (60.0, "Advanced: £60/hour"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVELS)
    price_per_hour = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        choices=PRICE_CHOICES
    )
    ProgrammingLanguage = models.ForeignKey('Expertise', on_delete=models.CASCADE, related_name='courses', null=True)
    
    def qualifiedTutors(self):
        return Tutor.objects.filter(
            Expertise = self.ProgrammingLanguage
        )
    
    def __str__(self):
        return f"{self.name} ({self.level})"


class Term(models.Model):
    TERM_CHOICES = [
        ('autumn', 'September-Christmas'),
        ('spring', 'January-Easter'),
        ('summer', 'May-July'),
    ]
    name = models.CharField(max_length=20, choices=TERM_CHOICES, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.get_name_display()


class TutorSession(models.Model):
    """Model for tracking tutor availability."""

    TIME_CHOICES = [
        (time(hour, minute), f"{hour:02d}:{minute:02d}")
        for hour in range(9, 19)  # 9 AM to 6 PM 
        for minute in (0, 30)  # Half-hour intervals
    ]

    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday")
    ]

    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('fortnightly', 'Every Two Weeks'),
    ]
    DURATION_CHOICES = [
        (60, "1 Hour"),
        (120, "2 Hours"),
    ]


    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name="Tutor_Sessions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="Course_Sessions")
    time = models.TimeField(choices=TIME_CHOICES)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='Term_Sessions')
    start_day = models.IntegerField(choices=WEEKDAY_CHOICES, default=0)
    start_date = models.DateField(null=True, blank=True) 
    end_date = models.DateField(null=True, blank=True) 
    duration_minutes = models.PositiveIntegerField(choices=DURATION_CHOICES, default=60)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default ='weekly')
    is_booked = models.BooleanField(default=False)

    def calculate_start_date(self):
        """Calculate the first occurrence of the desired weekday in the term (excluding weekends)."""
        term_start = self.term.start_date
        # Calculate the difference to the next weekday
        delta_days = (self.start_day - term_start.weekday()) % 7
        calculated_date = term_start +  timedelta(days=delta_days)

        if calculated_date > self.term.end_date:
            raise ValueError("The calculated start date is beyond the term's end date.")

        return calculated_date

    def calculate_end_date(self):
        if not self.start_date:
            raise ValueError("Start date must be defined to calculate the end date.")
        
        # Determine the session interval based on frequency
        if(self.frequency == 'weekly'):
            session_interval = 7  
        else:
            session_interval = 14

        # Start from the initial session date
        current_date = self.start_date

        # Iterate to find the last valid session date within the term
        while current_date + timedelta(days=session_interval) <= self.term.end_date:
            current_date += timedelta(days=session_interval)

        return current_date


    def calculate_term_cost(self):
        lessons_per_term = 12 if self.frequency == 'weekly' else 6
        # Convert all components to Decimal
        duration_in_hours = Decimal(self.duration_minutes) / Decimal(60)  # Convert minutes to hours as Decimal
        price_per_hour = Decimal(self.course.price_per_hour)  # Ensure course price per hour is a Decimal
        lessons = Decimal(lessons_per_term)  # Convert lessons_per_term to Decimal

        # Perform the calculation
        total_cost = duration_in_hours * price_per_hour * lessons
        return total_cost
    
    def clean(self):
        # Check for duplicate sessions
        if TutorSession.objects.filter(
            tutor=self.tutor,
            course=self.course,
            time=self.time,
            start_date=self.start_date,
            term=self.term,
        ).exclude(pk=self.pk).exists():
            raise ValidationError("A tutor session with these details already exists.")
    

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = self.calculate_start_date() 
        if self.start_date:
            self.end_date = self.calculate_end_date()
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.tutor.user.username} - {self.course.name} ({status})"


class LessonRequest(models.Model):
    """Model for managing student lesson requests."""
    STATUS_CHOICES=[
            ('pending', 'Pending'),
            ('allocated', 'Allocated'),
            ('rejected', 'Rejected'),
        ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lesson_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson_requests')
    frequency = models.CharField(max_length=20, choices=TutorSession.FREQUENCY_CHOICES)
    duration_minutes = models.PositiveIntegerField(choices=TutorSession.DURATION_CHOICES, default=60)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='lesson_requests')
    status = models.CharField(
        max_length=20,
        choices= STATUS_CHOICES,
        default='pending'
    )
    # Flag to determine if the request is late or not
    is_late = models.BooleanField(default=False)
    requested_date = models.DateField(default=datetime.date.today)
    


    def __str__(self):
        return f"Request by {self.student.user.username} for {self.course.name} ({self.term.name})"

    def check_and_mark_late(self):
        """
        Checks if the request is late based on the term start date and marks it as late if applicable.
        """
        days_until_term_starts = (self.term.start_date - now().date()).days
        if days_until_term_starts < 14:
            self.is_late = True
        

    def get_available_tutor_sessions(self):
        """
        Fetch all available tutor sessions matching the course, term, and frequency.
        """
        return TutorSession.objects.filter(
            course=self.course,
            term=self.term,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            is_booked=False
        )
    
    def save(self, *args, **kwargs):
        """
        Override the save method to check if the request is late before saving.
        """
        self.check_and_mark_late()
        super().save(*args, **kwargs)
    
    
        


class Lesson(models.Model):
    """Model for Booking lessons."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lessons')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='lessons')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    start_day = models.IntegerField(choices=TutorSession.WEEKDAY_CHOICES, default=0)
    start_date = models.DateField(null=True, blank=True) 
    end_date = models.DateField(null=True, blank=True) 
    session = models.ForeignKey(
        TutorSession,
        on_delete=models.CASCADE,
        related_name='lessons',
        limit_choices_to=models.Q(is_booked=False)
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='lessons')
    #Link lesson to a specific lesson request
    request = models.ForeignKey(
        LessonRequest,
        on_delete=models.CASCADE,
        related_name='allocated_lesson'
    )

    rollover = models.BooleanField(default=True) # Student is going to take the model next term unless a change or cancellation is requested

    def clean(self):
        super().clean()
        if self.course != self.session.course:
            raise ValidationError("The course of the lesson must match the course of the tutor session.")
        if self.course != self.request.course:
            raise ValidationError("The course of the lesson must match the course of the lesson request.")

    def __str__(self):
        return f"Lesson for {self.student.user.username} with {self.tutor.user.username}"

    def save(self, *args, **kwargs):
        """
        Ensure session gets marked as booked and the request status updated to 'allocated'.
        """
        self.clean()
        self.session.is_booked = True
        self.session.save()

        self.start_day = self.session.start_day
        self.start_date = self.session.start_date
        self.end_date = self.session.end_date

        if self.request:
            self.request.status = 'allocated'
            self.request.save()

        super().save(*args, **kwargs)


class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='invoice')
    total_amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null = True)
    due_date = models.DateField(blank=True, null = True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
        ],
        default='unpaid'
    )
  
    def __str__(self):
        return f"Invoice for {self.student.user.username} ({self.status})"
    
    def save(self, *args, **kwargs):
     """
     Ensure session gets marked as booked and the request status updated to 'allocated'.
     """
     super().save(*args, **kwargs)



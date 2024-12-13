from django.conf import settings
from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, StudentSelectionForm,RequestSelectionForm,SessionSelectionForm, CancellationRequestForm, TutorSignUpForm
from tutorials.helpers import login_prohibited
from .models import Lesson
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import Student, LessonRequest,Admin, TutorSession, Expertise,Lesson, Invoice , Tutor, Course, CancellationRequest, Term
from .forms import CourseForm, ExpertiseForm
from django.db.models import Prefetch
from django.core.paginator import Paginator





# @login_required
# def dashboard(request):
#     """Display the current user's dashboard."""

#     current_user = request.user
#     # Check if the user is an admin
#     is_admin = hasattr(current_user, 'admin_profile')

#     context = {
#         'is_admin': is_admin,
#     }
#     return render(request, 'dashboard.html', {'user': current_user})

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user

    if hasattr(current_user, 'student_profile'):
        return redirect('student_dashboard')  # Redirect to student dashboard
    elif hasattr(current_user, 'admin_profile'):
        return redirect('admin_dashboard')  # Redirect to admin dashboard
    elif hasattr(current_user, 'tutor_profile'):
        return redirect('tutor_dashboard')  # Redirect to tutor dashboard

    messages.error(request, "Your account type is not authorized to access a dashboard.")
    return redirect('home')


@login_required
def student_courses_view(request):
    """Display courses a student is enrolled in and their assigned tutors."""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard')

    lessons = Lesson.objects.filter(student=student)

    if not lessons.exists():
        messages.info(request, "You are not enrolled in any courses yet.")
        return render(request, 'student_courses.html', {"courses_and_tutors": []})

    courses_and_tutors = [
        {
            "course_name": lesson.course.name,
            "tutor_name": lesson.tutor.user.full_name()
        }
        for lesson in lessons
    ]

    return render(request, 'student_courses.html', {"courses_and_tutors": courses_and_tutors})

@login_required
def student_lesson_schedule_view(request):
    """Display the lesson schedule for the logged-in student, including tutor details."""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard')

    lessons = Lesson.objects.filter(student=student).order_by('session__time', 'session__start_date')

    if not lessons.exists():
        messages.info(request, "No lessons scheduled.")
        return render(request, 'student_lesson_schedule.html', {"schedule": []})

    schedule = [
        {
            "course_name": lesson.course.name,
            "tutor_name": lesson.tutor.user.full_name(),
            "time": lesson.session.time.strftime("%I:%M %p"),
            "date": lesson.session.start_date.strftime("%Y-%m-%d"),
            "term": lesson.term.name,
        }
        for lesson in lessons
    ]

    return render(request, 'student_lesson_schedule.html', {"schedule": schedule})

@login_required
def tutor_schedule_view(request):
    """Display the schedule for the logged-in tutor, including assigned students and lesson details."""
    try:
        tutor = request.user.tutor_profile
    except AttributeError:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard')

    lessons = Lesson.objects.filter(tutor=tutor).order_by('session__start_date', 'session__time')

    if not lessons.exists():
        messages.info(request, "No lessons scheduled.")
        return render(request, 'tutor_schedule.html', {"schedule": []})

    schedule = [
        {
            "course_name": lesson.course.name,
            "student_name": lesson.student.user.full_name(),
            "time": lesson.session.time.strftime("%I:%M %p"),
            "date": lesson.session.start_date.strftime("%Y-%m-%d"),
            "term": lesson.term.name,
        }
        for lesson in lessons
    ]

    return render(request, 'tutor_schedule.html', {"schedule": schedule})

@login_required
def student_payment_history_view(request):
    """
    View to display the payment history of the logged-in student, with optional status filtering.
    """
    invoices = Invoice.objects.filter(student__user=request.user).order_by('-due_date')

    status_filter = request.GET.get('status')

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    return render(request, 'student_payment_history.html', {
        'invoices': invoices,
        'status_filter': status_filter,  
    })

@login_required
def student_dashboard(request):
    """Student dashboard with summarized data and actions."""
    student = request.user.student_profile  # Fetch the logged-in student's profile

    context = {
        'upcoming_classes': Lesson.objects.filter(student=student, start_date__gte=timezone.now()).order_by('start_date')[:5],
        'enrolled_classes': student.enrolled_courses(),
        'invoices': Invoice.objects.filter(student=student),
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def tutor_dashboard(request):
    """Tutor dashboard with summarized data and actions."""
    tutor = request.user.tutor_profile  # Fetch the logged-in tutor's profile

    context = {
        'upcoming_lessons': Lesson.objects.filter(tutor=tutor, start_date__gte=timezone.now()).order_by('start_date')[:5],
        'assigned_students': Student.objects.filter(lessons__tutor=tutor).distinct(),
    }
    return render(request, 'tutor_dashboard.html', context)

@login_required
def admin_invoice_view(request):
    """
    View for admin to view and filter invoices by status and student.
    """
    invoices = Invoice.objects.select_related('student__user', 'lesson').all()

    # Get filters from request
    status_filter = request.GET.get('status')
    student_filter = request.GET.get('student')

    # Apply filters if provided
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if student_filter:
        invoices = invoices.filter(student__user__username__icontains=student_filter)

    return render(request, 'admin_invoice_view.html', {
        'invoices': invoices,
        'status_filter': status_filter,
        'student_filter': student_filter,
    })

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url
        

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            Admin.objects.get(user=request.user)
        except Admin.DoesNotExist:
            messages.error(request, "You must be an admin to access this page.")
            return redirect('home')  # Redirect to a suitable page
        return super().dispatch(request, *args, **kwargs)


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('home')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    
class TutorSignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle tutor sign ups."""

    form_class = TutorSignUpForm
    template_name = "tutor_sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class LessonRequestView(LoginRequiredMixin, FormView): 
    form_class = LessonRequestForm  
    template_name = "lesson_requests.html"
    success_url = 'student_dashboard'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            term = form.cleaned_data['term']
            course = form.cleaned_data['course']
            duration_minutes = form.cleaned_data['duration_minutes']
            frequency = form.cleaned_data['frequency']

            try:
                # Ensure the logged-in user is a student
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                messages.error(request, "You must be a registered student to request a lesson.")
                return redirect(self.get_success_url())
            
            # Check if the request is late
            two_weeks_before = term.start_date - timedelta(weeks=2)
            is_late = timezone.now().date() > two_weeks_before

            lesson_request = LessonRequest.objects.create(
                student=student,
                frequency=frequency,
                duration_minutes=duration_minutes,
                course=course,
                term=term,
                status='pending',
                is_late=is_late,
            )
            
            #Set a warning message if the request is late
            if is_late:
                messages.warning(request, "Warning: This request was submitted late and may not be prioritized.")


            messages.success(request, "Your lesson request has been submitted successfully!")
            return redirect(self.success_url)

    
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display the LessonRequestForm.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    

def allocated_lessons_view(request):
    """Admin view to display all allocated lessons."""
    try:
        # Ensure the logged-in user is a student
        admin = Admin.objects.get(user=request.user)
    except Admin.DoesNotExist:
        messages.error(request, "You must be an admin to access this page.")
        return redirect('home')
    
    # Get filter values from GET parameters
    term_filter = request.GET.get('term')
    tutor_filter = request.GET.get('tutor')
    frequency_filter = request.GET.get('frequency')
    course_filter = request.GET.get('course')
    duration_filter = request.GET.get('duration')
    student_filter = request.GET.get('student')
    
    lessons = Lesson.objects.filter(session__is_booked=True) 

     # Apply filters
    if tutor_filter:
        lessons = lessons.filter(tutor__id=tutor_filter)
    if student_filter:
        lessons = lessons.filter(student__id=student_filter)
    if term_filter:
        lessons = lessons.filter(term__id=term_filter)
    if frequency_filter:
        lessons = lessons.filter(frequency=frequency_filter)
    if course_filter:
        lessons = lessons.filter(course = course_filter)
    if duration_filter:
        lessons =lessons.filter(duration_minutes=duration_filter)


    sort_by = request.GET.get('sort', 'start_date')  
    allowed_sort_fields = {
        'start_date': 'start_date',
        'start_date_desc': '-start_date',
        'end_date': 'end_date',
        'end_date_desc': '-end_date',
    }
    if sort_by in allowed_sort_fields:
        lessons = lessons.order_by(allowed_sort_fields[sort_by])

    # set 10 requests per page
    paginator = Paginator(lessons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    students = Student.objects.all()
    tutors = Tutor.objects.all()
    terms = Term.objects.all()
    courses = Course.objects.all()
    frequencies = TutorSession.FREQUENCY_CHOICES
    durations = TutorSession.DURATION_CHOICES


    return render(request, 'allocated_lessons.html', {
        'page_obj': page_obj,
        'lessons': page_obj.object_list,
        'tutors': tutors,
        'students': students,
        'terms':terms,
        'courses':courses,
        'frequencies':frequencies,
        'durations':durations

        })

def tutor_sessions_view(request):
    """Admin view to display all tutor sessions."""

    if not request.user.is_authenticated:
        messages.error(request, "You must log in to access this page.")
        return redirect('home')
    
    try:
        # Ensure the logged-in user is an admin
        admin = Admin.objects.get(user=request.user)
    except Admin.DoesNotExist:
        messages.error(request, "You must be an admin to access this page.")
        return redirect('home')

    # Get filter values from GET parameters
    term_filter = request.GET.get('term')
    tutor_filter = request.GET.get('tutor')
    frequency_filter = request.GET.get('frequency')
    booked_filter = request.GET.get('booked')
    duration_filter = request.GET.get('duration')

    tutor_sessions = TutorSession.objects.all().order_by("id")  # Ensure queryset is ordered

    # Apply filters
    if term_filter:
        tutor_sessions = tutor_sessions.filter(term__id=term_filter)
    if tutor_filter:
        tutor_sessions = tutor_sessions.filter(tutor__id=tutor_filter)
    if frequency_filter:
        tutor_sessions = tutor_sessions.filter(frequency=frequency_filter)
    if booked_filter in ["true", "false"]:
        tutor_sessions = tutor_sessions.filter(is_booked=(booked_filter == "true"))
    if duration_filter:
        tutor_sessions = tutor_sessions.filter(duration_minutes=duration_filter)

    # Pagination
    paginator = Paginator(tutor_sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass filter options to the template
    terms = Term.objects.all()
    tutors = Tutor.objects.all()
    frequencies = TutorSession.FREQUENCY_CHOICES
    durations = TutorSession.DURATION_CHOICES

    current_filters = {
        "term": term_filter,
        "tutor": tutor_filter,
        "frequency": frequency_filter,
        "booked": booked_filter,
        "duration": duration_filter,
    }

    return render(request, 'admin_tutor_sessions.html', {
        "page_obj": page_obj,
        "tutor_sessions": page_obj.object_list,
        "terms": terms,
        "tutors": tutors,
        "frequencies": frequencies,
        "durations": durations,
        "current_filters": current_filters,
    })



@login_required
def student_lesson_requests(request):  
    """View to display all lesson requests submitted by the logged-in student."""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'You must be a student to view this page.')
        return redirect('home') 

    
    sort_by = request.GET.get('sort', 'requested_date')  # Default sort by requested_date

    allowed_sort_fields = {
     'requested_date': 'requested_date',           
     'requested_date_desc': '-requested_date',     
     'term': 'term__start_date',                   
     'term_desc': '-term__start_date',            
 }

    # Sort the queryset based on the sort_by parameter, if valid
    if sort_by in allowed_sort_fields:
        lesson_requests = LessonRequest.objects.filter(student=student).order_by(allowed_sort_fields[sort_by])
    else:
        lesson_requests = LessonRequest.objects.filter(student=student).order_by('-id')  # Default ordering

    paginator = Paginator(lesson_requests, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'student_lesson_requests.html', {
        'page_obj': page_obj,
        'lesson_requests': page_obj.object_list,
    })
    

@login_required
def manage_lesson_requests(request):
    """Admin view to display and manage all lesson requests."""
    try:
        admin = Admin.objects.get(user=request.user)
    except Admin.DoesNotExist:
        messages.error(request, "You must be an admin to access this page.")
        return redirect('home')

    # Get filter values from GET parameters
    term_filter = request.GET.get('term')
    frequency_filter = request.GET.get('frequency')
    course_filter = request.GET.get('course')
    duration_filter = request.GET.get('duration')
    student_filter = request.GET.get('student')
    status_filter = request.GET.get('status')
    
    lesson_requests = LessonRequest.objects.filter() 

     # Apply filters
    if student_filter:
        lesson_requests = lesson_requests.filter(student__id=student_filter)
    if status_filter:
        lesson_requests = lesson_requests.filter(status=status_filter)
    if term_filter:
        lesson_requests = lesson_requests.filter(term__id=term_filter)
    if frequency_filter:
        lesson_requests = lesson_requests.filter(frequency=frequency_filter)
    if course_filter:
        lesson_requests = lesson_requests.filter(course = course_filter)
    if duration_filter:
        lesson_requests = lesson_requests.filter(duration_minutes=duration_filter)

    sort_by = request.GET.get('sort', 'requested_date')  

    allowed_sort_fields = {
        'requested_date': 'requested_date',
        'requested_date_desc': '-requested_date',
    }

    if sort_by in allowed_sort_fields:
        lesson_requests = lesson_requests.order_by(allowed_sort_fields[sort_by])
    else:
        lesson_requests = lesson_requests.order_by('-id') 

    # set 10 requests per page
    paginator = Paginator(lesson_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)   

    students = Student.objects.all()
    courses = Course.objects.all()
    terms = Term.objects.all()
    durations = TutorSession.DURATION_CHOICES
    frequencies = TutorSession.FREQUENCY_CHOICES
    statuses = LessonRequest.STATUS_CHOICES

    return render(request, 'manage_lesson_requests.html', {
        'page_obj': page_obj,
        'lesson_requests': page_obj.object_list,
        'frequencies': frequencies,
        'courses': courses,
        'durations': durations,
        'students': students,
        'statuses': statuses,
        'terms': terms,
        'sort_by': sort_by,
    })


"""LESSON BOOKING VIEWS START"""
# Step 1: Select Student
class SelectStudentView(AdminRequiredMixin,FormView):

    template_name = "select_student.html"
    form_class = StudentSelectionForm

    def form_valid(self, form):
        student = form.cleaned_data['student']
        self.request.session['student_id'] = student.id  
        return redirect(reverse("select_request"))  


# Step 2: Select Request
class SelectRequestView(AdminRequiredMixin,FormView):
    template_name = "select_request.html"
    form_class = RequestSelectionForm

    def get_form(self):
        student_id = self.request.session.get('student_id')
        if not student_id:
            messages.error(self.request, "Please select a student first.")
            return redirect(reverse("select_student"))
        form = super().get_form()
        form.fields['request'].queryset = LessonRequest.objects.filter(student_id=student_id, status='pending')
        return form

    def form_valid(self, form):
        lesson_request = form.cleaned_data['request']
        self.request.session['request_id'] = lesson_request.id
        return redirect(reverse("select_session")) 


# Step 3: Select Session
class SelectSessionView(AdminRequiredMixin,FormView):
    template_name = "select_session.html"
    form_class = SessionSelectionForm

    def get_form(self):
        request_id = self.request.session.get('request_id')
        if not request_id:
            messages.error(self.request, "Please select a lesson request first.")
            return redirect(reverse("select_request"))

        # Get the lesson request and filter sessions
        lesson_request = LessonRequest.objects.get(id=request_id)

        # Filter sessions based on lesson request and tutor expertise
        sessions = TutorSession.objects.filter(
        duration_minutes=lesson_request.duration_minutes,
        frequency=lesson_request.frequency,
        term=lesson_request.term,
        is_booked=False,
        tutor__expertise=lesson_request.course.ProgrammingLanguage
        ).distinct()

        
        form = super().get_form()
        form.fields['session'].queryset = sessions
        return form

    def form_valid(self, form):
        session = form.cleaned_data.get('session')

        if not session:
            messages.error(self.request, "No session selected. Please choose an action.")
            return redirect(reverse("reject_or_book_later"))
        
       
        self.request.session['session_id'] = session.id
        return redirect(reverse("confirm_booking"))

#Step 4 Confirm Booking (If there is a session)
class ConfirmLessonBookingView(AdminRequiredMixin,FormView):
    template_name = "confirm_booking.html"
    form_class = forms.Form 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        request_id = self.request.session.get('request_id')
        session_id = self.request.session.get('session_id')

        if student_id:
            context['student_name'] = Student.objects.get(id=student_id).user.get_full_name()
        if request_id:
            lesson_request = LessonRequest.objects.get(id=request_id)
            context['request_details'] = f"{lesson_request.course.name} ({lesson_request.term.name})"
        if session_id:
            tutor_session = TutorSession.objects.get(id=session_id)
            context['session_details'] = (
                f"{lesson_request.course.name} - {tutor_session.tutor.user.get_full_name()} "
                f"on {tutor_session.start_date}"
            )
            context['due_date'] = tutor_session.start_date  

        # Add calculated invoice amount to the context
        context['invoice_amount'] = self.calculate_invoice_amount()

        return context

    def calculate_invoice_amount(self):
        """Helper method to calculate the invoice amount."""
        request_id = self.request.session.get('request_id')
        lesson_request = LessonRequest.objects.get(id=request_id)
        session_id = self.request.session.get('session_id')
        if session_id and lesson_request:
            tutor_session = TutorSession.objects.get(id=session_id)
            return tutor_session.calculate_term_cost(lesson_request.course)  
        return 0

    def form_valid(self, form):
        student_id = self.request.session.get('student_id')
        request_id = self.request.session.get('request_id')
        session_id = self.request.session.get('session_id')

        if not all([student_id, request_id, session_id]):
            messages.error(self.request, "Some information is missing. Please start over.")
            return redirect(reverse("select_student"))

        # Fetch instances
        student = Student.objects.get(id=student_id)
        lesson_request = LessonRequest.objects.get(id=request_id)
        session = TutorSession.objects.get(id=session_id)

        # Create the lesson
        booked_lesson = Lesson.objects.create(
            student=student,
            tutor=session.tutor,
            course=lesson_request.course,
            start_day=session.start_day,
            start_date=session.start_date,
            end_date=session.end_date,
            session=session,
            term=lesson_request.term,
            request=lesson_request,
            rollover=True,

        )

        # Create the Invoice
        invoice = Invoice.objects.create(
            student=student,
            lesson=booked_lesson,
            total_amount=self.calculate_invoice_amount(),
            due_date=session.start_date,
        )

        # Update related models
        session.is_booked = True
        session.save()
        lesson_request.status = 'allocated'
        lesson_request.save()

        messages.success(self.request, f"Lesson successfully booked. Invoice amount: ${invoice.total_amount:.2f}")
        return redirect(reverse("manage_lesson_requests"))

#Step 4 Reject Booking or snooze it for later (If there is no session)
class RejectOrBookLaterView(AdminRequiredMixin,FormView):
    template_name = "reject_or_book_later.html"
    form_class = forms.Form 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.request.session.get('request_id')

        if request_id:
            lesson_request = LessonRequest.objects.get(id=request_id)
            context['request_details'] = f"{lesson_request.course.name} ({lesson_request.term.name})"
        
        return context

    def form_valid(self, form):
      
        if "reject_request" in self.request.POST:  
            return self.reject_request()
        elif "book_later" in self.request.POST: 
            return self.book_later()

    def reject_request(self):
 
        request_id = self.request.session.get('request_id')
        if request_id:
            lesson_request = LessonRequest.objects.get(id=request_id)
            lesson_request.status = "rejected"
            lesson_request.rejection_reason = self.request.POST.get("rejection_reason", "No reason provided")
            lesson_request.save()
            messages.success(self.request, "The request has been rejected.")
        
        return redirect(reverse("manage_lesson_requests"))

    def book_later(self):
        #This needs to redirect to lesson requests view 
        messages.info(self.request, "The request has been marked for booking later.")
        return redirect(reverse("manage_lesson_requests"))

    
"""LESSON BOOKING VIEWS END"""
def admin_dashboard(request):
        """Admin dashboard with summarized data."""
        lesson_requests = LessonRequest.objects.filter(status='pending')[:5]  # Top 5 pending requests

        context = {
            'pending_requests': LessonRequest.objects.filter(status='pending').count(),
            'total_lessons': Lesson.objects.count(),
            'unpaid_invoices': Invoice.objects.count(),
            'total_students': Student.objects.count(),
            'total_tutors': Tutor.objects.count(),
            'total_courses': Course.objects.count(),
        }
        return render(request, 'admin_dashboard.html', context)

def student_list(request):
    search_query = request.GET.get('search', '')
    learning_level = request.GET.get('learning_level', '')

    students = Student.objects.all().order_by('id')

    if search_query:
        students = students.filter(user__first_name__icontains=search_query)
    if learning_level:
        students = students.filter(learning_level=learning_level)

    for student in students:
        student.gravatar_url = student.user.gravatar()

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'student_list.html', {
        'page_obj': page_obj,
        'students': page_obj.object_list,})


def student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    enrolled_courses = student.enrolled_courses()
    assigned_tutors = Lesson.objects.filter(student=student).values(
        'tutor__user__first_name', 'tutor__user__last_name', 'tutor__user__email'
    ).distinct()
    lesson_requests = LessonRequest.objects.filter(student=student)
    schedule = Lesson.objects.filter(student=student).order_by('session__start_date', 'session__time')

    back_url = request.META.get('HTTP_REFERER', reverse('student_list'))

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'assigned_tutors': assigned_tutors,
        'lesson_requests': lesson_requests,
        'schedule': schedule,
        'back_url': back_url,
    }

    return render(request, 'student_detail.html', context)


def tutor_list(request):
    search_query = request.GET.get('search', '').strip()

    tutors = Tutor.objects.all().order_by('id')

    if search_query:
        tutors = tutors.filter(user__first_name__icontains=search_query)

    paginator = Paginator(tutors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tutor_list.html',
        {'page_obj': page_obj,
         'tutors': page_obj.object_list,})

def tutor_detail(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    expertise = tutor.expertise.all()
    available_sessions = TutorSession.objects.filter(tutor=tutor, is_booked=False)
    booked_sessions = TutorSession.objects.filter(tutor=tutor, is_booked=True).prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.select_related('student__user', 'course'))
    )

    back_url = request.META.get('HTTP_REFERER', reverse('tutor_list'))

    return render(request, 'tutor_detail.html', {
        'tutor': tutor,
        'expertise': expertise,
        'available_sessions': available_sessions,
        'booked_sessions': booked_sessions,
        'back_url' : back_url,
    })


def course_list(request):
    search_query = request.GET.get('search', '')
    expertise_filter = request.GET.get('expertise', '')

    courses = Course.objects.all().order_by('name')

    if search_query:
        courses = courses.filter(name__icontains=search_query)

    if expertise_filter:
        courses = courses.filter(ProgrammingLanguage__name__iexact=expertise_filter)

    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'course_list.html', {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
        'expertise': Expertise.objects.all()
    })

def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(request, 'course_add.html', {'form': form})


def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)

    return render(request, 'course_edit.html', {'form': form, 'course': course})

def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course_name = course.name
        course.delete()
        messages.success(request, f"The course '{course_name}' has been successfully deleted.")
        return redirect('course_list')

    return render(request, 'course_delete.html', {'course': course})


def expertise_list(request):
    search_query = request.GET.get('search', '')

    expertise = Expertise.objects.all().order_by('name')
    if search_query:
        expertise = expertise.filter(name__icontains=search_query)

    paginator = Paginator(expertise, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'expertise_list.html', {
        'page_obj': page_obj,
        'expertise': page_obj.object_list,
    })

def expertise_add(request):
    if request.method == 'POST':
        form = ExpertiseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New expertise added successfully!")
            return redirect('expertise_list')
    else:
        form = ExpertiseForm()

    return render(request, 'expertise_add.html', {'form': form})

def expertise_edit(request, expertise_id):
    expertise = get_object_or_404(Expertise, id=expertise_id)

    if request.method == 'POST':
        form = ExpertiseForm(request.POST, instance=expertise)
        if form.is_valid():
            form.save()
            messages.success(request, "Expertise updated successfully!")
            return redirect('expertise_list')
    else:
        form = ExpertiseForm(instance=expertise)

    return render(request, 'expertise_edit.html', {'form': form, 'expertise': expertise})

def expertise_delete(request, expertise_id):
    expertise = get_object_or_404(Expertise, id=expertise_id)

    if request.method == 'POST':
        expertise_name = expertise.name
        expertise.delete()
        messages.success(request, f"'{expertise_name}' has been deleted.")
        return redirect('expertise_list')

    return render(request, 'expertise_delete.html', {'expertise': expertise})

@login_required
def CancellationRequestView(request):
    if request.method == 'POST':
        form = CancellationRequestForm(request.POST, user=request.user)  # Pass the user to the form
        if form.is_valid():

            cancellation_request = form.save(commit=False)
            # Assign the logged-in user to the `user` field
            cancellation_request.user = request.user
            
            cancellation_request.save()
            messages.success(request, "Your cancellation request has been submitted.")
            return redirect('student_dashboard')  # Redirect to the dashboard or another page
    else:
        form = CancellationRequestForm(user=request.user)  # Pass the user to the form
    return render(request, 'cancellation_request.html', {'form': form})

@login_required
def manage_cancellation_requests(request):
    """Admin view to display and manage all cancellation requests."""
    try:
        admin = Admin.objects.get(user=request.user)
    except Admin.DoesNotExist:
        messages.error(request, "You must be an admin to access this page.")
        return redirect('home')

    # Base queryset
    cancellation_requests = CancellationRequest.objects.select_related(
        'lesson', 'lesson__student__user', 'lesson__tutor__user'
    ).all()

    # Sorting logic
    sort_by = request.GET.get('sort', 'request_date')
    allowed_sort_fields = {
        'request_date': 'request_date',
        'request_date_desc': '-request_date',
    }

    if sort_by in allowed_sort_fields:
        cancellation_requests = cancellation_requests.order_by(allowed_sort_fields[sort_by])
    else:
        cancellation_requests = cancellation_requests.order_by('-id')

    # Handle POST requests for accept/reject actions
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')

        if not action or not request_id:
            messages.error(request, "Invalid action or request ID.")
            return redirect('manage_cancellation_requests')

        cancellation_request = get_object_or_404(CancellationRequest, id=request_id)

        if action == 'accept':
            lesson = Lesson.objects.select_related('session').get(id=cancellation_request.lesson.id)
            lesson.rollover = False
            lesson.save()
            cancellation_request.status = 'approved'
            cancellation_request.save()

            messages.success(request, "Cancellation request approved. This session will not be rolled over to next semester.")
        elif action == 'reject':
            cancellation_request.status = 'rejected'
            cancellation_request.save()
            messages.success(request, "Cancellation request rejected.")

        return redirect('manage_cancellation_requests')

    # Pagination
    paginator = Paginator(cancellation_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context data for filters and sorting
    return render(request, 'manage_cancellation_requests.html', {
        'page_obj': page_obj,
        'cancellation_requests': page_obj.object_list,
        'sort_by': sort_by,
    })

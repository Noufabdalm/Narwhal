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
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, StudentSelectionForm,RequestSelectionForm,SessionSelectionForm #, StudentForm, CourseForm, TermForm, CombinedLessonRequestForm
from tutorials.helpers import login_prohibited
from django.utils import timezone
from datetime import timedelta

#not sure yet
from .models import Student, LessonRequest, Term, TutorSession, Expertise,Lesson, Invoice 
#from .models import Student, Lesson, LessonRequest


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})
    #return render(request, 'dashboard.html', {'user': current_user})


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
        return reverse('dashboard')


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
    

class LessonRequestView(LoginRequiredMixin, FormView): 
    form_class = LessonRequestForm  
    template_name = "lesson_requests.html"
    success_url = '/dashboard/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Extract the cleaned data
            term = form.cleaned_data['term']
            course = form.cleaned_data['course']
            frequency = form.cleaned_data['frequency']
            duration_minutes = form.cleaned_data['duration_minutes']

            try:
                # Ensure the logged-in user is a student
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                messages.error(request, "You must be a registered student to request a lesson.")
                return redirect(self.get_success_url())
            
            # Check if the request is late
            # two_weeks_before = term.start_date - timedelta(weeks=2)
            # is_late = timezone.now().date() > two_weeks_before

            # Create the LessonRequest instance
            lesson_request = LessonRequest.objects.create(
                student=student,
                course=course,
                frequency=frequency,
                duration_minutes=duration_minutes,
                term=term,
                status='pending',
            )

            # Set a warning message if the request is late
            # if is_late:
            #     messages.warning(request, "Warning: This request was submitted late and may not be prioritized.")


            messages.success(request, "Your lesson request has been submitted successfully!")
            return redirect(self.success_url)

        # If form is not valid, re-render the form with errors
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display the LessonRequestForm.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    

"""LESSON BOOKING VIEWS START"""
# Step 1: Select Student
class SelectStudentView(FormView):
    template_name = "select_student.html"
    form_class = StudentSelectionForm

    def form_valid(self, form):
        student = form.cleaned_data['student']
        self.request.session['student_id'] = student.id  # Store student in session
        return redirect(reverse("select_request"))  # Redirect to the next step


# Step 2: Select Request
class SelectRequestView(FormView):
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
        return redirect(reverse("select_session"))  # Redirect to the next step


# Step 3: Select Session
class SelectSessionView(FormView):
    template_name = "select_session.html"
    form_class = SessionSelectionForm

    def get_form(self):
        request_id = self.request.session.get('request_id')
        if not request_id:
            messages.error(self.request, "Please select a lesson request first.")
            return redirect(reverse("select_request"))
        form = super().get_form()
        lesson_request = LessonRequest.objects.get(id=request_id)
        form.fields['session'].queryset = TutorSession.objects.filter(
            course=lesson_request.course,
            term=lesson_request.term,
            is_booked=False
        )
        return form

    def form_valid(self, form):
        session = form.cleaned_data['session']
        self.request.session['session_id'] = session.id
        return redirect(reverse("confirm_booking"))


class ConfirmLessonBookingView(FormView):
    template_name = "confirm_booking.html"
    form_class = forms.Form  # No fields needed, just confirmation

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
                f"{tutor_session.course.name} - {tutor_session.tutor.user.get_full_name()} "
                f"on {tutor_session.start_date}"
            )
            context['due_date'] = tutor_session.start_date  #Assuming start_date is the due dat

        # Add calculated invoice amount to the context
        context['invoice_amount'] = self.calculate_invoice_amount()

        return context

    def calculate_invoice_amount(self):
        """Helper method to calculate the invoice amount."""
        session_id = self.request.session.get('session_id')
        if session_id:
            tutor_session = TutorSession.objects.get(id=session_id)
            return tutor_session.calculate_term_cost()  # Assuming `calculate_term_cost` is defined in TutorSession
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
            course=session.course,
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
        return redirect(reverse("dashboard"))


    
"""LESSON BOOKING VIEWS END"""




#testing 
# def combined_lesson_request_view(request):
#     if request.method == 'POST':
#         form = CombinedLessonRequestForm(request.POST)
        
#         if form.is_valid():
#             # Get cleaned data from the form
#             learning_level = form.cleaned_data['learning_level']
#             course = form.cleaned_data['course']
#             term = form.cleaned_data['term']
#             preferred_time = form.cleaned_data['preferred_time']
            
#             # Find the student making the request
#             student = Student.objects.get(user=request.user)

#             # Save the data into the LessonRequest model
#             lesson_request = LessonRequest.objects.create(
#                 student=student,
#                 course=course,
#                 term=term,
#                 frequency='weekly',  # Example default value for frequency
#                 status='pending'  # Default status
#             )
            
#             messages.success(request, "Your lesson request has been successfully submitted!")
#             return redirect('dashboard')  # Redirect to the student's dashboard or any other relevant page
        
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = CombinedLessonRequestForm()

#     return render(request, 'request_lesson.html', {'form': form})


def student_list(request):
    search_query = request.GET.get('search', '')
    learning_level = request.GET.get('learning_level', '')

    students = Student.objects.all()

    if search_query:
        students = students.filter(user__first_name__icontains=search_query)
    if learning_level:
        students = students.filter(learning_level=learning_level)

    for student in students:
        student.gravatar_url = student.user.gravatar()

    return render(request, 'student_list.html', {'students': students})


def student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    enrolled_courses = student.enrolled_courses()
    assigned_tutors = Lesson.objects.filter(student=student).values(
        'tutor__user__first_name', 'tutor__user__last_name', 'tutor__user__email'
    ).distinct()
    lesson_requests = LessonRequest.objects.filter(student=student)
    schedule = Lesson.objects.filter(student=student).order_by('session__start_date', 'session__time')

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'assigned_tutors': assigned_tutors,
        'lesson_requests': lesson_requests,
        'schedule': schedule,
    }

    return render(request, 'student_detail.html', context)
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
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm, StudentSelectionForm,RequestSelectionForm,SessionSelectionForm
from tutorials.helpers import login_prohibited
from django.utils import timezone
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required


from .models import Student, LessonRequest, Term, TutorSession, Expertise,Lesson, Invoice , Tutor, Course
from .forms import CourseForm, ExpertiseForm
from django.db.models import Prefetch
from django.core.paginator import Paginator



@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


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
            preferred_time = form.cleaned_data['preferred_time']
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

            # Create the LessonRequest instance
            lesson_request = LessonRequest.objects.create(
                student=student,
                frequency=frequency,
                course=course,
                term=term,
                status='pending',
            )

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
        return redirect(reverse("select_session")) 


# Step 3: Select Session
class SelectSessionView(FormView):
    template_name = "select_session.html"
    form_class = SessionSelectionForm

    def get_form(self):
        request_id = self.request.session.get('request_id')
        if not request_id:
            messages.error(self.request, "Please select a lesson request first.")
            return redirect(reverse("select_request"))

        # Get the lesson request and filter sessions
        lesson_request = LessonRequest.objects.get(id=request_id)
        sessions = TutorSession.objects.filter(
            duration_minutes = lesson_request.duration_minutes,
            frequency = lesson_request.frequency,
            term=lesson_request.term,
            is_booked=False
        )

        # Dynamically update the queryset for the session field
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
                f"{lesson_request.course.name} - {tutor_session.tutor.user.get_full_name()} "
                f"on {tutor_session.start_date}"
            )
            context['due_date'] = tutor_session.start_date  #Assuming start_date is the due dat

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
            return tutor_session.calculate_term_cost(lesson_request.course)  # Assuming `calculate_term_cost` is defined in TutorSession
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
        return redirect(reverse("dashboard"))

#Step 4 Reject Booking or snooze it for later (If there is no session)
class RejectOrBookLaterView(FormView):
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
        
        return redirect(reverse("dashboard"))

    def book_later(self):
        #This needs to redirect to lesson requests view 
        messages.info(self.request, "The request has been marked for booking later.")
        return redirect(reverse("dashboard"))

    
"""LESSON BOOKING VIEWS END"""

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


@login_required
def student_lesson_requests(request):
    """View to display all lesson requests submitted by the logged-in student."""
    try:
        student = request.user.student_profile
    except AttributeError:
        return render(request, 'error.html', {'message': 'You must be a student to view this page.'})

    lesson_requests = LessonRequest.objects.filter(student=student).order_by('-id')
    return render(request, 'request_list.html', {'lesson_requests': lesson_requests})

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

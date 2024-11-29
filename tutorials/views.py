from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, LessonRequestForm #, StudentForm, CourseForm, TermForm, CombinedLessonRequestForm
from tutorials.helpers import login_prohibited

#not sure yet
from .models import Student, LessonRequest, Term, TutorSession, Expertise,Lesson 


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

    def request_lesson_view(self, request):
        if request.method == 'POST':
            form = LessonRequestForm(request.POST)
            if form.is_valid():
                # Extract the cleaned data
                learning_level = form.cleaned_data['learning_level']
                preferred_time = form.cleaned_data['preferred_time']
                term = form.cleaned_data['term']
                programming_language = form.cleaned_data['programming_language']
                
                # Assuming the logged-in user is a student
                student = Student.objects.get(user=request.user)

                # Create LessonRequest instance
                lesson_request = LessonRequest.objects.create(
                    student=student,
                    course=programming_language.courses.first(),  # Assume first course for simplicity
                    frequency='weekly',  # Example default value
                    term=term,
                    status='pending'
                )
                
                # Check if the request is late
                # lesson_request.is_late = self.check_if_late(term)
                # lesson_request.save()

                # # Inform the user if the request is late
                # if lesson_request.is_late:
                #     messages.warning(request, "This is a late request. Admins will prioritize it accordingly.")
                # else:
                #     messages.success(request, "Your lesson request has been submitted successfully!")

                return redirect(self.get_success_url())

        else:
            form = LessonRequestForm()


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
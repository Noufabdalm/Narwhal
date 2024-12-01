"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, LessonRequest, Student, TutorSession, Term, Expertise, Course

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user
    

class LessonRequestForm(forms.Form):
    """Form to request a new lesson by specifying the preferred time, language, and type of lesson."""
    learning_level = forms.ChoiceField(
      choices=Student.LEARNING_LEVEL_CHOICES,
      label="Learning Level",
      widget= forms.Select(attrs={'class': 'form-control'})
    )

    preferred_time = forms.ChoiceField(
        choices=TutorSession.TIME_CHOICES,
        label="Preferred Time",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        label="Term",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),  
        empty_label="Select a Course",
        widget=forms.Select(attrs={'class': 'form-control'})  
    )


# class CombinedLessonRequestForm(forms.Form):
#     # Fields from Student model
#     learning_level = forms.ChoiceField(
#         choices=Student.LEARNING_LEVEL_CHOICES, 
#         label="Learning Level"
#     )
    
#     # Fields from Course model
#     course = forms.ModelChoiceField(
#         queryset=Course.objects.all(), 
#         label="Course"
#     )
    
#     # # Fields from Term model
#     # term = forms.ModelChoiceField(
#     #     queryset=Term.objects.all(), 
#     #     label="Term"
#     # )
    
#     # Additional field for preferred lesson time
#     preferred_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         label="Preferred Time"
#     )
# #testings      ``
# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = ['learning_level']

# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#         fields = ['name']

# class TermForm(forms.ModelForm):
#     class Meta:
#         model = Term
#         fields = ['name']    

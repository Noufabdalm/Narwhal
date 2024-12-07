"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Expertise, LessonRequest, Student, TutorSession, Term, Course

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


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'level', 'price_per_hour', 'ProgrammingLanguage']

class ExpertiseForm(forms.ModelForm):
    class Meta:
        model = Expertise
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter expertise name'}),
        }


class LessonRequestForm(forms.Form):
    """Form to request a new lesson by specifying the preferred time, language, and type of lesson."""
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),  
        empty_label="Select a Course",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    frequency = forms.ChoiceField(
        choices=TutorSession.FREQUENCY_CHOICES,
        label="Frequency",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        label="Term",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    preferred_time = forms.ChoiceField(
        choices=TutorSession.TIME_CHOICES,
        label="Preferred Time",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     

"""LESSON BOOKING FORMS START"""

class StudentSelectionForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Select a Student",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

class RequestSelectionForm(forms.Form):
    request = forms.ModelChoiceField(
        queryset=LessonRequest.objects.none(),  # Queryset populated dynamically
        label="Select a Request",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

class SessionSelectionForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=TutorSession.objects.none(),  # Queryset populated dynamically
        label="Select a Session",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

"""LESSON BOOKING FORMS END"""

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['level', 'ProgrammingLanguage']

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get('level')
        expertise = cleaned_data.get('ProgrammingLanguage')

        LEVEL_PRICES = {
            'beginner': 20.0,
            'intermediate': 40.0,
            'advanced': 60.0,
        }
        def get_article(word):
            if word[0].lower() in 'aeiou':
                return 'an'
            return 'a'

        if level and expertise:
            cleaned_data['name'] = f"{expertise.name.capitalize()} {level.capitalize()} Course"
            article = get_article(level)
            cleaned_data['description'] = f"This is {article} {level.lower()} course for {expertise.name.capitalize()}"
            cleaned_data['price_per_hour'] = LEVEL_PRICES[level]

        return cleaned_data

    def save(self, commit=True):
        course = super().save(commit=False)
        course.name = self.cleaned_data['name']
        course.description = self.cleaned_data['description']
        course.price_per_hour = self.cleaned_data['price_per_hour']
        if commit:
            course.save()
        return course

class ExpertiseForm(forms.ModelForm):
    class Meta:
        model = Expertise
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter expertise name'}),
        }


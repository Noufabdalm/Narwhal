from django.contrib import admin
from .models import User, Admin, Student, Expertise, Tutor, Course, Term, TutorSession, LessonRequest, Lesson


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('last_name', 'first_name')


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_level')
    search_fields = ('user__username', 'user__email', 'learning_level')
    list_filter = ('learning_level',)


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_expertise')
    search_fields = ('user__username', 'user__email', 'expertise__name')
    filter_horizontal = ('expertise',)

    def display_expertise(self, obj):
        return ", ".join([exp.name.capitalize() for exp in obj.expertise.all()])
    display_expertise.short_description = 'Expertise'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'price_per_hour', 'duration_minutes', 'frequency', 'ProgrammingLanguage')
    search_fields = ('name', 'level', 'ProgrammingLanguage__name')
    list_filter = ('level', 'frequency', 'ProgrammingLanguage')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'course', 'time', 'start_day', 'start_date', 'term', 'is_booked')
    search_fields = ('tutor__user__username', 'course__name', 'term__name')
    list_filter = ('term', 'is_booked', 'start_day', 'time')
    ordering = ('term', 'time', 'start_date')


@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'frequency', 'term', 'status')
    search_fields = ('student__user__username', 'course__name', 'term__name')
    list_filter = ('status', 'term', 'frequency')
    ordering = ('term', 'status')

    def student(self, obj):
        return obj.student.user.full_name()
    student.short_description = 'Student Name'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'tutor_name', 'course', 'session', 'term')
    search_fields = ('student__user__username', 'tutor__user__username', 'course__name', 'term__name')
    list_filter = ('term', 'course')
    ordering = ('term', 'course')

    def student_name(self, obj):
        return obj.student.user.full_name()
    student_name.short_description = 'Student'

    def tutor_name(self, obj):
        return obj.tutor.user.full_name()
    tutor_name.short_description = 'Tutor'

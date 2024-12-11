from django.contrib import admin
from .models import (
    User, Admin, Student, Expertise, Tutor,
    Course, Term, TutorSession, LessonRequest, Lesson,Invoice
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'full_name', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    ordering = ('last_name', 'first_name')


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    """Admin interface for Admin model."""
    list_display = ('user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    list_display = ('user', 'learning_level')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('learning_level',)


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    """Admin interface for Expertise model."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    """Admin interface for Tutor model."""
    list_display = ('user', 'get_expertise')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('expertise',)

    def get_expertise(self, obj):
        return ", ".join([expertise.name.capitalize() for expertise in obj.expertise.all()])
    get_expertise.short_description = 'Expertise'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model."""
    list_display = ('name', 'level', 'price_per_hour', 'ProgrammingLanguage')
    search_fields = ('name', 'description')
    list_filter = ('level', 'price_per_hour', 'ProgrammingLanguage')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Admin interface for Term model."""
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')


@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    """Admin interface for TutorSession model."""
    list_display = ('tutor', 'term', 'time', 'start_date','end_date', 'is_booked', 'frequency', 'duration_minutes')
    search_fields = ('tutor__user__username', 'term__name')
    list_filter = ('is_booked', 'frequency', 'duration_minutes', 'term')
    ordering = ('term', 'start_date', 'time')


@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    """Admin interface for LessonRequest model."""
    list_display = ('student', 'course', 'frequency', 'term', 'status','is_late','requested_date')
    search_fields = ('student__user__username', 'course__name', 'term__name')
    list_filter = ('status', 'frequency', 'term')
    ordering = ('term',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model."""
    list_display = ('student', 'tutor', 'course','start_date','end_date', 'session', 'term', 'request')
    search_fields = ('student__user__username', 'tutor__user__username', 'course__name', 'term__name')
    list_filter = ('term',)
    ordering = ('term',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'total_amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('student__user__username', 'lesson__course__name')
    readonly_fields = ('total_amount', 'due_date')  # Make calculated fields readonly in admin
    fieldsets = (
        (None, {
            'fields': ('student', 'lesson', 'status')
        }),
        ('Calculated Fields', {
            'fields': ('total_amount', 'due_date'),
        }),
    )


"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('my-courses/', views.student_courses_view, name='student_courses'),
    path('lesson-schedule/', views.student_lesson_schedule_view, name='student_lesson_schedule'),
    path('tutor-schedule/', views.tutor_schedule_view, name='tutor_schedule'),
    path('lesson_requests/', views.LessonRequestView.as_view(), name='lesson_requests'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_details, name='student_detail'),
    path('tutors/', views.tutor_list, name='tutor_list'),
    path('tutors/<int:tutor_id>/', views.tutor_detail, name='tutor_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_add, name='course_add'),
    path('courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='course_delete'),
    path('expertise/', views.expertise_list, name='expertise_list'),
    path('expertise/add/', views.expertise_add, name='expertise_add'),
    path('expertise/<int:expertise_id>/edit/', views.expertise_edit, name='expertise_edit'),
    path('expertise/<int:expertise_id>/delete/', views.expertise_delete, name='expertise_delete'),
    path('lesson_booking/select_student/', views.SelectStudentView.as_view(), name='select_student'),
    path('lesson_booking/select_request/', views.SelectRequestView.as_view(), name='select_request'),
    path('lesson_booking/select_session/', views.SelectSessionView.as_view(), name='select_session'),
    path('lesson_booking/confirm/', views.ConfirmLessonBookingView.as_view(), name='confirm_booking'),
    path('reject_or_book_later/', views.RejectOrBookLaterView.as_view(), name="reject_or_book_later"),
    path('student_lesson_requests/', views.student_lesson_requests, name='student_lesson_requests'),
    path('manage-lesson-requests/', views.manage_lesson_requests, name='manage_lesson_requests'),
    path('allocated_lessons/', views.allocated_lessons_view, name='allocated_lessons'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('payment-history/', views.student_payment_history_view, name='student_payment_history'),
    path('admin-invoices/', views.admin_invoice_view, name='admin_invoice_view'),


]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
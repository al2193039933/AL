# learning/urls.py
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import dashboard_redirect
from .views import create_course
from . import views
#Tiene el proposito de redireccionar las paginas de forma correcta y pasando los datos apropiados
app_name = 'learning'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='learning/login.html'), name='login'),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create_course/', create_course, name='create_course'),
    path('edit_course/<uuid:course_id>/', views.edit_course, name='edit_course'),
    path('course/<uuid:course_id>/create_unit/', views.create_unit, name='create_unit'),
    path('unit/<uuid:unit_id>/edit/', views.edit_unit, name='edit_unit'),
    path('unit/<uuid:unit_id>/add_material/', views.add_material, name='add_material'),
    path('material/<uuid:material_id>/edit/', views.edit_material, name='edit_material'),
    path('unit/<uuid:unit_id>/edit/', views.edit_unit, name='edit_unit'),
    path('unit/<uuid:unit_id>/create_quiz/', views.create_quiz, name='create_quiz'),
    path('quiz/<uuid:quiz_id>/add_question/', views.add_question_to_quiz, name='add_question_to_quiz'),
    path('quiz/<uuid:quiz_id>/edit_questions/', views.edit_quiz_questions, name='edit_quiz_questions'),
    path('question/<uuid:question_id>/add_answer/', views.add_answer_to_question, name='add_answer_to_question'),
    path('course/<uuid:course_id>/enroll_students/', views.enroll_students, name='enroll_students'),
    path('learning_style_quiz/', views.learning_style_quiz, name='learning_style_quiz'),
    path('student_courses/', views.student_courses, name='student_courses'),
    re_path(r'student_course_dashboard/(?P<course_id>[0-9a-f-]+)/$', views.student_course_dashboard, name='student_course_dashboard'),
    path('student_unit_dashboard/<uuid:unit_id>/', views.student_unit_dashboard, name='student_unit_dashboard'),
    path('unit/<uuid:unit_id>/quiz/', views.student_answer_quiz, name='student_answer_quiz'),
    path('quiz/results/<int:grade>/<uuid:unit_id>/<str:passed>/', views.quiz_results, name='quiz_results'),
]


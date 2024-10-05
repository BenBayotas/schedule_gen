from django.urls import path
from . import views

urlpatterns = [
  path('department-form/', views.department_form_view, name='department_form'),
  path('course-form/', views.course_form_view, name='course_form'),
  path('section-form/', views.section_form_view, name='section_form'),
  path('subject-form/', views.subject_form_view, name='subject_form'),
  path('room-form/', views.room_form_view, name='room_form'),
]

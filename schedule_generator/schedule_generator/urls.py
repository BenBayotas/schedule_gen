"""
URL configuration for schedule_generator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from scheduling import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('department-form/', views.department_form_view, name='department_form'),
    path('course-form/', views.course_form_view, name='course_form'),
    path('section-form/', views.section_form_view, name='section_form'),
    path('subject-form/', views.subject_form_view, name='subject_form'),
    path('room-form/', views.room_form_view, name='room_form'),
    path('', views.home, name='home'),
]

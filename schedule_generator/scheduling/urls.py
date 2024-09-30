from django.urls import path
from . import views

urlpatterns = [
    path('generate-schedule/', views.schedule_view, name='generate-schedule'),
]

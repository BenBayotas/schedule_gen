from django import forms
from .models import *

class ScheduleForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all())
    instructors = forms.ModelMultipleChoiceField(queryset=Instructor.objects.all())
    rooms = forms.ModelMultipleChoiceField(queryset=Room.objects.all())
    timeslots = forms.ModelMultipleChoiceField(queryset=TimeSlot.objects.all())
from django import forms
from .models import Timeslot

class TimeSlotForm(forms.ModelForm):
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%I:%M %p'),
        input_formats=['%I:%M %p'],
        label="Start Time (12-hour format)"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(format='%I:%M %p'),
        input_formats=['%I:%M %p'],
        label="End Time (12-hour format)"
    )

    class Meta:
        model = Timeslot
        fields = ['start_time', 'end_time', 'days']


from django import forms
from .models import Department, Course, Section, Subject, Room

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_id', 'department_name']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'department']

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_id', 'section_name', 'course', 'year_level'] 

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name', 'department', 
                  'course','section', 'year_level', 'requires_laboratory', 
                  'days', 'timeslot', 'weekly_duration'
                  ]    


class RoomForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['room_id', 'room_name', 'is_laboratory', 'department']


    


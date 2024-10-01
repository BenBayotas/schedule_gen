from django.db import models
from datetime import timedelta, datetime, date

TIMESLOTS = (
    ('7:30 AM - 9:00 AM', '7:30 AM - 9:00 AM'),
    ('9:00 AM - 10:30 AM', '9:00 AM - 10:30 AM'),
    ('10:30 AM - 12:00 PM', '10:30 AM - 12:00 PM'),
    ('12:00 PM - 1:30 PM', '12:00 PM - 1:30 PM'),
    ('1:30 PM - 3:00 PM', '1:30 PM - 3:00 PM'),
    ('3:00 PM - 4:30 PM', '3:00 PM - 4:30 PM'),
    ('4:30 PM - 6:00 PM', '4:30 PM - 6:00 PM'),
    ('6:00 PM - 7:30 PM', '6:00 PM - 7:30 PM'),
    ('7:30 PM - 9:00 PM', '7:30 PM - 9:00 PM'),
)
TIMESLOT_CUSTOM = (
    ('7:30 AM', '7:30 AM'),
    ('9:00 AM', '9:00 AM'),
    ('10:30 AM', '10:30 AM'),
    ('12:00 PM', '12:00 PM'),
    ('1:30 PM', '1:30 PM'),
    ('3:00 PM', '3:00 PM'),
    ('4:30 PM', '4:30 PM'),
    ('6:00 PM', '6:00 PM'),
    ('7:30 PM', '7:30 PM'),
    ('9:00 PM', '9:00 PM'),
)

DAYS_OF_WEEK = (
    ('MTh', 'Monday/Thursday'),
    ('TF', 'Tuesday/Friday'),
    ('W', 'Wednesday'),
    ('Sat', 'Saturday'),
)

YEAR = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
)

SUBJECT_TYPE = (
    ('Major', 'Major'),
    ('Minor', 'Minor'),    
)

UNITS = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
)

# Create your models here.


class Room(models.Model):
    room_id = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.room_id}" 
        

class Timeslot(models.Model):
   
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    days = models.CharField(max_length=20, choices=DAYS_OF_WEEK, default='MTh')

    def calculate_end_time(self, duration, session_days):

        if session_days in ["Mth", "TF"]:
            session_duration = duration / 2
        elif session_days in ["W", "Sat"]:
            session_duration = duration
        else:
            raise ValueError("Invalid Session days")

        session_duration_delta = timedelta(hours=session_duration)
        self.end_time = (datetime.combine(date.today(), self.start_time) + session_duration_delta).time()        

    def __str__(self):
        return f"{self.get_days_display()} {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"



class Department(models.Model):
    dept_id = models.CharField(max_length=10, primary_key=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.dept_id} - {self.department_name}"
    

class Course(models.Model):
    course_id = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    

    def __str__(self):
        return f" [{self.department.dept_id}] {self.course_id} - {self.course_name}"
    

class Section(models.Model):
    section_id = models.CharField(max_length=10, primary_key=True)
    section_name = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YEAR, null=True)
    

    def __str__(self):
        return f"{self.course.course_name} {self.section_name} {self.year_level}"


class Subject(models.Model):

    subject_id = models.CharField(max_length=15, primary_key=True)
    subject_name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)
    year_level = models.IntegerField(choices=YEAR, null=True) 

    duration = models.FloatField()
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)

    def set_timeslot_end_time(self):
        self.timeslot.calculate_end_time(self.duration, self.timeslot)
        self.timeslot.save()
    

class Instructor(models.Model):
    id = models.IntegerField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject_expertise = models.ManyToManyField(Subject)  # Instructors can have expertise in many subjects
    
    
    def __str__(self):
        return f"{self.id} ({self.name})"




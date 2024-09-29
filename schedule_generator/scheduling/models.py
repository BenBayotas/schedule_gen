from django.db import models

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
    ('MTH', 'MTH'),
    ('TF', 'TF'),
    ('W', 'W'),
    ('SAT', 'SAT'),
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



# ---------DEPARTMENT HEIRARCHY ---------- #

class Department(models.Model):
    dept_id = models.CharField(max_length=10, unique=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.dept_id} - {self.department_name}"
    

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True, null=True)
    course_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    

    def __str__(self):
        return f" [{self.department.dept_id}] {self.course_id} - {self.course_name}"
    

class Section(models.Model):
    section_name = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YEAR, null=True)
    

    def __str__(self):
        return f"{self.course.course_name} {self.section_name} {self.year_level}"


class Subject(models.Model):

    subject_id = models.CharField(max_length=10, null=True, unique=True)
    subject_name = models.CharField(max_length=100, null=True)
    type = models.CharField(choices=SUBJECT_TYPE, null=True, blank=True)
    lec_units = models.IntegerField(choices=UNITS, default=0, null=True)
    lab_units = models.IntegerField(choices=UNITS, default=0, null=True)

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)
    year_level = models.IntegerField(choices=YEAR, null=True) 

    def __str__(self):
        return f"[{self.subject_id}] - {self.subject_name} ({self.course} {self.year_level})"


class Instructor(models.Model):
    id = models.IntegerField(max_length=20)
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(Subject)  # Instructors can have expertise in many subjects
    subjects_handled = models.ManyToManyField(Subject, related_name='handled_by', blank=True)  # Track the subjects an instructor is handling

    def __str__(self):
        return f"{self.id} ({self.name})"


# -------- UNIVERSITY DATASETS ------------ #

class Room(models.Model):
    room_id = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.room_id}" 


class TimeSlot(models.Model):
    time_slot = models.CharField(choices=TIMESLOTS)
    days = models.CharField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.days} - {self.time_slot}"


class TimeSlotCustom(models.Model):
    start_time = models.CharField(choices=TIMESLOT_CUSTOM, default='7:30 AM')
    end_time = models.CharField(choices=TIMESLOT_CUSTOM, default="9:00 AM")
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, null=True, blank=True)

    def __str__(self):
        return f"{self.day_of_week} {self.start_time} - {self.end_time}"
    

# ------------ SESSION MEETINGS ------------- #

class SessionMeeting(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=True, blank=True)
    timeslot = models.ManyToManyField(TimeSlot)
    days = models.CharField(choices=DAYS_OF_WEEK)
    room = models.ManyToManyField(Room)
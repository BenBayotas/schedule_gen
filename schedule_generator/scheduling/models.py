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

class Department(models.Model):
    dept_id = models.CharField(max_length=10, unique=True)
    dept_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.dept_id} - {self.dept_name}"
    

class Course(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=20, unique=True, null=True)
    course_name = models.CharField(max_length=100)

    def __str__(self):
        return f" [{self.dept.dept_id}] {self.course_id} - {self.course_name}"
    

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_year = models.IntegerField(null=True)
    section_id = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.section_id} {self.course.course_name}"


class Instructor(models.Model):
    instructor_id = models.IntegerField(max_length=20)
    instructor_name = models.CharField(max_length=100, null=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.instructor_name} ({self.instructor_id})"
    

class Subject(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.IntegerField(choices=YEAR, null=True) 
    subject_id = models.CharField(max_length=10, null=True, unique=True)
    subject_name = models.CharField(max_length=100, null=True)
    subject_type = models.CharField(choices=SUBJECT_TYPE, null=True, blank=True)
    lec_units = models.IntegerField(choices=UNITS, default=0, null=True)
    lab_units = models.IntegerField(choices=UNITS, default=0, null=True)
    instructors = models.ManyToManyField(Instructor, related_name="subjects")

    def __str__(self):
        return f"[{self.subject_id}] - {self.subject_name} ({self.course} {self.year})"


class Room(models.Model):
    dept_priority = models.ForeignKey(Department, on_delete=models.CASCADE)
    room_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.room_id} [{self.dept_priority.dept_id}]" 


class TimeSlot(models.Model):
    time_slot = models.CharField(choices=TIMESLOTS)
    days = models.CharField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.days} - {self.time_slot}"


class TimeSlotCustom(models.Model):
    start_time = models.TimeField(default='00:00:00')
    end_time = models.TimeField(default="00:00:00")
    day = models.CharField(choices=DAYS_OF_WEEK, null=True, blank=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
    

class SessionMeeting(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=True, blank=True)
    timeslot = models.ManyToManyField(TimeSlot)
    days = models.CharField(choices=DAYS_OF_WEEK)
    room = models.ManyToManyField(Room)
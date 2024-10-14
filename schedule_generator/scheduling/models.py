from django.db import models


DAYS_OF_WEEK = (
    ('M/TH', 'M/TH'),
    ('T/F', 'T/F'),
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

LOCATION = (
    ('CB MAIN', 'CB MAIN'),
    ('CBS SOUTH', 'CBS SOUTH'),
    ('CBE EAST', 'CBE EAST'),
)



# Create your models here.


   
class Department(models.Model):
    dept_id = models.CharField(max_length=10, unique=True)
    department_name = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.dept_id} - {self.department_name}"
    

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    

    def __str__(self):
        return f" [{self.department.dept_id}] {self.course_id} - {self.course_name}"
    

class Section(models.Model):
    section_id = models.CharField(max_length=10, unique=True)
    section_name = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YEAR, null=True)
    

    def __str__(self):
        return f"{self.course.course_name} {self.section_name} {self.year_level}"


class Room(models.Model):
    room_id = models.CharField(max_length=15, unique=True)
    room_name = models.CharField(max_length=64, null=True, blank=True)
    room_floor = models.IntegerField()
    room_building = models.CharField(max_length=20, choices=LOCATION)
    is_laboratory = models.BooleanField(null=True, blank=True)
    department_priority = models.ManyToManyField(Department, blank=True)
    
    
    def __str__(self):
        return f"{self.room_id}" 


class Subject(models.Model):

    subject_id = models.CharField(max_length=15)
    subject_name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YEAR, null=True)
    requires_laboratory = models.BooleanField(null=True, blank=True) 
    subject_type = models.CharField(max_length=6, choices=SUBJECT_TYPE)


    days = models.CharField(max_length=6, choices=DAYS_OF_WEEK)
    timeslot = models.CharField(max_length= 10, default="7:30AM-9:00AM")
    weekly_duration = models.FloatField(default=3, null=True, blank=True)
    
    def __str__(self):
        return f"[{self.subject_id}] {self.subject_name} | {self.department.dept_id} - {self.course} {self.year_level} | {self.days} {self.timeslot}"    





class Instructor(models.Model):
    instructor_id = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(Subject)  # Instructors can have expertise in many subjects
    
    
    def __str__(self):
        return f"{self.instructor_id} ({self.name})"




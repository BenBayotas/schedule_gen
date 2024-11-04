from django.db import models


DAYS_OF_WEEK = (
    ('M / TH', 'M / TH'),
    ('M / W', 'M / W'),
    ('W / TH', 'W / TH'),
    ('T / F', 'T / F'),
    ('T / W', 'T / W'),
    ('M', 'M'),
    ('T', 'T'),
    ('W', 'W'),
    ('TH', 'TH'),
    ('F', 'F'),
    ('SAT', 'SAT'),
    ('W / W', 'W / W'),
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

SEMESTER = (
    ('1st Semester', '1st Semester'),
    ('2nd Semester', '2nd Semester'),
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

ROOM_TYPES = (
    ('Lecture Room', 'Lecture Room'),
    ('PE Hall', 'PE Hall'),
    ('Gym Hall', 'Gym Hall'),
    ('Civil Engineering Lab', 'Civil Engineering Lab'),
    ('JEEP Start', 'JEEP Start'),
    ('JEEP Accelerate', 'JEEP Accelerate'),
    ('Nursing Lab', 'Nursing Lab'),
    ('Human Anatomy Simulation Center', 'Human Anatomy Simulation Center'),
    ('Computer Laboratory', 'Computer Laboratory'),
    ('EIRC', 'EIRC'),
    ('DSAC', 'DSAC'),
    ('TBI MOESIS', 'TBI MOESIS'),
    ('ETP Drawing Room', 'ETP Drawing Room'),
    ('Chemistry Lab', 'Chemistry Lab'),
    ('Biology Room', 'Biology Room'),
    ('Criminology Lab', 'Criminology Lab'),
    ('Criminology Lecture Room', 'Criminology Lecture Room'),
    ('Hotel de Saturnino', 'Hotel de Saturnino'),
    ('Physics Lab', 'Physics Lab'),
    ('Kitchen', 'Kitchen'),
    ('Drawing Room', 'Drawing Room'),
    

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
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    

    def __str__(self):
        return f" [{self.department.dept_id}] {self.course_id} - {self.course_name}"
    

class Section(models.Model):
    section_id = models.CharField(max_length=10, unique=True)
    section_name = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    year_level = models.IntegerField(choices=YEAR, null=True)
    

    def __str__(self):
        return f"[{self.course.department.dept_id} - {self.course.course_id}] {self.section_name} {self.year_level}"


class Room(models.Model):
    room_id = models.CharField(max_length=15, unique=True)
    room_name = models.CharField(max_length=64, null=True, blank=True)
    room_floor = models.IntegerField()
    room_building = models.CharField(max_length=20, choices=LOCATION)
    is_laboratory = models.BooleanField(default=False)
    department_priority = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    
    # courses = models.ManyToManyField(Course, blank=True, related_name='rooms')
    # priority = models.CharField(max_length=100, default='all')

    """
    def save(self, *args, **kwargs):
        # If no courses are assigned, set priority to "all"
        if not self.courses.exists():
            self.priority = "all"
        else:
            self.priority = ', '.join(course.course_name for course in self.courses.all())
        super().save(*args, **kwargs)

    """

    def __str__(self):
        return f"{self.room_id} {self.room_name}"
    

class LectureRoom(models.Model):
    room_id = models.CharField(max_length=15, unique=True)
    room_name = models.CharField(max_length=64, default='Lecture Room')

    def __str__(self):
        return f"{self.room_id} {self.room_name}"


class Laboratories(models.Model):
    lab_id = models.CharField(max_length=15, unique=True)
    lab_name = models.CharField(max_length=64, default='Laboratory')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.lab_id} {self.lab_name} {self.department.dept_id}"
    

class PEGymHall(models.Model):
    hall_id = models.CharField(max_length=15, unique=True)
    hall_name = models.CharField(max_length=64, default= 'PE Hall')

    def __str__(self):
        return f"{self.hall_id} {self.hall_name}"


    
class Subject(models.Model):

    subject_id = models.CharField(max_length=15)
    subject_name = models.CharField(max_length=100, null=True)
    semester = models.CharField(max_length=50, choices=SEMESTER, default='1st Semester')
    requires_laboratory = models.BooleanField(default=False) 

    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True)
    year_level = models.IntegerField(choices=YEAR, null=True, blank=True)

    days = models.CharField(max_length=12, choices=DAYS_OF_WEEK)
    timeslot = models.CharField(max_length=50, default="07:30AM - 09:00AM")
    starttime = models.CharField(max_length=24, null=True, blank=True)
    
    room_preference = models.CharField(max_length=64,choices=ROOM_TYPES, null=True, blank=True, default='Lecture Room')
    
    def __str__(self):
        return f"[{self.subject_id}] {self.subject_name}| {self.course.course_id} {self.section.section_name} {self.year_level} | {self.days} {self.timeslot}"    


class Timeslot(models.Model):
    days = models.CharField(max_length=20)
    timeslot = models.CharField(max_length=34)

    def __str__(self):
        return f"[{self.days}] {self.timeslot}" 


class SubjectSession(models.Model):
    subject_id = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=64)
    sections = models.ManyToManyField(Section)
    rooms = models.ManyToManyField(Room)
    timeslot = models.ManyToManyField(Timeslot)

    def __str__(self):
        return f"[{self.subject_id}] {self.subject_name}"


class Instructor(models.Model):
    instructor_id = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(Subject)  # Instructors can have expertise in many subjects
    
    
    def __str__(self):
        return f"{self.instructor_id} ({self.name})"
    






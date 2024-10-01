from collections import defaultdict
import random
from datetime import timedelta
from django.utils import timezone
from .models import Department, Course, Section, Subject, Instructor, Room


def initialize_population(population_size):
    
    POPULATION = []
    room_occupancy = defaultdict(list)

    departments = Department.objects.all()

    for _ in range(population_size):
        
        individual_schedule = []
        
        for department in departments:
            courses = department.course_set.all()

            for course in courses:
                for year_level in range(1, 5):
                    sections = Section.objects.filter(course=course, year_level=year_level)
                    subjects = Subject.objects.filter(course=course, year_level=year_level)

                    for section in sections:
                        for subject in subjects:
                            
                            
                            
                            

                            

                            


                    


    
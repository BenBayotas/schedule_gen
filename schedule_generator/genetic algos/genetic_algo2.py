import random
from collections import defaultdict
from scheduling.models import Department, Course, Section, Subject, Instructor, Room, TimeSlot

POPULATION_SIZE = 100
GENERATION = 50
MUTATION_RATE = 0.05


class GenAlgo:
    def __init__(self, population_size, generation, mutation_rate):
        self.population_size = population_size
        self.generation = generation
        self.mutation_rate = mutation_rate


    def initialize_population(self):

        population = []
        departments = Department.objects.all()

        for _ in range(POPULATION_SIZE):
            
            individual_schedule = []

            for department in departments: 
                courses = department.course_set.all()

                for course in courses:

                    for year_level in range(1, 5):
                        sections = Section.objects.filter(course=course, year_level=year_level)
                        subjects = Subject.objects.filter(course=course, year_level=year_level)

                        for section in sections:

                            for subject in subjects:
                                timeslot = random.choice(TimeSlot.objects.all())
                                room = random.choice(Room.objects.all())

                                instructor = random.choice(Instructor.objects.filter(expertise=subject))

                                if instructor.subjects_handled.count() < 3:
                                    session_count_today = sum(1 for s in individual_schedule if s['instructor'] == instructor and s['timeslot'].days == timeslot.days )

                                    if session_count_today < 2:
                                        session = {
                                            'subject': subject,
                                            'timeslot': timeslot,
                                            'room': room,
                                            'instructor': instructor,
                                            'section': section,
                                        }
                                        individual_schedule.append(session)
            population.append(individual_schedule)
        return population    


                 

                
                                
                            
                    
                    
                    

            



      

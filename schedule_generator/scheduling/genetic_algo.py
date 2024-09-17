import random
from models import *

POPULATION_SIZE = 50
MUTATION_RATE = 0.1
NUM_GENERATIONS = 100

class TimetableGA():


    def __init__(self):
        self.subjects = Subject.objects.all()
        self.instructors = Instructor.objects.all()
        self.rooms = Room.objects.all()
        self.timeslots = TimeSlot.objects.all()
        self.population = self.create_inital_population()
    

    def create_inital_population(self):
        population = []
        for _ in range(POPULATION_SIZE):
            individual = []
            for subject in self.subjects:
                room = random.choice(self.rooms)
                instructor = random.choice(subject.instructors.all())
                timeslot = random.choice(self.timeslots)

                session = {
                    'subject': subject,
                    'room': room,
                    'instructor': instructor,
                    'timeslot': timeslot,
                }
                individual.append(session)
            population.append(individual)
        return population     


    def fitness(self, individual):
        score = 0
        room_schedule = {}

        for session in individual:
            room_key = (session['room'], session['timeslot'])
            if room_key in room_schedule:
                score -= 10
            else:
                room_schedule[room_key] = session    



from collections import defaultdict
import random
from datetime import datetime, timedelta
from .models import Department, Course, Section, Subject, Room, Instructor


def parse_timeslot(timeslot):
     
    start_str, end_str = timeslot.split(" - ")
    start_time = datetime.strptime(start_str.strip(), "%I:%M%p").time()
    end_time = datetime.strptime(end_str.strip(), "%I:%M%p").time()

    return start_time, end_time


def parse_days(days):
     
    return [day.strip() for day in days.split(" / ")]

def has_conflict(existing_sessions, new_timeslot, new_days):
     
    new_start, new_end = parse_timeslot(new_timeslot)
    new_days_set = set(parse_days(new_days))

    for session in existing_sessions:
        session_start, session_end = parse_timeslot(session['timeslot'])
        session_days_set = set(parse_days(session['days']))

        if new_days_set & session_days_set:
             if (new_start < session_end and new_end > session_start):
                  return True
    return False    




def initialize_population(population_size):
    
    population = []
    session_occupancy = defaultdict(list)

    '''
    instructor_subject_count = defaultdict(int)
    instructor_daily_sessions = defaultdict(lambda: defaultdict(int))
    '''

    sections = Section.objects.all()
    for _ in range(population_size):

        individual_schedule = []

        for section in sections:
               subjects = Subject.objects.filter(section=section)

               for subject in subjects:
                    
                    days = subject.days
                    timeslot = subject.timeslot

                    starttime = subject.starttime
                    room_preference = subject.room_preference

                    
                    available_rooms = Room.objects.none()

                    if subject.requires_laboratory:
                         room_preference = str(room_preference).strip()
                         preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=True)
                         if preferred_rooms.exists():
                              available_rooms = preferred_rooms
                         else:
                              available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=True)
                              if not available_rooms.exists():
                                   available_rooms = Room.objects.filter(is_laboratory=True)

                    else:
                         room_preference = str(room_preference).strip()
                         preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=False)
                         if preferred_rooms.exists():
                              available_rooms = preferred_rooms
                         else:
                              available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=False)
                              if not available_rooms.exists():
                                   available_rooms = Room.objects.filter(is_laboratory=False)

                    room_assigned = False
                    

                    for _ in range(20):
                         new_room = random.choice(available_rooms)

                         if not has_conflict(session_occupancy[new_room], timeslot, days):
                              
                              session = {
                                   'section': section,
                                   'subject': subject,
                                   'room': new_room,
                                   'days': days,
                                   'timeslot': timeslot,
                                   'starttime': starttime,
                                   'requires_laboratory': subject.requires_laboratory,
                                   'preferred_room': subject.room_preference
                                    
                                }
                              
                              individual_schedule.append(session)
                              session_occupancy[new_room].append(session)       
                              room_assigned = True
                              break
                         
                         if not room_assigned:
                               print(f"Could not assign a room for {subject} without conflict.")

               population.append(individual_schedule)
    return population



def fitness(individual_schedule):

    fitness_score = 0

    session_occupancy = defaultdict(list)

    for session in individual_schedule:

        section = session['section']  
        subject = session['subject']
        start_time = session['starttime']
        timeslot = session['timeslot']
        days = session['days']
        room = session['room']
        
        
        if (start_time, days) in session_occupancy[room]:
            fitness_score -= 10
        else:
            session_occupancy[room].append((start_time, days))
            fitness_score += 5

    return fitness_score

    

def selection(population, fitness_scores, k=3):
     selected = random.choices(population, weights=fitness_scores, k=k)
     
     return selected


def crossover(parent1, parent2):
     cutoff = random.randint(0, len(parent1) - 1)
     child1 = parent1[:cutoff] + parent2[cutoff:]
     child2 = parent2[:cutoff] + parent1[cutoff:]
     
     return child1, child2




def mutate(individual, mutation_rate=0.01, session_occupancy=None):
    
    if session_occupancy is None:
        session_occupancy = defaultdict(list)
        
    if random.random() < mutation_rate:
        
        index = random.randint(0, len(individual) - 1)
        session = individual[index]

        subject = session.get('subject')
        if subject is None:
            return individual  
        
        room_preference = (subject.room_preference or "").strip()
        days = session['days']
        timeslot = session['timeslot']
        default_room = session['room']
        
        if subject.requires_laboratory:
            room_preference = str(room_preference).strip()
            preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=True)
            if preferred_rooms.exists():
                available_rooms = preferred_rooms
            else:
                available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=True)
                if not available_rooms.exists():
                    available_rooms = Room.objects.filter(is_laboratory=True)

        else:
            room_preference = str(room_preference).strip()
            preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=False)
            if preferred_rooms.exists():
                available_rooms = preferred_rooms
            else:
                available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=False)
                if not available_rooms.exists():
                    available_rooms = Room.objects.filter(is_laboratory=False)


        room_found = False
        max_attempts = 20
        for _ in range(max_attempts):
            new_room = random.choice(available_rooms)

            if not has_conflict(session_occupancy[new_room], timeslot, days):

                session['room'] = new_room
                session_occupancy[new_room].append((session))
                room_found = True
                break

       
        if not room_found:
            session['room'] = default_room 

    return individual




''' 

def mutate(individuals, mutation_rate):

    if random.random() < mutation_rate:
        
        index = random.randint(0, len(individuals) - 1)
        session = individuals[index]
        subject = session['subject']
        room_preference = (subject.room_preference or "").strip()
        
        if subject.requires_laboratory:
            preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=True)
            if preferred_rooms.exists():
                available_rooms = preferred_rooms
            else:
                available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=True)
                if not available_rooms.exists():
                    available_rooms = Room.objects.filter(is_laboratory=True)
        else:
            preferred_rooms = Room.objects.filter(room_name__iexact=room_preference, is_laboratory=False)
            if preferred_rooms.exists():
                available_rooms = preferred_rooms
            else:
                available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=False)
                if not available_rooms.exists():
                    available_rooms = Room.objects.filter(is_laboratory=False)
        if available_rooms.exists():
            new_room = random.choice(available_rooms)
            session['room'] = new_room

        individuals[index] = session

    return individuals


'''



class GeneticAlgorithm:
     
     def __init__(self, population_size=100, generations=50, mutation_rate=0.01):
          self.population_size = population_size
          self.generations = generations
          self.mutation_rate = mutation_rate

     def run(self):
          population = initialize_population(self.population_size)

          for _ in range(self.generations):

               population_with_fitness = [(individual, fitness(individual)) for individual in population]  
               population_with_fitness.sort(key=lambda x: x[1], reverse=True)   

               sorted_population = [individual for individual, _ in population_with_fitness]

               new_population = []

               while len(new_population) < self.population_size:
                    
                    #sorted_population = [individual for individual, _ in population_with_fitness]
                    parents = selection(sorted_population, [score for _, score in population_with_fitness])
                    offspring1, offspring2 = crossover(parents[0], parents[1])

                    offspring1 = mutate(offspring1, self.mutation_rate)
                    offspring2 = mutate(offspring2, self.mutation_rate)

                    new_population.extend([offspring1, offspring2])

               population = new_population      
          
          best_individual = sorted_population[0]
     
          return best_individual

          
          
          







                            
                            
                            
                            

                            

                            


                    


    
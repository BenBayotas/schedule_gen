from collections import defaultdict
import random
from .models import Department, Course, Section, Subject, Room, LectureRoom, Laboratories, PEGymHall, Instructor


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
                    department = subject.department
                    days = subject.days
                    timeslot = subject.timeslot
                    room_preference = subject.room_preference

                    # Default to an empty QuerySet in case subject.requires_laboratory is False
                    
                    if subject.requires_laboratory == False or room_preference == "Lecture Room":
                         available_rooms = LectureRoom.objects.all()

                    elif room_preference == "PE Hall" or "Gym Hall":
                         available_rooms = PEGymHall.objects.all()

                    elif subject.requires_laboratory:
                         available_rooms = Laboratories.objects.filter(department=department)
                    



                    room_found = False
                    max_attempts = 20

                    for _ in range(max_attempts):
                         room = random.choice(available_rooms)

                         if (subject, timeslot, days) not in session_occupancy[room]:
                              session = {
                                   'section': section,
                                   'subject': subject,
                                   'room': room,
                                   'days': days,
                                   'timeslot': timeslot, 
                                   }
                              individual_schedule.append(session)

                              session_occupancy[room].append((subject, timeslot, days))
                                           
                              room_found = True
                              break
                         if not room_found:
                              continue

               population.append(individual_schedule)
    return population



def fitness(individual_schedule):

    fitness_score = 0

    session_occupancy = defaultdict(list)

    for session in individual_schedule:

        section = session['section']  
        subject = session['subject']
        timeslot = session['timeslot']
        days = session['days']
        room = session['room']
        
        
        if (subject, timeslot, days) in session_occupancy[room]:
            fitness_score -= 10
        else:
            session_occupancy[room].append((subject, timeslot, days))
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


def mutate(individual, mutation_rate= 0.1):
     
     if random.random() < mutation_rate:
          index = random.randint(0, len(individual) - 1)
          session = individual[index]

          if random.choice([True, False]):
               
               available_rooms = Room.objects.all()
               new_room = random.choice(available_rooms)
               session['room'] = new_room


          individual[index] = session

     return individual 


class GeneticAlgo:
     
     def __init__(self, population_size=100, generations=50, mutation_rate=0.1):
          self.population_size = population_size
          self.generations = generations
          self.mutation_rate = mutation_rate

     def run(self):
          population = initialize_population(self.population_size)

          for generation in range(self.generations):

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

          
          



          
          
          







                            
                            
                            
                            

                            

                            


                    


    
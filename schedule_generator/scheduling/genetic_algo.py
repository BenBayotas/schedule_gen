import random
from collections import defaultdict
from datetime import timedelta
from .models import *


class GeneticAlgorithm:

    def __init__(self, population_size, generations, mutation_rate):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    # Represents a random initial population
    def initialize_population(self, subjects, instructors, rooms, timeslots):
        population = []
        for _ in range(self.population_size):
            individual = []
            for subject in subjects:
                instructor = random.choice(instructors)
                room = random.choice(rooms)
                timeslot = random.choice(timeslots)
                
                individual.append({
                    'subject': subject,
                    'instructor': instructor,
                    'room': room,
                    'timeslot': timeslot,
                })
            population.append(individual)
        return population
    
     # Fitness function: Evaluates how many constraints are violated in a given schedule
    def fitness(self, individual):

        score = 100 # Start with a perfect score

        # Check for room conflicts
        room_occupancy = defaultdict(list) # Tracks room usage per timeslot
        instructor_usage = defaultdict(list) # Tracks instructor usage per timeslot

        for session in individual:
            timeslot = session['timeslot']
            room = session['room']
            instructor = session['instructor']

             # Check room conflicts
            if room in room_occupancy[timeslot]:
                score -= 10 # Penalty for instructor conflict
            else:
                instructor_usage[timeslot].append(room)


            # Check instructor conflicts
            if instructor in instructor_usage[timeslot]:
                score -= 10 # Penalty for instructor conflict
            else:
                instructor_usage[timeslot].append(instructor)    


            # Check if instructor has more than 2 meetings per day
            instructor_meetings = defaultdict(list)
            instructor_meetings[instructor] += 1
            if instructor_meetings[instructor] > 2:
                score -= 5 # Penalty for exceeding 2 meetings per day
        
        
        return score


     # Crossover: Create offspring by combining two parent schedules
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2


    # Mutation: Randomly change an assignment to introduce variation
    def mutate(self, individual, instructors, rooms, timeslots):
        if random.random() < self.mutation_rate:
            mutate_point = random.randint(0, len(individual) - 1)
            individual[mutate_point]['instructor'] = random.choice(instructors)
            individual[mutate_point]['room'] = random.choice(rooms)
            individual[mutate_point]['timeslot'] = random.choice(timeslots)



    # Main loop of the genetic algorithm
    def run(self, subjects, instructors, rooms, timeslots):
        population = self.initialize_population(subjects, instructors, rooms, timeslots)

        for generation in range(self.generations):

            # Sort population by fitness (higher is better)
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)


            # If the best individual has a perfect score, we're done
            if self.fitness(population[0]) == 100:
                break


            # Select the top individuals for reproduction (elitism)
            new_population = population[:self.population_size // 2]


            # Generate offspring through crossover
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population[:self.population_size // 2], 2)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([child1, child2])    


            # Mutate some of the offspring
            for individual in new_population:
                self.mutate(individual, instructors, rooms, timeslots)


            population = new_population

            # Return the best individual (best schedule) 
            return population[0]   









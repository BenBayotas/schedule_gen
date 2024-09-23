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
    def initialize_population(self, departments, courses, sections, subjects, instructors, rooms, timeslots):
        
        population = []

        for _ in range(self.population_size):
            individual = []
            schedule_checker = defaultdict(lambda: defaultdict(list))

            for department in departments:
                dept_course = [course for course in courses if course.department == department]

                for course in dept_course:
                    course_sections = [section for section in sections if section.course == course]

                    for section in course_sections :
                        year_level = section.year_level

                        section_subjects = [
                            subject for subject in subjects 
                            if subject.course == course and subject.year_level == year_level 
                        ]

                        for subject in section_subjects:
                            assigned_timeslot = None
                            assigned_room = None
                            assigned_instructor = None

                            attempts = 0
                            max_attempts = 100
                            while attempts < max_attempts:
                                assigned_timeslot = random.choice(timeslots)
                                assigned_room = random.choice(rooms)
                                assigned_instructor = random.choice(instructors)
                                
                                room_conflict = assigned_room in schedule_checker[assigned_timeslot]['room']
                                instructor_conflict = assigned_instructor in schedule_checker[assigned_timeslot]['instructor']
                                instructor_overload = self.instructor_meeting_count(individual, assigned_instructor) >= 2

                                if not room_conflict and not instructor_conflict and not instructor_overload:
                                    break

                                attempts += 1

                            if attempts == max_attempts:
                                continue

                            schedule_checker[assigned_timeslot]['rooms'].append(assigned_room)
                            schedule_checker[assigned_timeslot]['instructors'].append(assigned_instructor)


                            individual.append({
                                'department': department,
                                'course': course,
                                'section': section,
                                'subject': subject,
                                'instructor': assigned_instructor,
                                'room': assigned_room,
                                'timeslot': assigned_timeslot,
                            })    
            population.append(individual)

        return population    
    
        
    def instructor_meeting_count(self, individual, instructor):

        count = 0
        for session in individual:
            if session['instructor'] == instructor:
                count += 1

        return count        

    
     # Fitness function: Evaluates how many constraints are violated in a given schedule
    def fitness(self, individual):

        score = 100 # Start with a perfect score

        # Check for room conflicts
        room_schedule = defaultdict(list) # Tracks room usage per timeslot
        instructor_schedule = defaultdict(list) # Tracks instructor usage per timeslot

        for session in individual:
            timeslot = session['timeslot']
            room = session['room']
            instructor = session['instructor']
            day = timeslot.day_of_week


        '''
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
        
        '''
        
        room_key = (room, day, timeslot)
        if room_key in room_schedule:
            score -= 10  # Penalty for room conflict
        else:
            room_schedule[room_key].append(session)

        # Instructor Conflict Check
        instructor_key = (instructor, day, timeslot)
        if instructor_key in instructor_schedule:
            score -= 10  # Penalty for instructor conflict
        else:
            instructor_schedule[instructor_key].append(session)

        # Instructor Meeting Limit per Day
        instructor_day_meetings = sum(1 for s in individual if s['instructor'] == instructor and s['timeslot'].day_of_week == day)
        if instructor_day_meetings > 2:
            score -= 5  # Penalty for exceeding daily meeting limit
        
        
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
    def run(self, population, instructors, rooms, timeslots):
    

        for generation in range(self.generations):

            # Sort population by fitness (higher is better)
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)


            # If the best individual has a perfect score, we're done
            if self.fitness(population[0]) >= 100:
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









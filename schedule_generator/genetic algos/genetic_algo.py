import random
from collections import defaultdict
from datetime import timedelta, time
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
                dept_instructor = [instructor for instructor in instructors if instructor.department == department]

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
                                assigned_instructor = random.choice(dept_instructor)
                                
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

        score = 100 # Start with a perfect score and deduct penalties for violations
        room_conflicts_within_dept = 0
        room_conflicts_between_dept = 0
        instructor_overload = 0
        

        instructor_day_sessions = defaultdict(lambda: defaultdict(list))  # Instructor -> day -> count
        instructor_subjects = defaultdict(list) # Instructor -> subject count

        
        for session in individual:
            department = session['department']
            course = session['course']
            section = session['section']
            subject = session['subject']
            instructor = session['instructor']
            room = session['room']
            timeslot = session['timeslot']

            day_of_week = timeslot.day_of_week
            

            # 1. Check for room conflicts within the same department
            for other_session in individual:
                if session == other_session:
                    continue  # Skip the current session being checked

                other_department = other_session['department']
                other_room = other_session['room']
                other_timeslot = other_session['timeslot']

                if department == other_department and timeslot == other_timeslot and room == other_room:
                    room_conflicts_within_dept += 1


            # 2. Check for room conflicts between departments
            for other_session in individual:
                if session == other_session:
                    continue  # Skip the current session being checked

                other_department = other_session['department']
                other_room = other_session['room']
                other_timeslot = other_session['timeslot']

                if department != other_department and timeslot == other_timeslot and room == other_room:
                    room_conflicts_between_dept += 1


             # 3. Check if instructor has more than 2 sessions in a day
            instructor_day_sessions[instructor][day_of_week] += 1
            if instructor_day_sessions[instructor][day_of_week] > 2:
                instructor_overload += 1   


             # 4. Check if instructor is handling more than 3 subjects 
            instructor_subjects[instructor] += 1
            if instructor_subjects[instructor] > 3:
                instructor_overload += 1      

         # Deduct points based on the number of conflicts and overloads
        score -= room_conflicts_within_dept * 10  # Heavily penalize room conflicts within the department
        score -= room_conflicts_between_dept * 10  # Penalize room conflicts between departments
        score -= instructor_overload * 10  # Penalize instructor overload (sessions per day and total subjects)

    # Ensure score does not go below zero
        if score < 0:
            score = 0

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









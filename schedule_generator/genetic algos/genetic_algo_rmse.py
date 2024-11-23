from collections import defaultdict
import random
from datetime import datetime
from .models import Department, Course, Section, Subject, Room, Instructor
import numpy as np
from math import sqrt
from django.db.models import Q

# Helper functions


def parse_timeslot(timeslot):
    start_str, end_str = timeslot.split(" - ")
    start_time = datetime.strptime(start_str.strip(), "%I:%M%p").time()
    end_time = datetime.strptime(end_str.strip(), "%I:%M%p").time()
    return start_time, end_time

def parse_days(days):
    """
    Parses days string and returns a set of individual days.
    Handles both single-day strings (e.g., "M") and multi-day strings (e.g., "M / TH").
    """
    return {day.strip() for day in days.split(" / ")}

def time_conflict(session1, session2):
    """
    Checks if two sessions overlap in time on any common day.
    Includes edge cases like exact start/end matches and partial overlaps.
    """
    start1, end1 = parse_timeslot(session1['timeslot'])
    start2, end2 = parse_timeslot(session2['timeslot'])
    days1 = parse_days(session1['days'])
    days2 = parse_days(session2['days'])
    
    # Check for common days between the sessions
    common_days = days1 & days2
    if common_days:
        # Check if times overlap (even partially or exactly)
        if (start1 < end2 and end1 > start2) or (start2 < end1 and end2 > start1):
            return True
    return False

def has_conflict(existing_sessions, new_timeslot, new_days):
    """
    Checks if a new session has any time or day conflicts with existing sessions.
    """
    new_start, new_end = parse_timeslot(new_timeslot)
    new_days_set = parse_days(new_days)

    for session in existing_sessions:
        session_start, session_end = parse_timeslot(session['timeslot'])
        session_days_set = parse_days(session['days'])

        # Check for overlapping days and conflicting times
        common_days = new_days_set & session_days_set
        if common_days:
            # Times conflict if there is any overlap or if one starts exactly when the other ends
            if (new_start < session_end and new_end > session_start) or (session_start < new_end and session_end > new_start):
                return True
    return False


def time_conflict(session1, session2):
    start1, end1 = parse_timeslot(session1['timeslot'])
    start2, end2 = parse_timeslot(session2['timeslot'])
    days1 = set(parse_days(session1['days']))
    days2 = set(parse_days(session2['days']))

    # Check for overlapping times on any common day
    if days1 & days2:  # If there’s a common day
        return max(start1, start2) < min(end1, end2)  # Times overlap
    return False




# Enhanced Population Initialization
def initialize_population(population_size):
    population = []
    session_occupancy = defaultdict(list)  # Tracks room occupancy to avoid conflicts

    sections = Section.objects.all()
    for _ in range(population_size):
        individual_schedule = []

        for section in sections:
            subjects = Subject.objects.filter(section=section)
            for subject in subjects:
                days = subject.days
                timeslot = subject.timeslot
                room_preference = subject.room_preference or ""

                # Room selection based on lab requirements and department priority
                available_rooms = Room.objects.filter(
                    Q(room_name__icontains=room_preference) |
                    Q(department_priority=subject.department)
                )

                if subject.requires_laboratory:
                    available_rooms = available_rooms.filter(is_laboratory=True)
                else:
                    available_rooms = available_rooms.filter(is_laboratory=False)

                if not available_rooms.exists():
                    available_rooms = Room.objects.filter(is_laboratory=subject.requires_laboratory)

                # Attempt room assignment while respecting timeslot and room constraints
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
                            'starttime': subject.starttime,
                            'requires_laboratory': subject.requires_laboratory,
                            'preferred_room': subject.room_preference
                        }
                        individual_schedule.append(session)
                        session_occupancy[new_room].append(session)
                        room_assigned = True
                        break

                # If room assignment fails after all attempts, log a message for manual review
                if not room_assigned:
                    print(f"Could not assign a room for {subject} without conflict.")

        population.append(individual_schedule)

    return population



# Fitness Function
def fitness(individual_schedule):
    fitness_score = 0
    session_occupancy = defaultdict(list)

    for session in individual_schedule:
        room = session['room']
        timeslot = session['timeslot']
        days = session['days']
        
        start_time, end_time = parse_timeslot(timeslot)
        conflict = False

        # Check against other sessions in the same room
        for occupied_time, occupied_days in session_occupancy[room]:
            if days == occupied_days and (start_time < occupied_time[1] and end_time > occupied_time[0]):
                fitness_score -= 20  # Larger penalty for overlapping times
                conflict = True
                break

        if not conflict:
            session_occupancy[room].append(((start_time, end_time), days))
            fitness_score += 5  # Reward for conflict-free assignments

    return fitness_score


# Selection Functions

def selection(population, fitness_scores, k=3):
    selected = random.choices(population, weights=fitness_scores, k=k)
    return selected


def tournament_selection(population, fitness_scores, tournament_size=3):
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
        selected.append(max(tournament, key=lambda x: x[1])[0])
    return selected


def roulette_wheel_selection(population, fitness_scores):
    scaled_fitness = [score - min(fitness_scores) + 1 for score in fitness_scores]
    total_fitness = sum(scaled_fitness)
    probabilities = [f / total_fitness for f in scaled_fitness]
    selected = random.choices(population, weights=probabilities, k=len(population))
    return selected



# Crossover Function
def crossover(parent1, parent2):
     cutoff = random.randint(0, len(parent1) - 1)
     child1 = parent1[:cutoff] + parent2[cutoff:]
     child2 = parent2[:cutoff] + parent1[cutoff:]
     
     return child1, child2



# Mutation Function
def mutate(individual, mutation_rate=0.01, session_occupancy=None):
    if session_occupancy is None:
        session_occupancy = defaultdict(list)

    if random.random() < mutation_rate:
        index = random.randint(0, len(individual) - 1)
        session = individual[index]
        subject = session.get('subject')
        if subject is None:
            return individual

        room_preference = (subject.room_preference or "").strip()  # Default to an empty string if None
        days = session['days']
        timeslot = session['timeslot']
        default_room = session['room']

        # Adjust room assignment based on room preferences and requirements
        if subject.requires_laboratory:
            available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=True)
            if not available_rooms.exists():
                available_rooms = Room.objects.filter(is_laboratory=True)
        else:
            available_rooms = Room.objects.filter(room_name__icontains=room_preference, is_laboratory=False)
            if not available_rooms.exists():
                available_rooms = Room.objects.filter(is_laboratory=False)

        room_found = False
        for _ in range(20):
            new_room = random.choice(available_rooms)
            start_time, end_time = parse_timeslot(timeslot)

            conflict = False
            for occupied_times, occupied_days in session_occupancy[new_room]:
                if days == occupied_days and (start_time < occupied_times[1] and end_time > occupied_times[0]):
                    conflict = True
                    break
            
            if not conflict:
                session['room'] = new_room
                session_occupancy[new_room].append(((start_time, end_time), days))
                room_found = True
                break

        if not room_found:
            session['room'] = default_room

    return individual



# Genetic Algorithm Class

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
                parents = selection(sorted_population, [score for _, score in population_with_fitness])
                offspring1, offspring2 = crossover(parents[0], parents[1])

                session_occupancy = defaultdict(list)
                offspring1 = mutate(offspring1, self.mutation_rate, session_occupancy)
                offspring2 = mutate(offspring2, self.mutation_rate, session_occupancy)

                new_population.extend([offspring1, offspring2])

            population = new_population

        best_individual = sorted_population[0]
        return best_individual

'''

class GeneticAlgorithm:
    def __init__(self, population_size=100, generations=50, mutation_rate=0.01, elitism_count=5):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count

    def run(self):
        population = initialize_population(self.population_size)

        for _ in range(self.generations):
            population_with_fitness = [(individual, fitness(individual)) for individual in population]
            population_with_fitness.sort(key=lambda x: x[1], reverse=True)

            # Apply elitism to carry over top individuals
            sorted_population = [individual for individual, _ in population_with_fitness]
            new_population = sorted_population[:self.elitism_count]

            # Generate remaining population
            while len(new_population) < self.population_size:
                parents = selection(sorted_population, [score for _, score in population_with_fitness])
                offspring1, offspring2 = crossover(parents[0], parents[1])

                session_occupancy = defaultdict(list)
                offspring1 = mutate(offspring1, self.mutation_rate, session_occupancy)
                offspring2 = mutate(offspring2, self.mutation_rate, session_occupancy)

                new_population.extend([offspring1, offspring2])

            population = new_population

        best_individual = sorted_population[0]
        return best_individual




# Evaluation Functions
def calculate_rmse(population):
    conflict_counts = []

    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0

        for session in individual:
            room = session['room']
            timeslot = session['timeslot']
            days = session['days']
            
            # Parse timeslot and days to ensure consistent format
            parsed_timeslot = parse_timeslot(timeslot)
            parsed_days = parse_days(days)

            # Check if this (timeslot, days) is already occupied in the room
            if (parsed_timeslot, tuple(parsed_days)) in session_occupancy[room]:
                conflicts += 1  # Count as a conflict
            else:
                # Add the session to the room occupancy
                session_occupancy[room].append((parsed_timeslot, tuple(parsed_days)))

        # Record the conflict count for this individual
        conflict_counts.append(conflicts)

    # Calculate RMSE based on the conflicts across all individuals
    return np.sqrt(np.mean(np.square(conflict_counts)))




def calculate_accuracy(population):
    accuracies = []
    
    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0
        total_sessions = len(individual)

        for session in individual:
            room = session['room']
            timeslot = session['timeslot']
            days = session['days']
            
            # Parse timeslot and days to ensure consistent format
            parsed_timeslot = parse_timeslot(timeslot)
            parsed_days = tuple(parse_days(days))  # Convert days list to tuple for consistency

            # Check if this (timeslot, days) already exists in the room
            if (parsed_timeslot, parsed_days) in session_occupancy[room]:
                conflicts += 1  # Count as a conflict
            else:
                # Add this (timeslot, days) to the room's occupancy
                session_occupancy[room].append((parsed_timeslot, parsed_days))

        # Calculate the number of conflict-free sessions
        conflict_free_sessions = max(total_sessions - conflicts, 0)
        # Calculate individual accuracy as a percentage
        individual_accuracy = conflict_free_sessions / total_sessions if total_sessions > 0 else 0
        accuracies.append(individual_accuracy)
    
    # Return average accuracy across the population in percentage
    return max(np.mean(accuracies) * 100, 0)



def calculate_room_assignment_accuracy(population):
    correct_assignments = []
    
    for individual in population:
        individual_correct = 0
        total_sessions = len(individual)
        
        for session in individual:
            room = session['room']
            subject = session['subject']
            room_preference = subject.room_preference
            requires_laboratory = subject.requires_laboratory
            
            if room.room_name == room_preference and room.is_laboratory == requires_laboratory:
                individual_correct += 1

        accuracy = individual_correct / total_sessions if total_sessions > 0 else 0
        correct_assignments.append(accuracy)
    
    return np.mean(correct_assignments) * 100

          







                            
                            
                            
                            

                            

                            


                    


    
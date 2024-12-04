from collections import defaultdict
import random
from datetime import datetime
from .models import *
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


# Helper function to check for overlapping timeslots
def timeslot_overlap(ts1, ts2):
    start1, end1 = ts1
    start2, end2 = ts2
    return max(start1, start2) < min(end1, end2)  # Overlaps if there's any intersection





def assign_room(subject):
    """
    Assigns a room based on the department of the subject and whether it requires a laboratory.
    """
    department = subject.department.department_name
    requires_laboratory = subject.requires_laboratory

    # Assign laboratory rooms if needed
    if requires_laboratory:
        if department == "COMPUTER STUDIES PROGRAM":
            available_rooms = CSPRoom.objects.filter(subject_tags=subject, room_capacity__gt=0)  # Filter rooms that are laboratories
            if not available_rooms.exists():
                available_rooms = CSPRoom.objects.filter(room_capacity__gt=0)  # Default to all CSP rooms
        elif department == "ENGINEERING TECHNOLOGY PROGRAM":
            available_rooms = ETPRoom.objects.filter(subject_tags=subject, room_capacity__gt=0)  # Filter rooms that are laboratories
            if not available_rooms.exists():
                available_rooms = ETPRoom.objects.filter(room_capacity__gt=0)  # Default to all ETP rooms
        else:
            available_rooms = LectureRoom.objects.filter(room_capacity__gt=0)  # Default to all lecture rooms with capacity

    # If laboratory room is not required, assign normal rooms
    else:
        if department == "COMPUTER STUDIES PROGRAM":
            available_rooms = CSPRoom.objects.filter(subject_tags=subject)
            if not available_rooms.exists():
                available_rooms = CSPRoom.objects.all()  # Default to all CSP rooms
        elif department == "ENGINEERING TECHNOLOGY PROGRAM":
            available_rooms = ETPRoom.objects.filter(subject_tags=subject)
            if not available_rooms.exists():
                available_rooms = ETPRoom.objects.all()  # Default to all ETP rooms
        else:
            available_rooms = LectureRoom.objects.all()  # Default to all lecture rooms
    
    return available_rooms


def initialize_population(population_size):
    population = []
    session_occupancy = defaultdict(lambda: defaultdict(list))  # Maps room -> department -> sessions

    sections = Section.objects.all()
    for _ in range(population_size):

        individual_schedule = []

        for section in sections:
            subjects = Subject.objects.filter(section=section)

            for subject in subjects:
                days = subject.days
                timeslot = subject.timeslot
                starttime = subject.starttime
                requires_laboratory = subject.requires_laboratory

                available_rooms = Room.objects.none()

                sub_name = subject.subject_name.strip().lower()
                dept_name = str(subject.department.department_name)

                # Select rooms based on department and requirements
                if dept_name == "COMPUTER STUDIES PROGRAM":
                    if requires_laboratory:
                        available_rooms = CSPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
                        if not available_rooms.exists():
                            available_rooms = CSPRoom.objects.filter(subject_tags__subject_name__icontains=sub_name)
                    else:
                        available_rooms = LectureRoom.objects.all()

                elif dept_name == "ENGINEERING AND TECHNOLOGY PROGRAM":
                    if requires_laboratory:
                        available_rooms = ETPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
                        if not available_rooms.exists():
                            available_rooms = ETPRoom.objects.filter(subject_tags__subject_name__icontains=sub_name)
                    else:
                        available_rooms = LectureRoom.objects.all()

                elif dept_name == "GENERAL DEPARTMENTS":
                    available_rooms = LectureRoom.objects.all()

                else:
                    print(f"Skipping subject {subject.subject_name} due to unrecognized department: {dept_name}")
                    continue

                if not available_rooms.exists():
                    print(f"Skipping subject {subject.subject_name} due to lack of available rooms.")
                    continue

                # Assign a room while avoiding conflicts
                room_assigned = False
                for _ in range(10):
                    new_room = random.choice(available_rooms)

                    # Check for conflicts in the selected room across all departments
                    conflicts = False
                    for sessions in session_occupancy[new_room].values():
                        if has_conflict(sessions, timeslot, days):
                            conflicts = True
                            break

                    if not conflicts:
                        session = {
                            'section': section,
                            'subject': subject,
                            'room': new_room,
                            'days': days,
                            'timeslot': timeslot,
                            'starttime': starttime,
                            'requires_laboratory': requires_laboratory,
                        }
                        individual_schedule.append(session)
                        session_occupancy[new_room][dept_name].append(session)
                        room_assigned = True
                        break

                if not room_assigned:
                    print(f"Could not assign a room for subject {subject.subject_name} without conflict.")

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
        max_attempts = 10
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


class GeneticAlgorithm:
    def __init__(self, population_size=100, generations=50, mutation_rate=0.01):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def run(self):
        population = initialize_population(self.population_size)

        for _ in range(self.generations):
            # Identify and remove conflicting sessions
            clean_population = []
            for individual in population:
                conflicts = []
                session_occupancy = defaultdict(list)
                clean_individual = []

                for session in individual:
                    room = session['room']
                    timeslot = session['timeslot']
                    days = session['days']

                    # Check for conflicts
                    if has_conflict(session_occupancy[room], timeslot, days):
                        conflicts.append(session)
                    else:
                        clean_individual.append(session)
                        session_occupancy[room].append(session)

                clean_population.append(clean_individual)

            # Evaluate fitness of clean population
            population_with_fitness = [(individual, fitness(individual)) for individual in clean_population]
            population_with_fitness.sort(key=lambda x: x[1], reverse=True)

            sorted_population = [individual for individual, _ in population_with_fitness]

            # Create new population through selection, crossover, and mutation
            new_population = []
            while len(new_population) < self.population_size:
                parents = selection(sorted_population, [score for _, score in population_with_fitness])
                offspring1, offspring2 = crossover(parents[0], parents[1])

                offspring1 = mutate(offspring1, self.mutation_rate)
                offspring2 = mutate(offspring2, self.mutation_rate)

                new_population.extend([offspring1, offspring2])

            population = new_population

        best_individual = sorted_population[0]
        return best_individual

        
def calculate_mape(actual_values, predicted_values):
    """Calculate MAPE."""
    actual_values = np.array(actual_values)
    predicted_values = np.array(predicted_values)
    epsilon = 1e-10
    actual_values = np.where(actual_values == 0, epsilon, actual_values)

    return np.mean(np.abs((actual_values - predicted_values) / actual_values)) * 100


def calculate_rmse(actual_values, predicted_values):
    """Calculate RMSE."""
    actual_values = np.array(actual_values)
    predicted_values = np.array(predicted_values)
    return np.sqrt(np.mean((predicted_values - actual_values) ** 2))


def calculate_accuracy(total_assignments, correct_assignments):
    """Calculate accuracy."""
    return (correct_assignments / total_assignments) * 100


def evaluate_individual(individual_schedule):
    """Evaluate an individual schedule based on MAPE, RMSE, and Accuracy."""
    total_sessions = len(individual_schedule)
    correct_assignments = 0
    actual_values = []
    predicted_values = []
    session_occupancy = defaultdict(list)

    for session in individual_schedule:
        subject = session['subject']
        assigned_room = session['room']
        days = session['days']
        timeslot = session['timeslot']

        # Check room assignment accuracy based on department and subject_tags
        department = subject.department.department_name
        room_correct = False

        if department == "COMPUTER STUDIES PROGRAM":
            room_correct = assigned_room in CSPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
        elif department == "ENGINEERING AND TECHNOLOGY PROGRAM":
            room_correct = assigned_room in ETPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
        elif department == "GENERAL DEPARTMENTS":
            room_correct = assigned_room in LectureRoom.objects.all()

        actual_values.append(1 if room_correct else 0)
        predicted_values.append(1 if assigned_room else 0)

        # Check timeslot conflicts
        if not has_conflict(session_occupancy[assigned_room], timeslot, days) and room_correct:
            correct_assignments += 1
            # Append a dictionary instead of a tuple
            session_occupancy[assigned_room].append({
                'timeslot': timeslot,
                'days': days
            })

    mape = calculate_mape(actual_values, predicted_values)
    rmse = calculate_rmse(actual_values, predicted_values)
    accuracy = calculate_accuracy(total_sessions, correct_assignments)

    return mape, rmse, accuracy







                            
                            
                            
                            

                            

                            


                    


    
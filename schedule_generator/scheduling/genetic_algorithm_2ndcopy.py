from collections import defaultdict
import random
from datetime import datetime
from .models import *
import numpy as np
from math import sqrt
from django.db.models import Q


# Helper functions


def parse_timeslot(timeslot):
    """
    Parses a timeslot string (e.g., "12:30PM - 03:00PM") into start and end time objects.
    """
    start_str, end_str = timeslot.split(" - ")
    start_time = datetime.strptime(start_str.strip(), "%I:%M%p").time()
    end_time = datetime.strptime(end_str.strip(), "%I:%M%p").time()
    return start_time, end_time

def parse_days(days):
    """
    Parses a days string (e.g., "M / TH") into a set of individual days (e.g., {"M", "TH"}).
    """
    return {day.strip() for day in days.split(" / ")}

def timeslot_overlap(start1, end1, start2, end2):
    """
    Determines if two timeslots overlap.
    Returns True if there is any intersection between the two timeslots.
    """
    return max(start1, start2) < min(end1, end2)

def has_conflict(existing_sessions, new_timeslot, new_days):
    """
    Checks if a new session has any conflicts with existing sessions based on time and days.
    - Conflict exists if the new session overlaps in time with an existing session on any common day.
    """
    new_start, new_end = parse_timeslot(new_timeslot)
    new_days_set = parse_days(new_days)

    for session in existing_sessions:
        session_start, session_end = parse_timeslot(session['timeslot'])
        session_days_set = parse_days(session['days'])

        # Check for overlapping days and times
        if new_days_set & session_days_set:  # Common days exist
            if timeslot_overlap(new_start, new_end, session_start, session_end):
                return True  # Conflict detected
    return False



def initialize_population(population_size):
    population = []
    session_occupancy = defaultdict(list)  # Global room occupancy keyed by room_id

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
                for _ in range(20):
                    new_room = random.choice(available_rooms)

                    # Check for conflicts in the selected room
                    room_id = new_room.room_id  # Use room_id as the global key
                    if not has_conflict(session_occupancy[room_id], timeslot, days):
                        session = {
                            'section': section,
                            'subject': subject,
                            'room': room_id,
                            'days': days,
                            'timeslot': timeslot,
                            'starttime': starttime,
                            'requires_laboratory': requires_laboratory,
                        }
                        individual_schedule.append(session)
                        session_occupancy[room_id].append(session)  # Add to global occupancy
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
        session_occupancy = defaultdict(list)  # Global session occupancy keyed by room_id

    if random.random() < mutation_rate:
        index = random.randint(0, len(individual) - 1)  # Choose a random session to mutate
        session = individual[index]

        subject = session.get('subject')
        if subject is None:
            return individual  # Skip mutation if the subject is missing
        
        days = session['days']
        timeslot = session['timeslot']
        default_room_id = session['room']  # Default to current room if mutation fails

        available_rooms = Room.objects.none()
        department_name = subject.department.department_name
        requires_laboratory = subject.requires_laboratory

        sub_name = subject.subject_name.strip().lower()

        # Select available rooms based on department and requirements
        if department_name == "COMPUTER STUDIES PROGRAM":
            if requires_laboratory:
                available_rooms = CSPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
                if not available_rooms.exists():
                    available_rooms = CSPRoom.objects.filter(subject_tags__subject_name__icontains=sub_name)
            else:
                available_rooms = LectureRoom.objects.all()
        elif department_name == "ENGINEERING AND TECHNOLOGY PROGRAM":
            if requires_laboratory:
                available_rooms = ETPRoom.objects.filter(subject_tags__subject_name__iexact=subject.subject_name)
                if not available_rooms.exists():
                    available_rooms = ETPRoom.objects.filter(subject_tags__subject_name__icontains=sub_name)
            else:
                available_rooms = LectureRoom.objects.all()
        elif department_name == "GENERAL DEPARTMENTS":
            available_rooms = LectureRoom.objects.all()
        else:
            print(f"Skipping mutation for subject {subject.subject_name} due to unrecognized department: {department_name}")
            return individual

        if not available_rooms.exists():
            print(f"Skipping mutation for subject {subject.subject_name} due to lack of available rooms.")
            return individual

        # Attempt to find a new room without conflicts
        room_found = False
        max_attempts = 10
        for _ in range(max_attempts):
            new_room = random.choice(available_rooms)
            new_room_id = new_room.room_id  # Use room_id as the global identifier

            # Check for conflicts in the selected room
            if not has_conflict(session_occupancy[new_room_id], timeslot, days):
                session['room'] = new_room_id  # Assign the new room
                session_occupancy[new_room_id].append(session)  # Update global occupancy
                room_found = True
                break

        # If no suitable room is found, retain the original room
        if not room_found:
            session['room'] = default_room_id

    return individual


class GeneticAlgorithm:
    def __init__(self, population_size=100, generations=50, mutation_rate=0.01):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def run(self):
        population = initialize_population(self.population_size)

        for _ in range(self.generations):
            # Evaluate fitness of each individual
            population_with_fitness = [(individual, fitness(individual)) for individual in population]
            population_with_fitness.sort(key=lambda x: x[1], reverse=True)

            sorted_population = [individual for individual, _ in population_with_fitness]

            new_population = []
            while len(new_population) < self.population_size:
                # Select parents using selection
                parents = selection(sorted_population, [score for _, score in population_with_fitness])

                # Generate offspring using crossover
                offspring1, offspring2 = crossover(parents[0], parents[1])

                # Apply mutation to offspring
                offspring1 = mutate(offspring1, self.mutation_rate)
                offspring2 = mutate(offspring2, self.mutation_rate)

                new_population.extend([offspring1, offspring2])

            population = new_population[:self.population_size]  # Ensure population size remains constant

        best_individual = max(population, key=fitness)
        return best_individual
        

def has_conflict_evaluate(current_sessions, new_session):
    """
    Checks if a new session conflicts with existing sessions in a room.
    """
    new_timeslot = new_session['timeslot']
    new_days = new_session['days']

    # Compare with all current sessions in the same room
    return any(
        has_conflict([session], new_timeslot, new_days)
        for session in current_sessions
    )


def time_overlap(session1, session2):
    """
    Checks if two sessions have overlapping times on the same day.
    """
    start1, end1 = parse_timeslot(session1['timeslot'])
    start2, end2 = parse_timeslot(session2['timeslot'])
    days1 = parse_days(session1['days'])
    days2 = parse_days(session2['days'])

    # Check for overlapping days and times
    if days1 & days2:  # If there are shared days
        return timeslot_overlap(start1, end1, start2, end2)
    return False


def calculate_rmse_from_conflicts(population):
    """
    Calculate RMSE based on conflict counts for each individual in the population.
    This uses logic similar to the old function for stability.
    """
    conflict_counts = []

    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0

        for session in individual:
            room = session['room']
            parsed_timeslot = parse_timeslot(session['timeslot'])  # Should return a tuple (start, end)
            parsed_days = set(parse_days(session['days']))

            # Check for conflicts in the same room
            for occupied_timeslot, occupied_days in session_occupancy[room]:
                if parsed_days & occupied_days and timeslot_overlap(
                    parsed_timeslot[0], parsed_timeslot[1],
                    occupied_timeslot[0], occupied_timeslot[1]
                ):
                    conflicts += 1
                    break  # Stop checking once a conflict is found

            # Add this session to the room occupancy
            session_occupancy[room].append((parsed_timeslot, parsed_days))

        # Record the conflict count for this individual
        conflict_counts.append(conflicts)

    # Calculate RMSE based on the conflicts across all individuals
    return np.sqrt(np.mean(np.square(conflict_counts)))


def calculate_conflict_free_rate(total_sessions, conflicting_sessions):
    """
    Calculate the percentage of sessions without conflicts.
    Conflicting sessions are sessions with overlapping timeslot days in the same room.
    """
    conflict_free_sessions = total_sessions - conflicting_sessions
    return (conflict_free_sessions / total_sessions) * 100


def calculate_room_assignment_validity(total_sessions, correct_room_assignments):
    """
    Calculate the percentage of correct room assignments based on department-specific rules.
    """
    return (correct_room_assignments / total_sessions) * 100


def calculate_accuracy(total_sessions, conflicting_sessions, incorrect_assignments):
    """
    Calculate the overall accuracy, factoring in conflicts and misassignments.
    Accuracy = (1 - (conflicts + misassignments) / total_sessions) * 100.
    """
    total_issues = conflicting_sessions + incorrect_assignments
    return ((total_sessions - total_issues) / total_sessions) * 100


def evaluate_individual(individual_schedule):
    """
    Evaluate an individual schedule based on conflicts, room assignment validity, overall correctness, and RMSE.
    """
    total_sessions = len(individual_schedule)
    conflicting_sessions = 0
    correct_room_assignments = 0
    incorrect_assignments = 0
    session_occupancy = defaultdict(list)  # Global room occupancy keyed by room_id

    for session in individual_schedule:
        subject = session['subject']
        assigned_room_id = session['room']
        days = session['days']
        timeslot = session['timeslot']

        department_name = subject.department.department_name
        requires_lab = subject.requires_laboratory

        # Determine the expected rooms based on department and lab requirements
        if department_name == "COMPUTER STUDIES PROGRAM":
            if requires_lab:
                expected_rooms = CSPRoom.objects.filter(
                    subject_tags__subject_name__iexact=subject.subject_name
                ).values_list("room_id", flat=True)
            else:
                expected_rooms = LectureRoom.objects.values_list("room_id", flat=True)
        elif department_name == "ENGINEERING AND TECHNOLOGY PROGRAM":
            if requires_lab:
                expected_rooms = ETPRoom.objects.filter(
                    subject_tags__subject_name__iexact=subject.subject_name
                ).values_list("room_id", flat=True)
            else:
                expected_rooms = LectureRoom.objects.values_list("room_id", flat=True)
        elif department_name == "GENERAL DEPARTMENTS":
            expected_rooms = LectureRoom.objects.values_list("room_id", flat=True)
        else:
            expected_rooms = []

        # Validate the room assignment
        if assigned_room_id in expected_rooms:
            if requires_lab:
                # Ensure the assigned room is a laboratory when required
                is_lab = CSPRoom.objects.filter(room_id=assigned_room_id).exists() or \
                         ETPRoom.objects.filter(room_id=assigned_room_id).exists()
                if is_lab:
                    correct_room_assignments += 1
                else:
                    incorrect_assignments += 1
            else:
                correct_room_assignments += 1
        else:
            incorrect_assignments += 1

        # Check for conflicts
        current_room_sessions = session_occupancy[assigned_room_id]
        new_session = {'timeslot': timeslot, 'days': days}

        if has_conflict(current_room_sessions, timeslot, days):
            print(f"Conflict found with session: {new_session}")
            conflicting_sessions += 1
        else:
            session_occupancy[assigned_room_id].append(new_session)

    # Calculate evaluation metrics
    population = [individual_schedule]  # Single individual wrapped in a list
    rmse = calculate_rmse_from_conflicts(population)
    conflict_free_rate = calculate_conflict_free_rate(total_sessions, conflicting_sessions)
    room_assignment_validity = calculate_room_assignment_validity(total_sessions, correct_room_assignments)
    accuracy = calculate_accuracy(total_sessions, conflicting_sessions, incorrect_assignments)

    # Format metrics to two decimal places
    rmse = round(rmse, 4)
    conflict_free_rate = round(conflict_free_rate, 2)
    room_assignment_validity = round(room_assignment_validity, 2)
    accuracy = round(accuracy, 2)

    return {
        "RMSE": rmse,
        "Conflict-Free Rate": conflict_free_rate,
        "Room Assignment Validity": room_assignment_validity,
        "Accuracy": accuracy,
    }



                            
                            
                            
                            

                            

                            


                    


    
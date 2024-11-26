from collections import defaultdict
import random
from datetime import datetime, time
from .models import *
import numpy as np
from math import sqrt
from django.db.models import Q


# Helper functions


def parse_timeslot(timeslot_str):
    """
    Parses a timeslot string (e.g., "09:00AM - 10:30AM") into a tuple of start and end times.
    """
    if " - " not in timeslot_str:
        raise ValueError(f"Invalid timeslot format: {timeslot_str}")
    
    try:
        start_time_str, end_time_str = timeslot_str.split(" - ")
        return start_time_str.strip(), end_time_str.strip()
    except ValueError:
        raise ValueError(f"Timeslot string is malformed: {timeslot_str}")


def parse_days(days_str):
    """
    Parses the days string (e.g., "M / TH" or "W") into a set of days.
    """
    return set(day.strip() for day in days_str.split('/') if day.strip())


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



def has_conflict(room_schedule, timeslot, days_str):
    """
    Checks if a conflict exists for the given room's schedule, timeslot, and days string.
    """
    days = parse_days(days_str)  # Convert to a set
    for entry in room_schedule:
        entry_days = parse_days(entry.get('days', ''))  # Parse stored days string
        entry_timeslot = entry.get('timeslot')

        if entry_days and timeslot_overlap(entry_timeslot, timeslot) and days & entry_days:
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




def is_within_allowed_time(timeslot, allowed_start, allowed_end):
    """
    Checks if a timeslot is within the allowed time range.

    Args:
        timeslot (tuple): A tuple containing the start and end times as strings (e.g., ("09:00AM", "10:30AM")).
        allowed_start (str): The allowed start time as a string (e.g., "08:00AM").
        allowed_end (str): The allowed end time as a string (e.g., "06:00PM").

    Returns:
        bool: True if the timeslot is within the allowed time range, False otherwise.

    Raises:
        ValueError: If any of the time strings have an invalid format.
    """
    # Helper function to parse time strings into datetime.time objects
    def parse_time_string(time_str):
        try:
            return datetime.strptime(time_str.strip(), "%I:%M%p").time()
        except ValueError as e:
            raise ValueError(f"Invalid time format '{time_str}': {e}")

    if not isinstance(timeslot, tuple) or len(timeslot) != 2:
        raise ValueError(f"Invalid timeslot format: Expected a tuple with two strings, got {timeslot}")

    try:
        # Parse the timeslot and allowed times
        start_time, end_time = map(parse_time_string, timeslot)
        allowed_start_time = parse_time_string(allowed_start)
        allowed_end_time = parse_time_string(allowed_end)
    except ValueError as e:
        raise ValueError(f"Error parsing time strings: {e}")

    # Compare times
    return allowed_start_time <= start_time and end_time <= allowed_end_time



def initialize_population(population_size):
    population = []
    room_occupancy = defaultdict(list)  # Tracks room usage per timeslot and day

    # Fetch all sessions and prefetch related data
    sessions = MajorSession.objects.prefetch_related('section', 'timeslots', 'subject', 'department').all()

    for _ in range(population_size):
        individual_schedule = []

        for session in sessions:
            department = str(session.department.department_name)
            has_lab = session.subject.need_lab

            # Get available timeslots within allowed time
            available_timeslots = [
                timeslot for timeslot in session.timeslots.all()
                if is_within_allowed_time(
                    tuple(timeslot.timeslot.split(" - ")),  # Parse timeslot into start and end
                    "07:30AM", "09:00PM"
                )
            ]

            if not available_timeslots:
                print(f"No suitable timeslots found for subject {session.subject.subject_name}.")
                continue

            # Determine available rooms based on session attributes
            if department == "COMPUTER STUDIES PROGRAM" and has_lab:
                available_rooms = CSPRoom.objects.filter(subject_tags=session.subject)
                if not available_rooms.exists():
                    available_rooms = CSPRoom.objects.all()
            else:
                available_rooms = LectureRoom.objects.all()

            if not available_rooms.exists():
                print(f"No suitable rooms found for subject {session.subject.subject_name}.")
                continue

            # Loop through each section in the session
            for section in session.section.all():
                section_scheduled = False

                # Assign section to a room and timeslot
                for timeslot in available_timeslots:
                    rooms = list(available_rooms)
                    random.shuffle(rooms)  # Shuffle rooms to reduce bias

                    for room in rooms:
                        timeslot_days = parse_days(timeslot.days)

                        # Check if room is free for all days in the timeslot
                        if all(
                            not has_conflict(room_occupancy[room], timeslot.timeslot, day)
                            for day in timeslot_days
                        ):
                            # Assign room and timeslot to the section
                            session_entry = {
                                'section': section,
                                'subject': session.subject,
                                'room': room,
                                'days': timeslot.days,
                                'timeslot': timeslot.timeslot,
                            }
                            individual_schedule.append(session_entry)

                            # Mark room as occupied for each day in the timeslot
                            for day in timeslot_days:
                                room_occupancy[room].append({
                                    'timeslot': timeslot.timeslot,
                                    'day': day,
                                    'section': section,
                                })

                            section_scheduled = True
                            break

                    if section_scheduled:
                        break

                if not section_scheduled:
                    print(f"Could not assign a room for section {section} in subject {session.subject.subject_name}.")

        if not individual_schedule:
            print("Warning: Individual schedule is empty. Consider retrying or handling incomplete schedules.")
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

        start_time, end_time = parse_timeslot(timeslot)
        session_days = parse_days(days)

        # Check for conflicts with existing sessions in the room
        conflict = False
        for existing_timeslot, existing_days in session_occupancy[room]:
            existing_start, existing_end = parse_timeslot(existing_timeslot)
            overlap_days = session_days & parse_days(existing_days)

            if overlap_days and not (
                end_time <= existing_start or start_time >= existing_end
            ):
                fitness_score -= 10
                conflict = True
                break

        if not conflict:
            fitness_score += 5  # Reward conflict-free scheduling

        session_occupancy[room].append((timeslot, days))

    return fitness_score



def selection(population, fitness_scores, k=3):
    fitness_scores = [max(score, 0) for score in fitness_scores]  # Normalize scores
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
        # Select a random session to mutate
        index = random.randint(0, len(individual) - 1)
        session = individual[index]

        # Retrieve current session details
        days = session['days']
        timeslot = session['timeslot']
        current_room = session['room']
        subject = session['subject']

        # Fetch available rooms based on the session's subject tags
        available_rooms = CSPRoom.objects.filter(subject_tags=subject)
        if not available_rooms.exists():
            available_rooms = LectureRoom.objects.all()

        # Attempt to find a new room and timeslot that avoids conflicts
        room_found = False
        max_attempts = 20
        for _ in range(max_attempts):
            new_room = random.choice(available_rooms)

            if not any(
                has_conflict(session_occupancy[new_room], timeslot, day)
                for day in parse_days(days)
            ):
                # Assign the new room and update occupancy
                session['room'] = new_room
                session_occupancy[new_room].append({
                    'timeslot': timeslot,
                    'days': days,
                    'section': session['section'],
                })
                room_found = True
                break

        # If no valid room is found, retain the current room
        if not room_found:
            session['room'] = current_room

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

        

def calculate_rmse(population):
    conflict_counts = []

    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0

        for session in individual:
            room = session['room']
            timeslot = session['timeslot']
            days = parse_days(session['days'])

            for occupied_timeslot, occupied_days in session_occupancy[room]:
                if days & parse_days(occupied_days) and timeslot_overlap(parse_timeslot(timeslot), parse_timeslot(occupied_timeslot)):
                    conflicts += 1
                    break

            session_occupancy[room].append((timeslot, session['days']))

        conflict_counts.append(conflicts)

    return np.sqrt(np.mean(np.square(conflict_counts))) if conflict_counts else 0



def calculate_accuracy(population):
    accuracies = []

    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0
        total_sessions = len(individual)

        for session in individual:
            room = session['room']
            timeslot = session['timeslot']
            days = set(parse_days(session['days']))

            # Check for conflicts in the same room
            for occupied_timeslot, occupied_days in session_occupancy[room]:
                if days & set(parse_days(occupied_days)) and timeslot_overlap(parse_timeslot(timeslot), parse_timeslot(occupied_timeslot)):
                    conflicts += 1
                    break

            # Add this session to the room occupancy
            session_occupancy[room].append((timeslot, session['days']))

        # Calculate the number of conflict-free sessions
        conflict_free_sessions = max(total_sessions - conflicts, 0)
        individual_accuracy = conflict_free_sessions / total_sessions if total_sessions > 0 else 0
        accuracies.append(individual_accuracy)

    # Return average accuracy across the population in percentage
    return np.mean(accuracies) * 100 if accuracies else 0




def calculate_room_assignment_accuracy(population):
    correct_assignments = []

    for individual in population:
        individual_correct = 0
        total_sessions = len(individual)

        for session in individual:
            room = session['room']
            subject = session['subject']

            # Fetch requirements based on updated model attributes
            requires_laboratory = subject.need_lab
            if requires_laboratory and isinstance(room, CSPRoom):
                individual_correct += 1
            elif not requires_laboratory and isinstance(room, LectureRoom):
                individual_correct += 1

        accuracy = individual_correct / total_sessions if total_sessions > 0 else 0
        correct_assignments.append(accuracy)

    return np.mean(correct_assignments) * 100 if correct_assignments else 0    
          







                            
                            
                            
                            

                            

                            


                    


    
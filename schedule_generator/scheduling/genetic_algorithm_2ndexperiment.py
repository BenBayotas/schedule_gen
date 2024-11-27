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
    Parses a timeslot string (e.g., "03:30PM - 06:00PM") into a tuple of start and end times.
    If the input is already a tuple, it validates and returns it directly.
    """
    if isinstance(timeslot_str, tuple):  # Input is already a tuple
        if len(timeslot_str) != 2:
            raise ValueError(f"Invalid timeslot tuple: {timeslot_str}")
        return timeslot_str  # Return the tuple as is

    if " - " not in timeslot_str:  # Input is a string but not formatted correctly
        raise ValueError(f"Invalid timeslot format: {timeslot_str}")
    
    start_time_str, end_time_str = timeslot_str.split(" - ")
    return start_time_str.strip(), end_time_str.strip()


def parse_days(days_str):
    """
    Parses the days string (e.g., "M / TH") into a set of individual days.
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



def has_conflict(room_schedule, timeslot, days_str, exclude_section=None):
    """
    Checks if a conflict exists for the given room's schedule, timeslot, and days string.
    """
    # Parse the input days and timeslot
    parsed_days = parse_days(days_str)
    parsed_timeslot = parse_timeslot(timeslot)

    for entry in room_schedule:
        if isinstance(entry, dict):  # Ensure entry is a dictionary
            entry_days = parse_days(entry.get('days', ''))
            entry_timeslot = parse_timeslot(entry.get('timeslot', ''))
            entry_section = entry.get('section')

            # Skip the excluded section, if specified
            if exclude_section and entry_section == exclude_section:
                continue

            # Check for conflicts
            if entry_days and timeslot_overlap(entry_timeslot, parsed_timeslot) and parsed_days & entry_days:
                return True
        else:
            print(f"Invalid entry found in room_schedule: {entry}")
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
    """
    Checks if two timeslots overlap.

    Args:
        ts1, ts2 (tuple or str): Start and end times as tuples (e.g., ("09:00AM", "10:30AM")) or raw timeslot strings.

    Returns:
        bool: True if the timeslots overlap, False otherwise.

    Raises:
        ValueError: If the inputs are not properly formatted.
    """
    # Parse if inputs are strings
    if isinstance(ts1, str):
        ts1 = parse_timeslot(ts1)
    if isinstance(ts2, str):
        ts2 = parse_timeslot(ts2)

    # Validate input format
    if not (isinstance(ts1, tuple) and len(ts1) == 2 and isinstance(ts2, tuple) and len(ts2) == 2):
        raise ValueError(f"Invalid timeslot format: ts1={ts1}, ts2={ts2}. Expected tuples with two elements.")

    start1, end1 = ts1
    start2, end2 = ts2

    # Check for overlap
    return max(start1, start2) < min(end1, end2)




def is_within_allowed_time(timeslot, allowed_start, allowed_end):
    """
    Checks if a timeslot is within the allowed time range.

    Args:
        timeslot (tuple or str): A tuple containing the start and end times as strings (e.g., ("09:00AM", "10:30AM")),
                                 or a timeslot string (e.g., "09:00AM - 10:30AM").
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

    # Parse timeslot if provided as a string
    if isinstance(timeslot, str):
        timeslot = parse_timeslot(timeslot)  # Ensure it's a tuple

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
    global_room_occupancy = defaultdict(list)  # Tracks room usage per timeslot and day

    # Helper function to validate and append room schedule entries
    def add_room_schedule_entry(room, timeslot, day, section):
        if not isinstance(timeslot, tuple) or not isinstance(day, str) or not section:
            print(f"Invalid room schedule entry: timeslot={timeslot}, day={day}, section={section}")
            return

        entry = {  # Ensure this is properly scoped
            'timeslot': timeslot,
            'days': day,
            'section': section
        }
        global_room_occupancy[room].append(entry)

    # Fetch all sessions and prefetch related data
    sessions = MajorSession.objects.prefetch_related('section', 'timeslots', 'subject', 'department').all()

    for _ in range(population_size):
        individual_schedule = []
        session_assignments = defaultdict(lambda: defaultdict(list))  # Tracks per-session assignments for validation

        for session in sessions:
            department = str(session.department.department_name)
            has_lab = session.subject.need_lab

            # Get available timeslots within allowed time
            available_timeslots = [
                timeslot for timeslot in session.timeslots.all()
                if is_within_allowed_time(parse_timeslot(timeslot.timeslot), allowed_start="07:30AM", allowed_end="09:00PM")
            ]

            if not available_timeslots:
                print(f"No available timeslots for session {session.subject.subject_name}")
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

            for section in session.section.all():
                section_scheduled = False

                for timeslot in sorted(
                    available_timeslots,
                    key=lambda ts: len(global_room_occupancy.get(parse_timeslot(ts.timeslot), []))
                ):
                    parsed_timeslot = parse_timeslot(timeslot.timeslot)
                    timeslot_days = parse_days(timeslot.days)
                    rooms = list(available_rooms)
                    random.shuffle(rooms)

                    for room in rooms:
                        if all(
                            not has_conflict(global_room_occupancy[room], parsed_timeslot, day)
                            for day in timeslot_days
                        ):
                            if any(
                                has_conflict(session_assignments[section], parsed_timeslot, day)
                                for day in timeslot_days
                            ):
                                continue

                            if any(
                                has_conflict(global_room_occupancy[room], parsed_timeslot, day, exclude_section=section)
                                for day in timeslot_days
                            ):
                                continue

                            session_entry = {
                                'section': section,
                                'subject': session.subject,
                                'room': room,
                                'days': timeslot.days,
                                'timeslot': parsed_timeslot,
                            }
                            individual_schedule.append(session_entry)

                            for day in timeslot_days:
                                add_room_schedule_entry(room, parsed_timeslot, day, section)
                                session_assignments[section][day].append(parsed_timeslot)

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
          







                            
                            
                            
                            

                            

                            


                    


    
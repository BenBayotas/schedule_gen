from collections import defaultdict
import random
from datetime import datetime, time
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


def is_within_allowed_time(timeslot_str, start, end):
    """
    Checks if a timeslot string falls within a given start and end time.

    Args:
        timeslot_str (str): Timeslot string in the format "09:00AM - 11:30AM".
        start (datetime.time): Earliest allowed time.
        end (datetime.time): Latest allowed time.

    Returns:
        bool: True if the timeslot is within the allowed time range.
    """
    timeslot_start, timeslot_end = parse_timeslot(timeslot_str)
    return timeslot_start >= start and timeslot_end <= end





def initialize_population(population_size):

    population = []
    room_occupancy = defaultdict(list)  # Tracks room usage per timeslot and day

    # Fetch all sessions and prefetch related data
    sessions = Session.objects.prefetch_related('section', 'timeslots', 'subject', 'course', 'department').all()


    for _ in range(population_size):
        individual_schedule = []

        for session in sessions:

            department = str(session.department.department_name)

            # Filter and parse timeslots manually
            available_timeslots = [
                timeslot for timeslot in session.timeslots.all()
                if is_within_allowed_time(timeslot.timeslot, start=time(7, 30), end=time(21, 0))
            ]

            if department == "COMPUTER STUDIES PROGRAM":
                available_rooms = CSPRoom.objects.filter(subject_tags=session.subject)

            if not available_rooms.exists():
                print(f"No suitable rooms found for subject {session.subject.subject_name}.")
                continue

            # Loop through each section in the session
            for section in session.section.all():
                section_scheduled = False

                # Try to assign the section to a room and timeslot
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

        start_time, _ = parse_timeslot(timeslot)
        session_days = parse_days(days)

        # Check for conflicts
        for existing_timeslot, existing_days in session_occupancy[room]:
            if session_days & parse_days(existing_days):
                fitness_score -= 10
                break
        else:
            fitness_score += 5

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

        # Fetch available rooms based on the session's subject tags
        available_rooms = CSPRoom.objects.filter(subject_tags=session['subject'])
        if not available_rooms.exists():
            return individual  # No valid rooms to mutate, return unchanged

        # Attempt to find a new room and timeslot that avoids conflicts
        room_found = False
        max_attempts = 20
        for _ in range(max_attempts):
            new_room = random.choice(available_rooms)

            if not has_conflict(session_occupancy[new_room], timeslot, days):
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

        

def calculate_rmse(population):
    conflict_counts = []

    for individual in population:
        session_occupancy = defaultdict(list)
        conflicts = 0

        for session in individual:
            room = session['room']
            parsed_timeslot = parse_timeslot(session['timeslot'])
            parsed_days = parse_days(session['days'])

            for occupied_timeslot, occupied_days in session_occupancy[room]:
                if parsed_days & parse_days(occupied_days) and timeslot_overlap(parsed_timeslot, occupied_timeslot):
                    conflicts += 1
                    break

            session_occupancy[room].append((parsed_timeslot, parsed_days))

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
            parsed_timeslot = parse_timeslot(session['timeslot'])
            parsed_days = set(parse_days(session['days']))

            # Check for conflicts in the same room
            for occupied_timeslot, occupied_days in session_occupancy[room]:
                if parsed_days & occupied_days and timeslot_overlap(parsed_timeslot, occupied_timeslot):
                    conflicts += 1
                    break  # Stop checking once a conflict is found

            # Add this session to the room occupancy
            session_occupancy[room].append((parsed_timeslot, parsed_days))

        # Calculate the number of conflict-free sessions
        conflict_free_sessions = max(total_sessions - conflicts, 0)
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
          







                            
                            
                            
                            

                            

                            


                    


    
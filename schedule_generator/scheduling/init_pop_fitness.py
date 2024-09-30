from collections import defaultdict
import random
from .models import Department, Course, Section, Subject, Instructor, Room, TimeSlot


def initialize_population(population_size):
    population = []
    
    departments = Department.objects.all()
    
    for _ in range(population_size):
        individual_schedule = []
        
        # Dictionary to track room usage per timeslot
        room_timeslot_usage = defaultdict(list)
        
        # Dictionary to track instructor subject handling
        instructor_subject_count = defaultdict(int)
        
        # Dictionary to track instructor session count per day
        instructor_daily_sessions = defaultdict(lambda: defaultdict(int))


        # Iterate over departments
        for department in departments:
            courses = department.course_set.all()
            

            for course in courses:
                # Iterate over year levels (1-4) for each course

                for year_level in range(1, 5):  # Assuming a 4-year course structure
                    
                    sections = Section.objects.filter(course=course, year_level=year_level)
                    subjects = Subject.objects.filter(course=course, year_level=year_level)
                    
                    for section in sections:
                        
                        # For each section, assign the subjects from the corresponding year level
                        for subject in subjects:
                            
                            valid_timeslot_found = False
                            max_attempts = 10  # Limit the attempts to prevent infinite loops
                            
                            for _ in range(max_attempts):
                                
                                timeslot = random.choice(TimeSlot.objects.filter(department=department))
                                room = random.choice(Room.objects.all())
                                instructor = random.choice(Instructor.objects.filter(expertise=subject))

                                # Check constraints:
                                # 1. Room should not be booked in the same timeslot
                                if room not in room_timeslot_usage[timeslot]:
                                    # 2. Instructor should handle a maximum of 3 subjects
                                    if instructor_subject_count[instructor] < 3:
                                        # 3. Instructor should not exceed 2 sessions per day
                                        if instructor_daily_sessions[instructor][timeslot.days] < 2:
                                            # Add session if all constraints are satisfied
                                            session = {
                                                'subject': subject,
                                                'timeslot': timeslot,
                                                'room': room,
                                                'instructor': instructor,
                                                'section': section
                                            }
                                            individual_schedule.append(session)
                                            
                                            # Update room usage, instructor subject count, and daily session count
                                            room_timeslot_usage[timeslot].append(room)
                                            instructor_subject_count[instructor] += 1
                                            instructor_daily_sessions[instructor][timeslot.days] += 1

                                            valid_timeslot_found = True
                                            break  # Exit loop if a valid timeslot is found
                            
                            # If a valid timeslot wasn't found after max_attempts, skip this session
                            if not valid_timeslot_found:
                                continue

        population.append(individual_schedule)
    
    return population          
          

def fitness(individual_schedule):
    """
    Evaluates the fitness of a schedule based on the following constraints:
    - No two departments, course sections, and subjects can have the same room in the same timeslot
    - Instructors can handle a maximum of 3 subjects
    - Instructors can have a maximum of 2 sessions per day
    """

    fitness_score = 100  # Start with a high fitness score and subtract for each violation

    # Dictionary to track room usage per timeslot
    room_timeslot_usage = defaultdict(list)

    # Dictionary to track instructor subject handling
    instructor_subject_count = defaultdict(int)

    # Dictionary to track instructor session count per day
    instructor_daily_sessions = defaultdict(lambda: defaultdict(int))

    # Loop through the individual schedule
    for session in individual_schedule:
        room = session['room']
        timeslot = session['timeslot']
        instructor = session['instructor']
        days = timeslot.days

        # Check for room conflicts in the same timeslot (department, section, subject)
        if room in room_timeslot_usage[timeslot]:
            fitness_score -= 10  # Room conflict in the same timeslot
        else:
            room_timeslot_usage[timeslot].append(room)

        # Check for instructor handling more than 3 subjects
        instructor_subject_count[instructor] += 1
        if instructor_subject_count[instructor] > 3:
            fitness_score -= 10  # Instructor handling more than 3 subjects

        # Check for instructor exceeding 2 sessions per day
        instructor_daily_sessions[instructor][days] += 1
        if instructor_daily_sessions[instructor][days] > 2:
            fitness_score -= 10  # Instructor exceeding 2 sessions per day

    return fitness_score

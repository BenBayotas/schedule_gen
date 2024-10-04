from collections import defaultdict
import random
from .models import Department, Course, Section, Subject, Instructor, Room, Timeslot

def initialize_population(population_size):
  population = []

  departments = Department.objects.all()
    
  for _ in range(population_size):
    individual_schedule = []
    room_timeslot_usage = defaultdict(list)
    instructor_subject_count = defaultdict(int)
    instructor_daily_session = defaultdict(lambda: defaultdict(int))
    
    for department in departments:
      courses = department.course_set.all()
      
      for course in courses:
        for year_level in range(1,5):
          
          sections = Section.objects.filter(course=course, year_level=year_level)
          subjects = Subject.objects.filter(course=course, year_level=year_level)
          
          for section in sections:
            for subject in subjects:
              
              valid_timeslot_found = False
              max_attempts = 10
              
              for _ range(max_attempts):
                timeslot = random.choice(Timeslot.objects.all())
                room = random.choice(Room.objects.all())
                instructor = random.choice(Instructor.objects.filter(expertise=subject))
                if room not in room_timeslot_usage[timeslot]:
                  if instructor_subject_count[instructor] < 3:
                    if instructor_daily_sessions[instructor][timeslot.days] < 2:
                      session = {
                        'subject': subject,
                        'timeslot': timeslot,
                        'room': room,
                        'instructor': instructor,
                        'section': section,
                      }
                      individual_schedule.append(session)
                      room_timeslot_usage[timeslot].append(room)
                      instructor_subject_count[instructor] += 1
                      instructor_daily_sessions[instructor][timeslot.day] += 1

                      valid_timeslot_found = True
                      break
            if not valid_timeslot_found:
              continue
    population.append(individual_schedule)                  
  return population            
          

def fitness(individual_schedule):
  fitness_score = 100
  
  room_timeslot_usage = defaultdict(list)
  instructor_subject_count = defaultdict(int)
  instructor_daily_sessions = defaultdict(lambda: defaultdict(int))

  for session in individual_schedule:
    room = session['room']
    timeslot = session['timeslot']
    instructor = session['instructor']
    day = timeslot.day

    if room in room_timeslot_usage[timeslot]:
      fitness_score -= 10
    else:
      room_timeslot_usage[timeslot].append(room)
      
    instructor_subject_count[instructor] += 1
    if instructor_subject_count[instructor] > 3:
      fitness_score -= 10
    
    instructor_daily_sessions[instructor][day] += 1
    if instructor_daily_sessions[instructor][day] > 2:
      fitness_score -= 10
  return fitness_score  
    

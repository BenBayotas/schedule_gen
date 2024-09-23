from django.shortcuts import render
from django.shortcuts import render
from .models import Department, Course, Section, Subject, Instructor, Room, TimeSlot
from .genetic_algo import GeneticAlgorithm

def generate_schedule(request):
    departments = Department.objects.all()
    courses = Course.objects.all()
    sections = Section.objects.all()
    subjects = Subject.objects.all()
    instructors = Instructor.objects.all()
    rooms = Room.objects.all()
    timeslots = TimeSlot.objects.all()

    # Instantiate and run the genetic algorithm
    ga = GeneticAlgorithm(population_size=20, generations=100, mutation_rate=0.05)
    initial_population = ga.initialize_population(departments, courses, sections, subjects, instructors, rooms, timeslots)
    best_schedule = ga.run(initial_population, instructors, rooms, timeslots)

    return render(request, 'schedule.html', {'schedule': best_schedule})
# Create your views here.

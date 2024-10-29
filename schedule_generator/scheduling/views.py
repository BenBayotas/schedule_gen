from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .genetic_algorithm1 import GeneticAlgorithm
from .forms import *


# Create your views here.

def home(request):
    return render(request, 'home.html')


def department_form_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            
            return render(request, 'department_form.html', {'form': form, 'saved': True})
        else:
            
            return render(request, 'department_form.html', {'form': form})
    else:
        form = DepartmentForm()
        return render(request, 'department_form.html', {'form': form})



def course_form_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()

            return render(request, 'course_form.html', {'form': form, 'saved': True})
        else:
           return render(request, 'course_form.html', {'form': form}) 
    
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})


def section_form_view(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'section_form.html', {'form': form, 'saved': True})
        else:
           return render(request, 'section_form.html', {'form': form}) 
    
    else:
        form = SectionForm()
    return render(request, 'section_form.html', {'form': form})



def subject_form_view(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'subject_form.html', {'form': form, 'saved':True})
        else:
            return render(request, 'subject_form.html', {'form': form})
    else:
        form = SubjectForm()
    return render(request, 'subject_form.html', {'form': form})


def room_form_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'room_form.html', {'form': form, 'saved': True})
        else:
            return render(request, 'room_form.html', {'form': form})
    else:
        form = RoomForm()
    return render(request, 'room_form.html', {'form': form})       

           
        
def schedule_view(request):

    best_schedule = None

    ga = GeneticAlgorithm(population_size=100)
    best_schedule = ga.run()

    context = {
        'schedule': best_schedule
    }

    return render(request, 'scheduletest.html', context)



    '''
        if request.method == "POST":

        ga = GeneticAlgorithm(population_size=100)
        best_schedule = ga.run()

        schedule_data = {}
        for room in best_schedule["rooms"]:
            schedule_data[room] = {}
            for session in best_schedule["sessions"]:

                room = session["room"]
                timeslot = session["timeslot"]

                if session["room"] == room:
                    start_time = session["timeslot"].start_time.strftime("%I:%M %p")
                    end_time = session["timeslot"].end_time.strftime("%I:%M %p")
                    schedule_data[room][(start_time, end_time)] = session

        return JsonResponse(schedule_data)
    return render(request, 'schedule.html')
    
    
    '''
    
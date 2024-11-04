from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .genetic_algorithm import GeneticAlgorithm
from .forms import *
from django.urls import reverse


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
    
    ga = GeneticAlgorithm(population_size=100)
    best_schedule = ga.run()

    
     
    formatted_schedule = []
    for session in best_schedule:
        
        if isinstance(session['timeslot'], str):
            timeslot = session['timeslot']
        else:
            timeslot = f"{session['timeslot'].start_time.strftime('%I:%M %p')} - {session['timeslot'].end_time.strftime('%I:%M %p')}"
        
        formatted_schedule.append({
            'room': session['room'].room_id,
            'section': getattr(session['section'], 'name', session['section']),  
            'subject': getattr(session['subject'], 'subject_name', session['subject']),
            'timeslot': timeslot,
            'days': session['days']
        })

    
    def room_sort_key(session):
        room = session['room']
        if room.startswith("CB"):
            return (0, room)
        elif room.startswith("CBS"):
            return (1, room)
        elif room.startswith("CBE"):
            return (2, room)
        else:
            return (3, room)

    
    formatted_schedule.sort(key=room_sort_key)

    
    context = {
        'schedule': formatted_schedule
    }

    return render(request, 'scheduletest.html', context)



def generate_schedule(request):


    if request.method == 'POST':
        # Run the genetic algorithm
        ga = GeneticAlgorithm()
        best_schedule = ga.run()

        # Extract individual sessions and format them for the template
        sessions = []
        for session in best_schedule:
            sessions.append({
                'course': session['section'].course.name,
                'section': session['section'].name,
                'subject_id': session['subject'].subject_id,
                'room': session['room'].room_name,
                'days': session['days'],
                'start_time': session['timeslot'].split('-')[0].strip(),
                'end_time': session['timeslot'].split('-')[1].strip()
            })

        # Redirect to the grid view with session data
        request.session['sessions'] = sessions  # Store sessions in Django session
        return redirect(reverse('display_schedule'))  # URL pattern for schedule display page

    return render(request, 'generate_schedule.html')  # Button template


def display_schedule(request):
    # Retrieve sessions from the session
    sessions = request.session.get('sessions', [])

    return render(request, 'schedule_grid.html', {'sessions': sessions})
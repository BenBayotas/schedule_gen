from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .genetic_algorithm import GeneticAlgorithm
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

           
        


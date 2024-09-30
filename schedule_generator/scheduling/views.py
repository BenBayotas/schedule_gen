from django.shortcuts import render
from django.http import JsonResponse
from .genetic_algorithm import GeneticAlgorithm


# Create your views here.

def schedule_view(request):
    
   if request.method == 'POST'

        ga = GeneticAlgorithm(population_size=50, generations=100, mutation_rate=0.01)
        best_schedule = ga.evolve()

        return JsonResponse({'schedule': best_schedule})
    return render(request, 'schedule.html')

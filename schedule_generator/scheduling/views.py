from django.shortcuts import render
from django.http import JsonResponse
from .init_pop_fitness import GeneticAlgorithm


# Create your views here.

def schedule_view(request):
    
   if request.method == 'POST':

        ga = GeneticAlgorithm(population_size=100, generations=50)
        best_schedule = ga.run()

        return JsonResponse({'schedule': best_schedule})
   return render(request, 'schedule.html')

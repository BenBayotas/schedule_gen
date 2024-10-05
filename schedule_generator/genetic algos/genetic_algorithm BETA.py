import random
from .models import Department, Room
from .init_pop_fitness import initialize_population, fitness

class GeneticAlgorithm:
  
  def __init__(self, population_size=50, generations=100, mutation_rate=0.01):
    self.population_size = population_size
    self.generations = generations
    self.mutation_rate = mutation_rate
    self.population = initialize_population(population_size)


  def evolve(self):
    for generation in range(self.generations):
      fitness_scores = [(individual, fitness(individual)) for individual in self.population]
      fitness_scores.sort(key=lambda x: x[1], reverse=True)

      top_half = [individual for individual, score in fitness_scores[:len(fitness_scores)//2]]
      
      new_population = self.crossover_and_mutate(top_half)

      self.population = new_population
    best_individual = sorted(self.population, key=lambda x: fitness(x), reverse=True)[0]
    return best_individual



  def crossover_and_mutate(self, selected_population):
    new_population = selected_population.copy()

    while len(new_population) < self.population_size:
      parent1 = random.choice(selected_population)
      parent2 = random.choice(selected_population)

      crossover_point = random.randint(0, len(parent1) - 1)
      child = parent1[:crossover_point] + parent2[crossover_point:]

      if random.random() < self.mutation_rate:
        child = self.mutate(child)

      new_population.append(child)
    return new_population

  def mutate(self, individual):
    mutated_individual = individual.copy()
    index_to_mutate = random.randint(0, len(mutated_individual) - 1)

    department = mutated_individual[index_to_mutate]['section'].course.department
    mutated_individual[index_to_mutate]['timeslot'] = random.choice(Timeslot.objects.filter(department=department)) # TO BE REVIEWED
    mutated_individual[index_to_mutate]['room'] = random.choice(Room.objects.all())

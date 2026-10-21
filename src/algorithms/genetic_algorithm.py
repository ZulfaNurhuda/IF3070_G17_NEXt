import random
from collections.abc import Sequence
from dataclasses import dataclass

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.evaluator import place_in_order
from src.core.initial import random_state
from src.core.models import Placement, Problem, State, VehicleId
from src.core.neighbors import random_successor


def select_parent(
    population: Sequence[State], fitness: Sequence[float], rng: random.Random
) -> State:
    if not population or len(population) != len(fitness):
        raise ValueError("population dan fitness harus sama-sama tidak kosong dan sejajar")
    offset = min(0.0, *fitness)
    weights = [value - offset for value in fitness]
    if sum(weights) == 0:
        return rng.choice(population)
    return rng.choices(population, weights=weights, k=1)[0]


def crossover(first: State, second: State, problem: Problem, rng: random.Random) -> State:
    crossover_point = rng.randrange(len(problem.vehicles) + 1)
    genes: list[tuple[VehicleId, Placement]] = []
    for index, vehicle in enumerate(problem.vehicles):
        placement = (first if index < crossover_point else second).placements[vehicle.id]
        if placement is not None:
            genes.append((vehicle.id, placement))
    return place_in_order(problem, genes)


def mutate(state: State, problem: Problem, rng: random.Random) -> State:
    successor = random_successor(state, problem, rng)
    return state if successor is None else successor[1]


@dataclass(frozen=True, slots=True)
class GeneticAlgorithm:
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.3
    elitism_count: int = 2

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        if self.population_size <= 0:
            raise ValueError("population_size harus positif")
        if self.generations < 0:
            raise ValueError("generations harus non-negatif")
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError("mutation_rate harus berada di antara 0 dan 1")
        if not 0 <= self.elitism_count <= self.population_size:
            raise ValueError("elitism_count harus berada di antara 0 dan population_size")

        population = [random_state(problem, rng) for _ in range(self.population_size)]
        fitness = [problem.value(state) for state in population]
        evaluations = len(population)
        initial_best = population[max(range(len(population)), key=lambda index: fitness[index])]
        previous_best = initial_best
        history = [
            HistoryRecord(
                iteration=0,
                value=max(fitness),
                maximum_value=max(fitness),
                average_value=sum(fitness) / len(fitness),
            )
        ]
        steps: list[Step] = []

        for generation in range(1, self.generations + 1):
            elite_indices = sorted(
                range(len(population)), key=lambda index: fitness[index], reverse=True
            )[: self.elitism_count]
            next_population = [population[index] for index in elite_indices]
            next_fitness = [fitness[index] for index in elite_indices]

            while len(next_population) < self.population_size:
                first_parent = select_parent(population, fitness, rng)
                second_parent = select_parent(population, fitness, rng)
                child = crossover(first_parent, second_parent, problem, rng)
                if rng.random() < self.mutation_rate:
                    child = mutate(child, problem, rng)
                next_population.append(child)
                next_fitness.append(problem.value(child))

            evaluations += len(next_population) - len(elite_indices)
            population, fitness = next_population, next_fitness
            best_index = max(range(len(population)), key=lambda index: fitness[index])
            current_best = population[best_index]
            maximum_value = fitness[best_index]
            history.append(
                HistoryRecord(
                    iteration=generation,
                    value=maximum_value,
                    maximum_value=maximum_value,
                    average_value=sum(fitness) / len(fitness),
                )
            )
            steps.append(Step(generation, previous_best.diff(current_best)))
            previous_best = current_best

        return SearchResult(
            initial_state=initial_best,
            final_state=previous_best,
            iterations=self.generations,
            evaluations=evaluations,
            history=tuple(history),
            steps=tuple(steps),
            extra={},
        )

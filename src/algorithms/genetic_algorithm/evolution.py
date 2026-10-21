import random
from collections.abc import Sequence
from dataclasses import dataclass

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.algorithms.genetic_algorithm.operators import (
    crossover,
    elite_indices,
    mutate,
    roulette_weights,
    select_parent,
)
from src.core.initial import random_state
from src.core.models import Problem, State


def best_index(fitness: Sequence[float]) -> int:
    return max(range(len(fitness)), key=fitness.__getitem__)


def generation_record(generation: int, fitness: Sequence[float]) -> HistoryRecord:
    return HistoryRecord(
        iteration=generation,
        value=max(fitness),
        metrics={"average_value": sum(fitness) / len(fitness)},
    )


@dataclass(frozen=True, slots=True)
class GeneticAlgorithm:
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.3
    elitism_count: int = 2

    def __post_init__(self) -> None:
        if self.population_size <= 0:
            raise ValueError("population_size harus positif")
        if self.generations < 0:
            raise ValueError("generations harus non-negatif")
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError("mutation_rate harus berada di antara 0 dan 1")
        if not 0 <= self.elitism_count <= self.population_size:
            raise ValueError("elitism_count harus berada di antara 0 dan population_size")

    def next_generation(
        self,
        population: Sequence[State],
        fitness: Sequence[float],
        problem: Problem,
        rng: random.Random,
    ) -> tuple[list[State], list[float]]:
        elites = elite_indices(fitness, self.elitism_count)
        next_population = [population[index] for index in elites]
        next_fitness = [fitness[index] for index in elites]
        cumulative_weights = roulette_weights(fitness)
        while len(next_population) < self.population_size:
            first_parent = select_parent(population, cumulative_weights, rng)
            second_parent = select_parent(population, cumulative_weights, rng)
            child = crossover(first_parent, second_parent, problem, rng)
            if rng.random() < self.mutation_rate:
                child = mutate(child, problem, rng)
            next_population.append(child)
            next_fitness.append(problem.value(child))
        return next_population, next_fitness

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        population = [random_state(problem, rng) for _ in range(self.population_size)]
        fitness = [problem.value(state) for state in population]
        evaluations = len(population)
        initial_best = population[best_index(fitness)]
        previous_best = initial_best
        history = [generation_record(0, fitness)]
        steps: list[Step] = []

        for generation in range(1, self.generations + 1):
            population, fitness = self.next_generation(population, fitness, problem, rng)
            evaluations += self.population_size - self.elitism_count
            current_best = population[best_index(fitness)]
            history.append(generation_record(generation, fitness))
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
            unit="generation",
        )

import random
from collections.abc import Sequence
from itertools import accumulate

from src.core.constraints import place_in_order
from src.core.models import Placement, Problem, State, VehicleId
from src.core.neighborhood.sampling import random_successor


def roulette_weights(fitness: Sequence[float]) -> list[float] | None:
    offset = min(0.0, *fitness)
    cumulative_weights = list(accumulate(value - offset for value in fitness))
    return cumulative_weights if cumulative_weights[-1] > 0 else None


def select_parent(
    population: Sequence[State], cumulative_weights: list[float] | None, rng: random.Random
) -> State:
    if cumulative_weights is None:
        return rng.choice(population)
    return rng.choices(population, cum_weights=cumulative_weights)[0]


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


def elite_indices(fitness: Sequence[float], count: int) -> list[int]:
    ranked = sorted(range(len(fitness)), key=lambda index: fitness[index], reverse=True)
    return ranked[:count]

import random
from collections.abc import Callable
from typing import Final

from src.core.constraints import is_valid_move, occupancy_of
from src.core.models import ORIENTATIONS, Change, Move, Placement, Problem, State
from src.core.neighborhood.enumeration import Successor, successors
from src.core.neighborhood.moves import rotation_move, swap_move

MAX_RANDOM_SUCCESSOR_ATTEMPTS: Final = 300

type Sampler = Callable[[State, Problem, random.Random], Move | None]


def sample_rotation(state: State, problem: Problem, rng: random.Random) -> Move | None:
    return rotation_move(rng.choice(problem.vehicles), state)


def sample_relocation(state: State, problem: Problem, rng: random.Random) -> Move | None:
    ship = problem.ship
    vehicle = rng.choice(problem.vehicles)
    current = state.placements[vehicle.id]
    if current is None:
        orientation = rng.choice(ORIENTATIONS)
    else:
        orientation = current.orientation
        if rng.randrange(ship.width * ship.length + 1) == 0:
            return (Change(vehicle.id, current, None),)
    target = Placement(rng.randrange(ship.width), rng.randrange(ship.length), orientation)
    if target == current:
        return None
    return (Change(vehicle.id, current, target),)


def sample_swap(state: State, problem: Problem, rng: random.Random) -> Move | None:
    first, second = rng.sample(problem.vehicles, 2)
    return swap_move(first, second, state)


SAMPLERS: Final[tuple[Sampler, ...]] = (sample_rotation, sample_relocation, sample_swap)


def random_successor(state: State, problem: Problem, rng: random.Random) -> Successor | None:
    vehicle_count = len(problem.vehicles)
    positions = problem.ship.width * problem.ship.length
    weights = (
        vehicle_count,
        vehicle_count * (positions + 1),
        vehicle_count * (vehicle_count - 1) // 2,
    )
    occupancy = occupancy_of(state, problem)
    for _ in range(MAX_RANDOM_SUCCESSOR_ATTEMPTS):
        sampler = rng.choices(SAMPLERS, weights=weights)[0]
        move = sampler(state, problem, rng)
        if move is not None and is_valid_move(move, occupancy, problem):
            return move, state.apply(move)
    valid = list(successors(state, problem))
    return rng.choice(valid) if valid else None

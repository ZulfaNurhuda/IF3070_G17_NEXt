import random
from collections.abc import Callable, Iterator
from itertools import chain, combinations
from typing import Final

from src.core.evaluator import is_valid_move, occupancy_of
from src.core.geometry import deck_positions
from src.core.models import (
    ORIENTATIONS,
    Change,
    Move,
    Orientation,
    Placement,
    Problem,
    State,
    Vehicle,
)

MAX_RANDOM_SUCCESSOR_ATTEMPTS: Final = 300

type Successor = tuple[Move, State]


def flipped(orientation: Orientation) -> Orientation:
    if orientation is Orientation.VERTICAL:
        return Orientation.HORIZONTAL
    return Orientation.VERTICAL


def rotation_move(vehicle: Vehicle, state: State) -> Move | None:
    placement = state.placements[vehicle.id]
    if placement is None or vehicle.width == vehicle.length:
        return None
    rotated = Placement(placement.x, placement.y, flipped(placement.orientation))
    return (Change(vehicle.id, placement, rotated),)


def swap_move(first: Vehicle, second: Vehicle, state: State) -> Move | None:
    first_placement = state.placements[first.id]
    second_placement = state.placements[second.id]
    if first_placement == second_placement:
        return None
    return (
        Change(first.id, first_placement, second_placement),
        Change(second.id, second_placement, first_placement),
    )


def rotation_candidates(state: State, problem: Problem) -> Iterator[Move]:
    return filter(None, (rotation_move(vehicle, state) for vehicle in problem.vehicles))


def relocation_candidates(state: State, problem: Problem) -> Iterator[Move]:
    ship = problem.ship
    for vehicle in problem.vehicles:
        current = state.placements[vehicle.id]
        if current is None:
            orientations = ORIENTATIONS
        else:
            orientations = (current.orientation,)
            yield (Change(vehicle.id, current, None),)
        for orientation in orientations:
            for x, y in deck_positions(vehicle, orientation, ship):
                target = Placement(x, y, orientation)
                if target != current:
                    yield (Change(vehicle.id, current, target),)


def swap_candidates(state: State, problem: Problem) -> Iterator[Move]:
    pairs = combinations(problem.vehicles, 2)
    return filter(None, (swap_move(first, second, state) for first, second in pairs))


def successors(state: State, problem: Problem) -> Iterator[Successor]:
    occupancy = occupancy_of(state, problem)
    candidates = chain(
        rotation_candidates(state, problem),
        relocation_candidates(state, problem),
        swap_candidates(state, problem),
    )
    for move in candidates:
        if is_valid_move(move, occupancy, problem):
            yield move, state.apply(move)


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

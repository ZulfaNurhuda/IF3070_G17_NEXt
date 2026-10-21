import random
from collections.abc import Callable, Iterator
from itertools import chain, combinations
from typing import Final

from src.core.evaluator import is_valid
from src.core.models import Change, Move, Orientation, Placement, Problem, State, Vehicle

MAX_RANDOM_NEIGHBOR_ATTEMPTS: Final = 100


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
            orientations = tuple(Orientation)
        else:
            orientations = (current.orientation,)
            yield (Change(vehicle.id, current, None),)
        for orientation in orientations:
            for x in range(ship.width):
                for y in range(ship.length):
                    target = Placement(x, y, orientation)
                    if target != current:
                        yield (Change(vehicle.id, current, target),)


def swap_candidates(state: State, problem: Problem) -> Iterator[Move]:
    pairs = combinations(problem.vehicles, 2)
    return filter(None, (swap_move(first, second, state) for first, second in pairs))


def enumerate_neighbors(state: State, problem: Problem) -> Iterator[Move]:
    candidates = chain(
        rotation_candidates(state, problem),
        relocation_candidates(state, problem),
        swap_candidates(state, problem),
    )
    for move in candidates:
        if is_valid(state.apply(move), problem):
            yield move


type Sampler = Callable[[State, Problem, random.Random], Move | None]


def sample_rotation(state: State, problem: Problem, rng: random.Random) -> Move | None:
    return rotation_move(rng.choice(problem.vehicles), state)


def sample_relocation(state: State, problem: Problem, rng: random.Random) -> Move | None:
    ship = problem.ship
    vehicle = rng.choice(problem.vehicles)
    current = state.placements[vehicle.id]
    if current is None:
        orientation = rng.choice(tuple(Orientation))
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


def random_neighbor(state: State, problem: Problem, rng: random.Random) -> Move | None:
    vehicle_count = len(problem.vehicles)
    if vehicle_count == 0:
        return None
    positions = problem.ship.width * problem.ship.length
    weights = (
        vehicle_count,
        vehicle_count * (positions + 1),
        vehicle_count * (vehicle_count - 1) // 2,
    )
    for _ in range(MAX_RANDOM_NEIGHBOR_ATTEMPTS):
        sampler = rng.choices(SAMPLERS, weights=weights)[0]
        move = sampler(state, problem, rng)
        if move is not None and is_valid(state.apply(move), problem):
            return move
    return None

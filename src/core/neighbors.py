import random
from collections.abc import Iterator
from itertools import chain, combinations
from typing import Final

from src.core.evaluator import is_valid
from src.core.models import Change, Move, Orientation, Placement, Problem, State

MAX_RANDOM_NEIGHBOR_ATTEMPTS: Final = 100


def flipped(orientation: Orientation) -> Orientation:
    if orientation is Orientation.VERTICAL:
        return Orientation.HORIZONTAL
    return Orientation.VERTICAL


def rotation_candidates(state: State, problem: Problem) -> Iterator[Move]:
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is None or vehicle.width == vehicle.length:
            continue
        rotated = Placement(placement.x, placement.y, flipped(placement.orientation))
        yield (Change(vehicle.id, placement, rotated),)


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
    for first, second in combinations(problem.vehicles, 2):
        first_placement = state.placements[first.id]
        second_placement = state.placements[second.id]
        if first_placement == second_placement:
            continue
        yield (
            Change(first.id, first_placement, second_placement),
            Change(second.id, second_placement, first_placement),
        )


def enumerate_neighbors(state: State, problem: Problem) -> Iterator[Move]:
    candidates = chain(
        rotation_candidates(state, problem),
        relocation_candidates(state, problem),
        swap_candidates(state, problem),
    )
    for move in candidates:
        if is_valid(state.apply(move), problem):
            yield move


def random_neighbor(
    state: State,
    problem: Problem,
    rng: random.Random,
    max_attempts: int = MAX_RANDOM_NEIGHBOR_ATTEMPTS,
) -> Move | None:
    # TODO: Implementasikan sampel acak satu neighbor valid.
    #   Input: state, problem, rng, max_attempts. Output: sebuah Move valid, atau None bila
    #   setelah max_attempts percobaan tidak ditemukan neighbor valid.
    #   Langkah: pilih jenis move (swap, relocate, rotate) dan parameternya secara acak
    #   lewat rng, bentuk Move, terima hanya bila is_valid(state.apply(move)); selain itu
    #   ulangi. Dilarang memakai random global.
    #   Dipakai oleh simulated-annealing dan mutasi GA.
    raise NotImplementedError

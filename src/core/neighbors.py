from collections.abc import Iterator
from itertools import chain, combinations

from src.core.evaluator import is_valid_move, occupancy_of
from src.core.geometry import deck_positions
from src.core.models import ORIENTATIONS, Change, Move, Placement, Problem, State
from src.core.moves import rotation_move, swap_move

type Successor = tuple[Move, State]


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

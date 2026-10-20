import random

from src.core.evaluator import try_place
from src.core.models import Orientation, Placement, Problem, State


def random_state(problem: Problem, rng: random.Random) -> State:
    ship = problem.ship
    state = State({vehicle.id: None for vehicle in problem.vehicles})
    vehicles = list(problem.vehicles)
    rng.shuffle(vehicles)
    for vehicle in vehicles:
        placement = Placement(
            rng.randrange(ship.width),
            rng.randrange(ship.length),
            rng.choice(tuple(Orientation)),
        )
        placed = try_place(state, problem, vehicle.id, placement)
        if placed is not None:
            state = placed
    return state

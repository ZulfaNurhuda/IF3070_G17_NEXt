import random

from src.core.evaluator import place_in_order
from src.core.models import ORIENTATIONS, Placement, Problem, State


def random_state(problem: Problem, rng: random.Random) -> State:
    ship = problem.ship
    vehicles = list(problem.vehicles)
    rng.shuffle(vehicles)
    candidates = (
        (
            vehicle.id,
            Placement(
                rng.randrange(ship.width), rng.randrange(ship.length), rng.choice(ORIENTATIONS)
            ),
        )
        for vehicle in vehicles
    )
    return place_in_order(problem, candidates)

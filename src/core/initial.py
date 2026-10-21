import random

from src.core.evaluator import place_in_order
from src.core.models import Orientation, Placement, Problem, Ship, State


def random_placement(ship: Ship, rng: random.Random) -> Placement:
    return Placement(
        rng.randrange(ship.width), rng.randrange(ship.length), rng.choice(tuple(Orientation))
    )


def random_state(problem: Problem, rng: random.Random) -> State:
    vehicles = list(problem.vehicles)
    rng.shuffle(vehicles)
    candidates = ((vehicle.id, random_placement(problem.ship, rng)) for vehicle in vehicles)
    return place_in_order(problem, candidates)

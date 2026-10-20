from typing import Final

from src.core.evaluator import loaded_vehicles
from src.core.models import Objective, Problem, State

DEFAULT_OBJECTIVE_NAME: Final = "total-shipping-fee"


def total_shipping_fee(state: State, problem: Problem) -> float:
    return float(sum(vehicle.shipping_fee for vehicle in loaded_vehicles(state, problem)))


def urgency_weighted_fee(state: State, problem: Problem) -> float:
    carried = loaded_vehicles(state, problem)
    return sum((vehicle.shipping_fee / vehicle.eta for vehicle in carried), 0.0)


OBJECTIVES: Final[dict[str, Objective]] = {
    "total-shipping-fee": total_shipping_fee,
    "urgency-weighted-fee": urgency_weighted_fee,
}

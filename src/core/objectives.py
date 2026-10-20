from typing import Final

from src.core.evaluator import loaded_vehicles
from src.core.models import Objective, Problem, State

DEFAULT_OBJECTIVE_NAME: Final = "total-shipping-fee"


def total_shipping_fee(state: State, problem: Problem) -> float:
    return float(sum(vehicle.shipping_fee for vehicle in loaded_vehicles(state, problem)))


def urgency_weighted_fee(state: State, problem: Problem) -> float:
    # TODO: Implementasikan objective alternatif (bonus 1) tanpa variabel baru.
    #   Input: state dan problem. Output: jumlah shipping_fee / eta untuk semua kendaraan
    #   terangkut, sehingga kendaraan dengan eta lebih dekat bernilai lebih besar.
    #   Asumsi eta > 0; validasi dilakukan saat memuat instance (serialize.load_problem).
    raise NotImplementedError


OBJECTIVES: Final[dict[str, Objective]] = {
    "total-shipping-fee": total_shipping_fee,
    "urgency-weighted-fee": urgency_weighted_fee,
}

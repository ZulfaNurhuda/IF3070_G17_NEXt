from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from src.core.geometry import Cell, cells_of, placement_limits
from src.core.models import (
    Change,
    Move,
    Placement,
    Problem,
    Ship,
    State,
    Vehicle,
    VehicleId,
)


@dataclass(frozen=True, slots=True)
class Occupancy:
    owners: Mapping[Cell, VehicleId]
    weight: int


def fits_on_deck(vehicle: Vehicle, placement: Placement, ship: Ship) -> bool:
    limit_x, limit_y = placement_limits(vehicle, placement.orientation, ship)
    return 0 <= placement.x < limit_x and 0 <= placement.y < limit_y


def loaded_vehicles(state: State, problem: Problem) -> tuple[Vehicle, ...]:
    return tuple(
        vehicle for vehicle in problem.vehicles if state.placements[vehicle.id] is not None
    )


def occupy(owners: dict[Cell, VehicleId], vehicle: Vehicle, placement: Placement) -> int:
    owners.update(dict.fromkeys(cells_of(vehicle, placement), vehicle.id))
    return vehicle.weight


def occupancy_of(state: State, problem: Problem) -> Occupancy:
    owners: dict[Cell, VehicleId] = {}
    weight = 0
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is not None:
            weight += occupy(owners, vehicle, placement)
    return Occupancy(owners, weight)


def is_valid_move(move: Move, occupancy: Occupancy, problem: Problem) -> bool:
    ship = problem.ship
    moved = [(problem.vehicle_by_id[change.vehicle_id], change) for change in move]
    weight = occupancy.weight
    for vehicle, change in moved:
        if change.before is not None:
            weight -= vehicle.weight
        if change.after is not None:
            weight += vehicle.weight
    if weight > ship.max_capacity:
        return False
    moved_ids = {vehicle.id for vehicle, _ in moved}
    taken: set[Cell] = set()
    for vehicle, change in moved:
        if change.after is None:
            continue
        if not fits_on_deck(vehicle, change.after, ship):
            return False
        for cell in cells_of(vehicle, change.after):
            owner = occupancy.owners.get(cell)
            if (owner is not None and owner not in moved_ids) or cell in taken:
                return False
            taken.add(cell)
    return True


def place_in_order(problem: Problem, candidates: Iterable[tuple[VehicleId, Placement]]) -> State:
    placements: dict[VehicleId, Placement | None] = dict.fromkeys(problem.vehicle_by_id)
    owners: dict[Cell, VehicleId] = {}
    weight = 0
    for vehicle_id, placement in candidates:
        move = (Change(vehicle_id, None, placement),)
        if is_valid_move(move, Occupancy(owners, weight), problem):
            weight += occupy(owners, problem.vehicle_by_id[vehicle_id], placement)
            placements[vehicle_id] = placement
    return State(placements)

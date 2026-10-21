from collections.abc import Mapping
from dataclasses import dataclass

from src.core.models import (
    Change,
    Move,
    Orientation,
    Placement,
    Problem,
    State,
    Vehicle,
    VehicleId,
)

type Cell = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Occupancy:
    owners: Mapping[Cell, VehicleId]
    weight: int


EMPTY_OCCUPANCY = Occupancy({}, 0)


def cells_of(vehicle: Vehicle, placement: Placement) -> frozenset[Cell]:
    if placement.orientation is Orientation.VERTICAL:
        extent_x, extent_y = vehicle.width, vehicle.length
    else:
        extent_x, extent_y = vehicle.length, vehicle.width
    return frozenset(
        (placement.x + offset_x, placement.y + offset_y)
        for offset_x in range(extent_x)
        for offset_y in range(extent_y)
    )


def loaded_vehicles(state: State, problem: Problem) -> tuple[Vehicle, ...]:
    return tuple(
        vehicle for vehicle in problem.vehicles if state.placements[vehicle.id] is not None
    )


def occupancy_of(state: State, problem: Problem) -> Occupancy:
    owners: dict[Cell, VehicleId] = {}
    weight = 0
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is not None:
            weight += vehicle.weight
            owners.update(dict.fromkeys(cells_of(vehicle, placement), vehicle.id))
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
        for x, y in cells_of(vehicle, change.after):
            if not (0 <= x < ship.width and 0 <= y < ship.length):
                return False
            owner = occupancy.owners.get((x, y))
            if (owner is not None and owner not in moved_ids) or (x, y) in taken:
                return False
            taken.add((x, y))
    return True


def is_valid(state: State, problem: Problem) -> bool:
    placing = tuple(
        Change(vehicle.id, None, state.placements[vehicle.id])
        for vehicle in loaded_vehicles(state, problem)
    )
    return is_valid_move(placing, EMPTY_OCCUPANCY, problem)


def try_place(
    state: State, problem: Problem, vehicle_id: VehicleId, placement: Placement
) -> State | None:
    move = (Change(vehicle_id, state.placements[vehicle_id], placement),)
    if is_valid_move(move, occupancy_of(state, problem), problem):
        return state.apply(move)
    return None

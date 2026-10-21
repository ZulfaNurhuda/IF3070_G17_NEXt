from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache

from src.core.models import (
    Change,
    Move,
    Orientation,
    Placement,
    Problem,
    Ship,
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


def footprint(vehicle: Vehicle, orientation: Orientation) -> tuple[int, int]:
    if orientation is Orientation.VERTICAL:
        return vehicle.width, vehicle.length
    return vehicle.length, vehicle.width


def fits_on_deck(vehicle: Vehicle, placement: Placement, ship: Ship) -> bool:
    extent_x, extent_y = footprint(vehicle, placement.orientation)
    return 0 <= placement.x <= ship.width - extent_x and 0 <= placement.y <= ship.length - extent_y


@cache
def cells_of(vehicle: Vehicle, placement: Placement) -> frozenset[Cell]:
    extent_x, extent_y = footprint(vehicle, placement.orientation)
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
        if not fits_on_deck(vehicle, change.after, ship):
            return False
        for cell in cells_of(vehicle, change.after):
            owner = occupancy.owners.get(cell)
            if (owner is not None and owner not in moved_ids) or cell in taken:
                return False
            taken.add(cell)
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


def place_in_order(problem: Problem, candidates: Iterable[tuple[VehicleId, Placement]]) -> State:
    placements: dict[VehicleId, Placement | None] = dict.fromkeys(problem.vehicle_by_id)
    owners: dict[Cell, VehicleId] = {}
    weight = 0
    for vehicle_id, placement in candidates:
        move = (Change(vehicle_id, None, placement),)
        if is_valid_move(move, Occupancy(owners, weight), problem):
            vehicle = problem.vehicle_by_id[vehicle_id]
            weight += vehicle.weight
            owners.update(dict.fromkeys(cells_of(vehicle, placement), vehicle_id))
            placements[vehicle_id] = placement
    return State(placements)

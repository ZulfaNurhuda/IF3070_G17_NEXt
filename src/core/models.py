from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final

type VehicleId = str


class Orientation(StrEnum):
    HORIZONTAL = "Horizontal"
    VERTICAL = "Vertical"


ORIENTATIONS: Final = tuple(Orientation)


@dataclass(frozen=True, slots=True)
class Vehicle:
    id: VehicleId
    width: int
    length: int
    shipping_fee: int
    weight: int
    eta: int


@dataclass(frozen=True, slots=True)
class Ship:
    width: int
    length: int
    max_capacity: int


@dataclass(frozen=True, slots=True)
class Placement:
    x: int
    y: int
    orientation: Orientation


@dataclass(frozen=True, slots=True)
class Change:
    vehicle_id: VehicleId
    before: Placement | None
    after: Placement | None


type Move = tuple[Change, ...]
type Objective = Callable[[State, Problem], float]


@dataclass(frozen=True, slots=True)
class State:
    placements: Mapping[VehicleId, Placement | None]

    def apply(self, move: Move) -> State:
        updated = dict(self.placements)
        for change in move:
            if change.vehicle_id not in self.placements:
                raise ValueError(f"kendaraan tidak dikenal: {change.vehicle_id}")
            if self.placements[change.vehicle_id] != change.before:
                raise ValueError(f"placement awal {change.vehicle_id} tidak cocok dengan move")
            updated[change.vehicle_id] = change.after
        return State(updated)

    def diff(self, other: State) -> Move:
        if self.placements.keys() != other.placements.keys():
            raise ValueError("kedua state harus memuat kendaraan yang sama")
        return tuple(
            Change(vehicle_id, self.placements[vehicle_id], other.placements[vehicle_id])
            for vehicle_id in sorted(self.placements)
            if self.placements[vehicle_id] != other.placements[vehicle_id]
        )


@dataclass(frozen=True, slots=True)
class Problem:
    ship: Ship
    vehicles: tuple[Vehicle, ...]
    objective_name: str
    objective: Objective
    vehicle_by_id: Mapping[VehicleId, Vehicle] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.vehicles:
            raise ValueError("problem harus memiliki minimal satu kendaraan")
        vehicle_by_id = {vehicle.id: vehicle for vehicle in self.vehicles}
        if len(vehicle_by_id) != len(self.vehicles):
            raise ValueError("id kendaraan harus unik")
        object.__setattr__(self, "vehicle_by_id", vehicle_by_id)

    def value(self, state: State) -> float:
        return self.objective(state, self)

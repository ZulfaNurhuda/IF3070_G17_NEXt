from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum

type VehicleId = str


class Orientation(StrEnum):
    HORIZONTAL = "Horizontal"
    VERTICAL = "Vertical"


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

    def value(self, state: State) -> float:
        return self.objective(state, self)

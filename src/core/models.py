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
        # TODO: Implementasikan penerapan sebuah Move pada State (immutable).
        #   Input: move berisi Change(vehicle_id, before, after). Output: State baru yang
        #   salinannya sama dengan self, kecuali placements[change.vehicle_id] = change.after
        #   untuk setiap change dalam move. State asal tidak boleh berubah.
        #   Validasi: placements[change.vehicle_id] harus sama dengan change.before; bila
        #   tidak, move dibuat dari state lain, sehingga raise ValueError.
        #   Fungsi ini TIDAK memeriksa constraint (itu tugas evaluator.is_valid).
        raise NotImplementedError

    def diff(self, other: State) -> Move:
        # TODO: Implementasikan selisih dua State sebagai Move.
        #   Input: other (State tujuan, memuat kendaraan yang sama dengan self).
        #   Output: Move berisi satu Change(vehicle_id, before, after) untuk setiap kendaraan
        #   yang placement-nya berbeda antara self dan other; Move kosong bila kedua state
        #   sama. Urutkan berdasarkan vehicle_id agar hasilnya deterministik.
        #   Invarian: self.apply(self.diff(other)) == other.
        #   Dipakai GA untuk membentuk Step antar generasi (individu terbaik berganti).
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Problem:
    ship: Ship
    vehicles: tuple[Vehicle, ...]
    objective_name: str
    objective: Objective

    def value(self, state: State) -> float:
        return self.objective(state, self)

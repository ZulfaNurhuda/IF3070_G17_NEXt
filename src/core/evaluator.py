from src.core.models import Orientation, Placement, Problem, State, Vehicle, VehicleId

type Cell = tuple[int, int]


def cells_of(vehicle: Vehicle, placement: Placement) -> frozenset[Cell]:
    if placement.orientation is Orientation.VERTICAL:
        extent_x, extent_y = vehicle.width, vehicle.length
    else:
        extent_x, extent_y = vehicle.length, vehicle.width
    return frozenset(
        (placement.x + dx, placement.y + dy) for dx in range(extent_x) for dy in range(extent_y)
    )


def loaded_vehicles(state: State, problem: Problem) -> tuple[Vehicle, ...]:
    # TODO: Implementasikan daftar kendaraan yang terangkut pada state.
    #   Input: state dan problem. Output: tuple Vehicle yang placement-nya bukan None,
    #   dengan urutan sama seperti problem.vehicles.
    #   Dipakai oleh objectives.py dan is_valid.
    raise NotImplementedError


def is_valid(state: State, problem: Problem) -> bool:
    # TODO: Implementasikan pengecekan seluruh constraint pada state.
    #   Input: state dan problem. Output: True hanya bila (1) tidak ada sel yang ditempati
    #   lebih dari satu kendaraan, (2) setiap sel footprint berada dalam 0 <= x < ship.width
    #   dan 0 <= y < ship.length, (3) total weight kendaraan terangkut <= ship.max_capacity.
    #   Kendaraan di luar kapal (placement None) tidak diperiksa.
    #   Ini satu-satunya tempat constraint dicek; neighbors, initial, dan crossover GA
    #   memanggilnya.
    raise NotImplementedError


def try_place(
    state: State, problem: Problem, vehicle_id: VehicleId, placement: Placement
) -> State | None:
    # TODO: Implementasikan penempatan kendaraan yang aman terhadap constraint.
    #   Input: state, problem, vehicle_id, placement. Output: State baru dengan kendaraan itu
    #   berada di placement, atau None bila hasilnya tidak lolos is_valid.
    #   State asal tidak boleh berubah. Dipakai oleh initial.random_state dan crossover GA
    #   (kendaraan yang gagal ditempatkan tetap di luar kapal).
    raise NotImplementedError

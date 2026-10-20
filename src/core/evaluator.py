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
    return tuple(
        vehicle for vehicle in problem.vehicles if state.placements[vehicle.id] is not None
    )


def is_valid(state: State, problem: Problem) -> bool:
    ship = problem.ship
    occupied: set[Cell] = set()
    total_weight = 0
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is None:
            continue
        total_weight += vehicle.weight
        if total_weight > ship.max_capacity:
            return False
        for x, y in cells_of(vehicle, placement):
            if not (0 <= x < ship.width and 0 <= y < ship.length):
                return False
            if (x, y) in occupied:
                return False
            occupied.add((x, y))
    return True


def try_place(
    state: State, problem: Problem, vehicle_id: VehicleId, placement: Placement
) -> State | None:
    # TODO: Implementasikan penempatan kendaraan yang aman terhadap constraint.
    #   Input: state, problem, vehicle_id, placement. Output: State baru dengan kendaraan itu
    #   berada di placement, atau None bila hasilnya tidak lolos is_valid.
    #   State asal tidak boleh berubah. Dipakai oleh initial.random_state dan crossover GA
    #   (kendaraan yang gagal ditempatkan tetap di luar kapal).
    raise NotImplementedError

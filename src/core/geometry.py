from collections.abc import Iterator
from functools import lru_cache
from itertools import product
from typing import Final

from src.core.models import Orientation, Placement, Ship, Vehicle

type Cell = tuple[int, int]

CELL_CACHE_SIZE: Final = 32768


def footprint(vehicle: Vehicle, orientation: Orientation) -> tuple[int, int]:
    if orientation is Orientation.VERTICAL:
        return vehicle.width, vehicle.length
    return vehicle.length, vehicle.width


def placement_limits(vehicle: Vehicle, orientation: Orientation, ship: Ship) -> tuple[int, int]:
    extent_x, extent_y = footprint(vehicle, orientation)
    return ship.width - extent_x + 1, ship.length - extent_y + 1


def deck_positions(vehicle: Vehicle, orientation: Orientation, ship: Ship) -> Iterator[Cell]:
    limit_x, limit_y = placement_limits(vehicle, orientation, ship)
    return product(range(limit_x), range(limit_y))


@lru_cache(maxsize=CELL_CACHE_SIZE)
def cells_of(vehicle: Vehicle, placement: Placement) -> frozenset[Cell]:
    extent_x, extent_y = footprint(vehicle, placement.orientation)
    return frozenset(
        (placement.x + offset_x, placement.y + offset_y)
        for offset_x in range(extent_x)
        for offset_y in range(extent_y)
    )

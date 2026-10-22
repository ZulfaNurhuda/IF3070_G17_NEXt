import itertools
import json
import random
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from src.core.models import Vehicle
from src.storage.payloads import ProblemPayload
from src.storage.results import vehicle_payload
from src.storage.specification import ATTRIBUTE_KEYS, IntegerRange, VehicleSpecification

VEHICLE_ID_PREFIX: Final = "Car"
DEFAULT_CAPACITY_RATIO: Final = 0.6
DEFAULT_VEHICLE_COUNT: Final = 25
DEFAULT_RANGES: Final[Mapping[str, IntegerRange]] = {
    "width": IntegerRange(1, 4),
    "length": IntegerRange(2, 6),
    "shipping_fee": IntegerRange(20, 100),
    "weight": IntegerRange(2, 8),
    "eta": IntegerRange(1, 10),
}
SAFE_NAME: Final = re.compile(r"[A-Za-z0-9_-]+")


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    ship_width: IntegerRange
    ship_length: IntegerRange
    capacity: IntegerRange | None
    capacity_ratio: float
    vehicle_count: IntegerRange | None
    ranges: Mapping[str, IntegerRange]
    specifications: Sequence[VehicleSpecification]


def effective_ranges(
    request: GenerationRequest, specification: VehicleSpecification
) -> Mapping[str, IntegerRange]:
    return {**request.ranges, **specification.ranges}


def can_have_random_vehicles(request: GenerationRequest) -> bool:
    if request.vehicle_count is None:
        return not request.specifications
    return request.vehicle_count.high > len(request.specifications)


def validate_ranges(
    ranges: Mapping[str, IntegerRange], request: GenerationRequest, owner: str
) -> None:
    width, length = ranges["width"].high, ranges["length"].high
    ship_width, ship_length = request.ship_width.low, request.ship_length.low
    fits = (width <= ship_width and length <= ship_length) or (
        length <= ship_width and width <= ship_length
    )
    if not fits:
        raise ValueError(
            f"{owner}: kendaraan terbesar {width}x{length} tidak muat di geladak "
            f"terkecil {ship_width}x{ship_length}"
        )
    heaviest = ranges["weight"].high
    if request.capacity is not None and heaviest > request.capacity.low:
        raise ValueError(
            f"{owner}: berat maksimum {heaviest} melebihi kapasitas terkecil {request.capacity.low}"
        )


def validate_request(request: GenerationRequest) -> None:
    if request.capacity_ratio <= 0:
        raise ValueError("--capacity-ratio harus lebih besar dari 0")
    explicit = [spec.number for spec in request.specifications if spec.number is not None]
    if len(set(explicit)) != len(explicit):
        raise ValueError("id pada --vehicle tidak boleh kembar")
    specified = len(request.specifications)
    if request.vehicle_count is not None and request.vehicle_count.low < specified:
        raise ValueError(
            f"--vehicles: batas bawah {request.vehicle_count.low} lebih kecil dari "
            f"jumlah --vehicle ({specified})"
        )
    for index, spec in enumerate(request.specifications, start=1):
        validate_ranges(effective_ranges(request, spec), request, f"--vehicle ke-{index}")
    if can_have_random_vehicles(request):
        validate_ranges(request.ranges, request, "kendaraan acak (--vehicle-*)")


def free_numbers(taken: set[int]) -> Iterator[int]:
    return (number for number in itertools.count(1) if number not in taken)


def draw_vehicle(number: int, ranges: Mapping[str, IntegerRange], rng: random.Random) -> Vehicle:
    values = {key: ranges[key].draw(rng) for key in ATTRIBUTE_KEYS}
    return Vehicle(f"{VEHICLE_ID_PREFIX}{number:02d}", **values)


def draw_vehicle_count(request: GenerationRequest, rng: random.Random) -> int:
    if request.vehicle_count is not None:
        return request.vehicle_count.draw(rng)
    return len(request.specifications) or DEFAULT_VEHICLE_COUNT


def generate_vehicles(
    request: GenerationRequest, random_count: int, rng: random.Random
) -> list[Vehicle]:
    explicit = {spec.number for spec in request.specifications if spec.number is not None}
    available = free_numbers(explicit)
    plan: list[tuple[int, Mapping[str, IntegerRange]]] = [
        (
            spec.number if spec.number is not None else next(available),
            effective_ranges(request, spec),
        )
        for spec in request.specifications
    ]
    plan.extend((next(available), request.ranges) for _ in range(random_count))
    drawn = [(number, draw_vehicle(number, ranges, rng)) for number, ranges in plan]
    return [vehicle for _, vehicle in sorted(drawn, key=lambda entry: entry[0])]


def resolve_capacity(capacity: int | None, ratio: float, vehicles: Sequence[Vehicle]) -> int:
    if capacity is not None:
        return capacity
    total_weight = sum(vehicle.weight for vehicle in vehicles)
    return max(1, round(total_weight * ratio))


def generate_problem(request: GenerationRequest, rng: random.Random) -> ProblemPayload:
    validate_request(request)
    ship_width = request.ship_width.draw(rng)
    ship_length = request.ship_length.draw(rng)
    count = draw_vehicle_count(request, rng)
    capacity = None if request.capacity is None else request.capacity.draw(rng)
    vehicles = generate_vehicles(request, count - len(request.specifications), rng)
    return {
        "ship": {
            "width": ship_width,
            "length": ship_length,
            "max_capacity": resolve_capacity(capacity, request.capacity_ratio, vehicles),
        },
        "vehicles": [vehicle_payload(vehicle) for vehicle in vehicles],
    }


def render_instance(payload: ProblemPayload) -> str:
    ship = json.dumps(payload["ship"])
    vehicles = ",\n    ".join(json.dumps(vehicle) for vehicle in payload["vehicles"])
    return f'{{\n  "ship": {ship},\n  "vehicles": [\n    {vehicles}\n  ]\n}}\n'


def write_instance(payload: ProblemPayload, directory: Path, name: str) -> Path:
    if SAFE_NAME.fullmatch(name) is None:
        raise ValueError("--name hanya boleh berisi huruf, angka, '-' dan '_'")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(render_instance(payload))
    except FileExistsError:
        raise ValueError(f"{path.name} sudah ada di {directory}") from None
    return path

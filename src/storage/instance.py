import json
from collections.abc import Mapping
from pathlib import Path

from src.core.models import Problem, Ship, Vehicle
from src.core.objectives import OBJECTIVES


def expect_mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} harus berupa objek JSON")
    return value


def expect_positive_int(mapping: Mapping[str, object], key: str, owner: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{owner}.{key} harus berupa bilangan bulat positif")
    return value


def parse_ship(raw: object) -> Ship:
    ship = expect_mapping(raw, "ship")
    return Ship(
        expect_positive_int(ship, "width", "ship"),
        expect_positive_int(ship, "length", "ship"),
        expect_positive_int(ship, "max_capacity", "ship"),
    )


def parse_vehicle(raw: object, index: int) -> Vehicle:
    owner = f"vehicles[{index}]"
    vehicle = expect_mapping(raw, owner)
    vehicle_id = vehicle.get("id")
    if not isinstance(vehicle_id, str) or not vehicle_id:
        raise ValueError(f"{owner}.id harus berupa teks tidak kosong")
    return Vehicle(
        vehicle_id,
        expect_positive_int(vehicle, "width", owner),
        expect_positive_int(vehicle, "length", owner),
        expect_positive_int(vehicle, "shipping_fee", owner),
        expect_positive_int(vehicle, "weight", owner),
        expect_positive_int(vehicle, "eta", owner),
    )


def load_problem(path: Path, objective_name: str) -> Problem:
    if objective_name not in OBJECTIVES:
        valid_names = ", ".join(sorted(OBJECTIVES))
        raise ValueError(f"objective tidak dikenal: {objective_name}; pilihan: {valid_names}")
    root = expect_mapping(json.loads(path.read_text(encoding="utf-8")), "instance")
    raw_vehicles = root.get("vehicles")
    if not isinstance(raw_vehicles, list):
        raise ValueError("vehicles harus berupa daftar")
    ship = parse_ship(root.get("ship"))
    vehicles = tuple(parse_vehicle(raw, index) for index, raw in enumerate(raw_vehicles))
    return Problem(ship, vehicles, objective_name, OBJECTIVES[objective_name])

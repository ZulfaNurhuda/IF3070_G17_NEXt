import json
from collections.abc import Mapping
from pathlib import Path
from typing import NotRequired, TypedDict

from src.core.models import Problem, Ship, State, Vehicle
from src.core.objectives import OBJECTIVES
from src.experiments.runner import ExperimentResult, RunRecord


class ShipPayload(TypedDict):
    width: int
    length: int
    max_capacity: int


class VehiclePayload(TypedDict):
    id: str
    width: int
    length: int
    shipping_fee: int
    weight: int
    eta: int


class ProblemPayload(TypedDict):
    ship: ShipPayload
    vehicles: list[VehiclePayload]


class PlacementPayload(TypedDict):
    x: int
    y: int
    orientation: str


class PlacedVehiclePayload(PlacementPayload):
    id: str


class StatePayload(TypedDict):
    placements: list[PlacedVehiclePayload]
    outside: list[str]
    value: float
    total_shipping_fee: float
    valid: bool


ChangePayload = TypedDict(
    "ChangePayload",
    {"id": str, "from": PlacementPayload | None, "to": PlacementPayload | None},
)


class HistoryEntry(TypedDict):
    iteration: int
    value: float
    acceptance_probability: NotRequired[float]
    maximum_value: NotRequired[float]
    average_value: NotRequired[float]


class StepPayload(TypedDict):
    iteration: int
    changes: list[ChangePayload]


class RunPayload(TypedDict):
    run: int
    seed: int
    duration_seconds: float
    iterations: int
    initial_state: StatePayload
    final_state: StatePayload
    history: list[HistoryEntry]
    steps: list[StepPayload]
    extra: dict[str, float]


class ExperimentPayload(TypedDict):
    problem: ProblemPayload
    algorithm: str
    objective: str
    params: dict[str, object]
    created_at: str
    runs: list[RunPayload]


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
    if not isinstance(raw_vehicles, list) or not raw_vehicles:
        raise ValueError("vehicles harus berupa daftar yang tidak kosong")
    ship = parse_ship(root.get("ship"))
    vehicles = tuple(parse_vehicle(raw, index) for index, raw in enumerate(raw_vehicles))
    vehicle_ids = [vehicle.id for vehicle in vehicles]
    if len(set(vehicle_ids)) != len(vehicle_ids):
        raise ValueError("id kendaraan harus unik")
    return Problem(ship, vehicles, objective_name, OBJECTIVES[objective_name])


def state_payload(state: State, problem: Problem) -> StatePayload:
    # TODO: Implementasikan konversi State ke StatePayload.
    #   Output: placements berisi kendaraan terangkut (id, x, y, orientation), outside berisi
    #   id kendaraan di luar kapal, value = problem.value(state), total_shipping_fee dihitung
    #   dengan objective total-shipping-fee (selalu disimpan), valid = is_valid(state, problem).
    raise NotImplementedError


def run_payload(record: RunRecord, problem: Problem) -> RunPayload:
    # TODO: Implementasikan konversi RunRecord ke RunPayload.
    #   Petakan HistoryRecord ke HistoryEntry (kunci opsional hanya bila nilainya bukan
    #   None), Step ke StepPayload (Change menjadi {"id", "from", "to"}), dan result.extra
    #   ke extra. duration_seconds dan seed diambil dari record.
    raise NotImplementedError


def experiment_payload(experiment: ExperimentResult) -> ExperimentPayload:
    # TODO: Implementasikan konversi ExperimentResult ke ExperimentPayload.
    #   params = dataclasses.asdict(experiment.algorithm) (nilai yang sudah resolved),
    #   created_at dalam format ISO tanpa mikrodetik, problem lewat konversi Problem ke
    #   ProblemPayload, objective = problem.objective_name.
    raise NotImplementedError


def write_experiment(experiment: ExperimentResult, directory: Path) -> Path:
    # TODO: Implementasikan penulisan hasil eksperimen ke file JSON baru.
    #   Nama file: {algorithm}_ship{width}x{length}-vehicles{n}_{unix_timestamp}.json
    #   Buat direktori bila belum ada, jangan menimpa file
    #   yang sudah ada, tulis UTF-8 dengan indent=2. Output: path file yang ditulis.
    raise NotImplementedError

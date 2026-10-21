import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import NotRequired, TypedDict

from src.algorithms.base import HistoryRecord
from src.algorithms.registry import REGISTRY
from src.core.evaluator import is_valid
from src.core.models import Change, Placement, Problem, Ship, State, Vehicle
from src.core.objectives import OBJECTIVES, total_shipping_fee
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


def placement_fields(placement: Placement) -> PlacementPayload:
    return {"x": placement.x, "y": placement.y, "orientation": placement.orientation.value}


def placement_payload(placement: Placement | None) -> PlacementPayload | None:
    return None if placement is None else placement_fields(placement)


def state_payload(state: State, problem: Problem) -> StatePayload:
    placements: list[PlacedVehiclePayload] = []
    outside: list[str] = []
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is None:
            outside.append(vehicle.id)
        else:
            placements.append({"id": vehicle.id, **placement_fields(placement)})
    return {
        "placements": placements,
        "outside": outside,
        "value": problem.value(state),
        "total_shipping_fee": total_shipping_fee(state, problem),
        "valid": is_valid(state, problem),
    }


def change_payload(change: Change) -> ChangePayload:
    return {
        "id": change.vehicle_id,
        "from": placement_payload(change.before),
        "to": placement_payload(change.after),
    }


def history_entry(record: HistoryRecord) -> HistoryEntry:
    entry: HistoryEntry = {"iteration": record.iteration, "value": record.value}
    if record.acceptance_probability is not None:
        entry["acceptance_probability"] = record.acceptance_probability
    if record.maximum_value is not None:
        entry["maximum_value"] = record.maximum_value
    if record.average_value is not None:
        entry["average_value"] = record.average_value
    return entry


def run_payload(record: RunRecord, problem: Problem) -> RunPayload:
    result = record.result
    return {
        "run": record.run,
        "seed": record.seed,
        "duration_seconds": record.duration_seconds,
        "iterations": result.iterations,
        "initial_state": state_payload(result.initial_state, problem),
        "final_state": state_payload(result.final_state, problem),
        "history": [history_entry(entry) for entry in result.history],
        "steps": [
            {
                "iteration": step.iteration,
                "changes": [change_payload(change) for change in step.changes],
            }
            for step in result.steps
        ],
        "extra": {**result.extra, "evaluations": result.evaluations},
    }


def problem_payload(problem: Problem) -> ProblemPayload:
    ship = problem.ship
    return {
        "ship": {"width": ship.width, "length": ship.length, "max_capacity": ship.max_capacity},
        "vehicles": [
            {
                "id": vehicle.id,
                "width": vehicle.width,
                "length": vehicle.length,
                "shipping_fee": vehicle.shipping_fee,
                "weight": vehicle.weight,
                "eta": vehicle.eta,
            }
            for vehicle in problem.vehicles
        ],
    }


def registry_name(algorithm: object) -> str:
    for name, factory in REGISTRY.items():
        if factory is type(algorithm):
            return name
    raise ValueError(f"algoritma tidak terdaftar: {type(algorithm).__name__}")


def algorithm_parameters(algorithm: object) -> dict[str, object]:
    if not is_dataclass(algorithm) or isinstance(algorithm, type):
        raise TypeError("algoritma harus berupa instance dataclass")
    parameters: dict[str, object] = {}
    for field in fields(algorithm):
        value: object = getattr(algorithm, field.name)
        if is_dataclass(value) and not isinstance(value, type):
            value = {"algorithm": registry_name(value), **algorithm_parameters(value)}
        parameters[field.name] = value
    return parameters


def experiment_payload(experiment: ExperimentResult) -> ExperimentPayload:
    problem = experiment.problem
    return {
        "problem": problem_payload(problem),
        "algorithm": experiment.algorithm_name,
        "objective": problem.objective_name,
        "params": algorithm_parameters(experiment.algorithm),
        "created_at": experiment.created_at.isoformat(timespec="seconds"),
        "runs": [run_payload(record, problem) for record in experiment.runs],
    }


def write_experiment(experiment: ExperimentResult, directory: Path) -> Path:
    ship = experiment.problem.ship
    vehicle_count = len(experiment.problem.vehicles)
    prefix = f"{experiment.algorithm_name}_ship{ship.width}x{ship.length}-vehicles{vehicle_count}"
    content = json.dumps(experiment_payload(experiment), indent=2, ensure_ascii=False) + "\n"
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = int(experiment.created_at.timestamp())
    while True:
        path = directory / f"{prefix}_{timestamp}.json"
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            timestamp += 1
        else:
            return path

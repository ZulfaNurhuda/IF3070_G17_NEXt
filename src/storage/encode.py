from src.algorithms.base import HistoryRecord, Step
from src.algorithms.registry import algorithm_parameters, registry_name
from src.core.models import Change, Placement, Problem, State, Vehicle
from src.core.objectives import total_shipping_fee
from src.experiments.runner import ExperimentResult, RunRecord
from src.storage.payloads import (
    ChangePayload,
    ExperimentPayload,
    HistoryEntry,
    PlacedVehiclePayload,
    PlacementPayload,
    ProblemPayload,
    RunPayload,
    StatePayload,
    StepPayload,
    VehiclePayload,
)


def placement_payload(placement: Placement) -> PlacementPayload:
    return {"x": placement.x, "y": placement.y, "orientation": placement.orientation.value}


def state_payload(state: State, problem: Problem) -> StatePayload:
    placements: list[PlacedVehiclePayload] = []
    outside: list[str] = []
    for vehicle in problem.vehicles:
        placement = state.placements[vehicle.id]
        if placement is None:
            outside.append(vehicle.id)
        else:
            placements.append({"id": vehicle.id, **placement_payload(placement)})
    return {
        "placements": placements,
        "outside": outside,
        "value": problem.value(state),
        "total_shipping_fee": total_shipping_fee(state, problem),
    }


def change_payload(change: Change) -> ChangePayload:
    before, after = change.before, change.after
    return {
        "id": change.vehicle_id,
        "from": None if before is None else placement_payload(before),
        "to": None if after is None else placement_payload(after),
    }


def step_payload(step: Step) -> StepPayload:
    return {
        "iteration": step.iteration,
        "changes": [change_payload(change) for change in step.changes],
    }


def history_entry(record: HistoryRecord) -> HistoryEntry:
    return {"iteration": record.iteration, "value": record.value, **record.metrics}


def run_payload(record: RunRecord, problem: Problem) -> RunPayload:
    result = record.result
    return {
        "run": record.run,
        "seed": record.seed,
        "duration_seconds": record.duration_seconds,
        "iterations": result.iterations,
        "unit": result.unit,
        "initial_state": state_payload(result.initial_state, problem),
        "final_state": state_payload(result.final_state, problem),
        "history": [history_entry(entry) for entry in result.history],
        "steps": [step_payload(step) for step in result.steps],
        "extra": {**result.extra, "evaluations": result.evaluations},
    }


def vehicle_payload(vehicle: Vehicle) -> VehiclePayload:
    return {
        "id": vehicle.id,
        "width": vehicle.width,
        "length": vehicle.length,
        "shipping_fee": vehicle.shipping_fee,
        "weight": vehicle.weight,
        "eta": vehicle.eta,
    }


def problem_payload(problem: Problem) -> ProblemPayload:
    ship = problem.ship
    return {
        "ship": {"width": ship.width, "length": ship.length, "max_capacity": ship.max_capacity},
        "vehicles": [vehicle_payload(vehicle) for vehicle in problem.vehicles],
    }


def experiment_payload(experiment: ExperimentResult) -> ExperimentPayload:
    problem = experiment.problem
    return {
        "problem": problem_payload(problem),
        "algorithm": registry_name(experiment.algorithm),
        "objective": problem.objective_name,
        "params": algorithm_parameters(experiment.algorithm),
        "created_at": experiment.created_at.isoformat(timespec="seconds"),
        "runs": [run_payload(record, problem) for record in experiment.runs],
    }

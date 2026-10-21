from typing import TypedDict


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


ChangePayload = TypedDict(
    "ChangePayload",
    {"id": str, "from": PlacementPayload | None, "to": PlacementPayload | None},
)


type HistoryEntry = dict[str, float]


class StepPayload(TypedDict):
    iteration: int
    changes: list[ChangePayload]


class RunPayload(TypedDict):
    run: int
    seed: int
    duration_seconds: float
    iterations: int
    unit: str
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

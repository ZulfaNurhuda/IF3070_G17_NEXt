from pathlib import Path
from typing import NotRequired, TypedDict

from src.core.models import Problem, State
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


def load_problem(path: Path, objective_name: str) -> Problem:
    # TODO: Implementasikan pemuatan instance dari file JSON.
    #   Input: path file instance (bentuknya objek `problem` pada kontrak JSON)
    #   dan objective_name (kunci objectives.OBJECTIVES).
    #   Output: Problem. Ini batas luar sistem: hasil json.load bertipe tak pasti, jadi
    #   validasi semua field (tipe, bilangan bulat positif, id kendaraan unik, eta > 0) dan
    #   raise ValueError berisi pesan jelas bila ada yang salah, sebelum membuat dataclass.
    #   objective_name tidak dikenal juga raise ValueError berisi daftar nama valid.
    raise NotImplementedError


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

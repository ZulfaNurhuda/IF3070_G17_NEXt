import json
from pathlib import Path

from src.experiments.runner import ExperimentResult
from src.storage.encode import experiment_payload


def write_unique(directory: Path, prefix: str, timestamp: int, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    while True:
        path = directory / f"{prefix}_{timestamp}.json"
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            timestamp += 1
        else:
            return path


def write_experiment(experiment: ExperimentResult, directory: Path, name: str) -> Path:
    ship = experiment.problem.ship
    vehicle_count = len(experiment.problem.vehicles)
    prefix = f"{name}_ship{ship.width}x{ship.length}-vehicles{vehicle_count}"
    content = json.dumps(experiment_payload(experiment), ensure_ascii=False, separators=(",", ":"))
    timestamp = int(experiment.created_at.timestamp())
    return write_unique(directory, prefix, timestamp, content + "\n")

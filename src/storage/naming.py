from collections.abc import Mapping
from typing import Final

from src.algorithms.registry import algorithm_parameters, registry_name
from src.experiments.runner import ExperimentResult

SEGMENT_SEPARATOR: Final = "__"
PAIR_SEPARATOR: Final = "_"


def format_value(value: object) -> str:
    if isinstance(value, Mapping):
        return str(value["algorithm"])
    return str(value)


def format_pairs(pairs: Mapping[str, object]) -> str:
    return PAIR_SEPARATOR.join(
        f"{key.replace('_', '-')}={format_value(value)}"
        for key, value in pairs.items()
        if value is not None
    )


def experiment_prefix(experiment: ExperimentResult) -> str:
    ship = experiment.problem.ship
    instance = {
        "ship": f"{ship.width}x{ship.length}",
        "vehicles": len(experiment.problem.vehicles),
    }
    segments = [registry_name(experiment.algorithm), format_pairs(instance)]
    parameters = format_pairs(algorithm_parameters(experiment.algorithm))
    if parameters:
        segments.append(parameters)
    return SEGMENT_SEPARATOR.join(segments)

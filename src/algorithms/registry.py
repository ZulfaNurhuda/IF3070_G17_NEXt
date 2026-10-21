from collections.abc import Callable, Mapping
from typing import Final, get_type_hints

from src.algorithms.base import Algorithm
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.hill_climbing import RandomRestart, SidewaysMove, SteepestAscent, Stochastic
from src.algorithms.simulated_annealing import SimulatedAnnealing

REGISTRY: Final[dict[str, Callable[..., Algorithm]]] = {
    "steepest-ascent": SteepestAscent,
    "sideways-move": SidewaysMove,
    "stochastic": Stochastic,
    "random-restart": RandomRestart,
    "simulated-annealing": SimulatedAnnealing,
    "genetic-algorithm": GeneticAlgorithm,
}


def parameter_types(name: str) -> dict[str, object]:
    if name not in REGISTRY:
        valid_names = ", ".join(sorted(REGISTRY))
        raise ValueError(f"algoritma tidak dikenal: {name}; pilihan: {valid_names}")
    return dict(get_type_hints(REGISTRY[name]))


def nested_algorithm(value: object) -> Algorithm:
    if isinstance(value, str):
        return create_algorithm(value, {})
    if isinstance(value, Mapping):
        nested_name = value.get("algorithm")
        if isinstance(nested_name, str):
            rest = {key: item for key, item in value.items() if key != "algorithm"}
            return create_algorithm(nested_name, rest)
    raise ValueError(
        'algoritma bersarang harus berupa nama algoritma atau objek {"algorithm": nama, ...}'
    )


def create_algorithm(name: str, parameters: Mapping[str, object]) -> Algorithm:
    types = parameter_types(name)
    unknown = sorted(set(parameters) - set(types))
    if unknown:
        valid_names = ", ".join(types) or "tidak ada"
        raise ValueError(
            f"parameter tidak dikenal untuk {name}: {', '.join(unknown)}; pilihan: {valid_names}"
        )
    arguments = {
        key: nested_algorithm(value) if types[key] is Algorithm else value
        for key, value in parameters.items()
    }
    return REGISTRY[name](**arguments)

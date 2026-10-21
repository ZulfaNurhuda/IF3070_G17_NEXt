from collections.abc import Callable, Mapping
from dataclasses import fields, is_dataclass
from typing import Final, get_type_hints

from src.algorithms.base import Algorithm
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.hill_climbing import SidewaysMove, SteepestAscent, Stochastic
from src.algorithms.random_restart import RandomRestart
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

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    name: str
    algorithm: str
    parameters: Mapping[str, object]


RUNS_PER_CONFIGURATION: Final = 3
OFFICIAL_EXPERIMENTS: Final[tuple[ExperimentConfig, ...]] = (
    ExperimentConfig("steepest-ascent", "steepest-ascent", {}),
    ExperimentConfig("sideways-move", "sideways-move", {"max_sideways": 100}),
    ExperimentConfig("stochastic", "stochastic", {}),
    ExperimentConfig(
        "random-restart", "random-restart", {"inner": "steepest-ascent", "max_restart": 10}
    ),
    ExperimentConfig("simulated-annealing", "simulated-annealing", {}),
    ExperimentConfig(
        "genetic-algorithm-generations-50",
        "genetic-algorithm",
        {"population_size": 50, "generations": 50},
    ),
    ExperimentConfig(
        "genetic-algorithm-generations-100",
        "genetic-algorithm",
        {"population_size": 50, "generations": 100},
    ),
    ExperimentConfig(
        "genetic-algorithm-generations-200",
        "genetic-algorithm",
        {"population_size": 50, "generations": 200},
    ),
    ExperimentConfig(
        "genetic-algorithm-population-20",
        "genetic-algorithm",
        {"population_size": 20, "generations": 150},
    ),
    ExperimentConfig(
        "genetic-algorithm-population-50",
        "genetic-algorithm",
        {"population_size": 50, "generations": 150},
    ),
    ExperimentConfig(
        "genetic-algorithm-population-100",
        "genetic-algorithm",
        {"population_size": 100, "generations": 150},
    ),
)

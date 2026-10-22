from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    algorithm: str
    parameters: Mapping[str, object]


RUNS_PER_CONFIGURATION: Final = 3
OFFICIAL_EXPERIMENTS: Final[tuple[ExperimentConfig, ...]] = (
    ExperimentConfig("steepest-ascent", {}),
    ExperimentConfig("sideways-move", {"max_sideways": 100}),
    ExperimentConfig("stochastic", {}),
    ExperimentConfig("random-restart", {"inner": "steepest-ascent", "max_restart": 10}),
    ExperimentConfig("simulated-annealing", {}),
    ExperimentConfig("genetic-algorithm", {"population_size": 50, "generations": 50}),
    ExperimentConfig("genetic-algorithm", {"population_size": 50, "generations": 100}),
    ExperimentConfig("genetic-algorithm", {"population_size": 50, "generations": 200}),
    ExperimentConfig("genetic-algorithm", {"population_size": 20, "generations": 150}),
    ExperimentConfig("genetic-algorithm", {"population_size": 50, "generations": 150}),
    ExperimentConfig("genetic-algorithm", {"population_size": 100, "generations": 150}),
)

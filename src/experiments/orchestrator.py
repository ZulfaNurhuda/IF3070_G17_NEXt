from collections.abc import Iterator

from src.algorithms.registry import create_algorithm
from src.core.models import Problem
from src.experiments.configs import OFFICIAL_EXPERIMENTS, RUNS_PER_CONFIGURATION, ExperimentConfig
from src.experiments.runner import ExperimentResult, execute_runs


def orchestrate_official_experiments(
    problem: Problem, base_seed: int
) -> Iterator[tuple[ExperimentConfig, ExperimentResult]]:
    for config in OFFICIAL_EXPERIMENTS:
        algorithm = create_algorithm(config.algorithm, config.parameters)
        yield config, execute_runs(problem, algorithm, RUNS_PER_CONFIGURATION, base_seed)

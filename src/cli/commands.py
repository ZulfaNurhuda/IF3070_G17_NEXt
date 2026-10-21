import argparse

from src.algorithms.registry import create_algorithm
from src.cli.parameters import parse_parameters
from src.cli.paths import FINAL_OUTPUT, OUTPUT_ROOT
from src.experiments.configs import OFFICIAL_EXPERIMENTS, RUNS_PER_CONFIGURATION
from src.experiments.runner import execute_runs
from src.storage.instance import load_problem
from src.storage.writer import write_experiment


def run_command(arguments: argparse.Namespace) -> None:
    parameters = parse_parameters(arguments.algorithm, arguments.param)
    algorithm = create_algorithm(arguments.algorithm, parameters)
    problem = load_problem(arguments.instance, arguments.objective)
    experiment = execute_runs(problem, algorithm, arguments.runs, arguments.seed)
    print(write_experiment(experiment, OUTPUT_ROOT / arguments.out, arguments.algorithm))


def run_all_command(arguments: argparse.Namespace) -> None:
    problem = load_problem(arguments.instance, arguments.objective)
    total = len(OFFICIAL_EXPERIMENTS)
    for number, config in enumerate(OFFICIAL_EXPERIMENTS, start=1):
        algorithm = create_algorithm(config.algorithm, config.parameters)
        experiment = execute_runs(problem, algorithm, RUNS_PER_CONFIGURATION, arguments.seed)
        path = write_experiment(experiment, OUTPUT_ROOT / FINAL_OUTPUT, config.name)
        print(f"[{number}/{total}] {config.name} -> {path}", flush=True)

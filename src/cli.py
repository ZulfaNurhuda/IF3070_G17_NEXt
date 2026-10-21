import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final, get_args

from src.algorithms.base import Algorithm
from src.algorithms.registry import REGISTRY, create_algorithm, parameter_types
from src.core.objectives import DEFAULT_OBJECTIVE_NAME, OBJECTIVES
from src.experiments.configs import OFFICIAL_EXPERIMENTS, RUNS_PER_CONFIGURATION
from src.experiments.runner import execute_runs
from src.storage.instance import load_problem
from src.storage.results import write_experiment

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_INSTANCE: Final = PROJECT_ROOT / "src" / "instances" / "default.json"
OUTPUT_ROOT: Final = PROJECT_ROOT / "output"
DEFAULT_RUNS: Final = 3
DEFAULT_SEED: Final = 0
DEFAULT_OUTPUT: Final = "scratch"
FINAL_OUTPUT: Final = "final"
OUTPUT_FOLDERS: Final = (DEFAULT_OUTPUT, FINAL_OUTPUT)


def convert_parameter(algorithm: str, key: str, text: str, annotation: object) -> object:
    if annotation is Algorithm:
        return text
    candidates = (annotation, *get_args(annotation))
    for number_type in (int, float):
        if number_type in candidates:
            try:
                return number_type(text)
            except ValueError:
                raise ValueError(
                    f"--param {key}: nilai '{text}' bukan {number_type.__name__}"
                ) from None
    raise ValueError(f"--param {key}: tipe parameter {algorithm} tidak didukung")


def parse_parameters(algorithm: str, pairs: Sequence[str]) -> dict[str, object]:
    types = parameter_types(algorithm)
    parameters: dict[str, object] = {}
    for pair in pairs:
        key, separator, text = pair.partition("=")
        if not separator:
            raise ValueError(f"--param harus berbentuk nama=nilai, bukan '{pair}'")
        if key in parameters:
            raise ValueError(f"--param {key}: diberikan lebih dari sekali")
        parameters[key] = (
            convert_parameter(algorithm, key, text, types[key]) if key in types else text
        )
    return parameters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m src.cli")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="jalankan satu algoritma")
    run.add_argument("--algorithm", required=True, choices=sorted(REGISTRY))
    run.add_argument("--param", action="append", default=[], metavar="NAMA=NILAI")
    run.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    run.add_argument("--out", choices=OUTPUT_FOLDERS, default=DEFAULT_OUTPUT)

    run_all = commands.add_parser("run-all", help="jalankan semua eksperimen resmi ke output/final")

    for command in (run, run_all):
        command.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
        command.add_argument(
            "--objective", choices=sorted(OBJECTIVES), default=DEFAULT_OBJECTIVE_NAME
        )
        command.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


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


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "run":
            run_command(arguments)
        else:
            run_all_command(arguments)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

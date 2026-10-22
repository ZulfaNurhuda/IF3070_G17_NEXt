import argparse
import random
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final, get_args

from src.algorithms.base import Algorithm
from src.algorithms.registry import REGISTRY, create_algorithm, parameter_types
from src.core.objectives import DEFAULT_OBJECTIVE_NAME, OBJECTIVES
from src.experiments.configs import OFFICIAL_EXPERIMENTS, RUNS_PER_CONFIGURATION
from src.experiments.runner import execute_runs
from src.storage.generation import (
    DEFAULT_CAPACITY_RATIO,
    DEFAULT_RANGES,
    GenerationRequest,
    generate_problem,
    write_instance,
)
from src.storage.instance import load_problem
from src.storage.naming import experiment_prefix
from src.storage.results import write_experiment
from src.storage.specification import ATTRIBUTE_KEYS, parse_range, parse_vehicle_specification

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
INSTANCES_DIRECTORY: Final = PROJECT_ROOT / "src" / "instances"
DEFAULT_INSTANCE: Final = INSTANCES_DIRECTORY / "default.json"
OUTPUT_ROOT: Final = PROJECT_ROOT / "output"
DEFAULT_RUNS: Final = 3
DEFAULT_SEED: Final = 0
DEFAULT_SHIP_WIDTH: Final = 10
DEFAULT_SHIP_LENGTH: Final = 20
DEFAULT_RANDOM_VEHICLES: Final = 25
USAGE_EXAMPLE_ALGORITHM: Final = "steepest-ascent"
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

    generate = commands.add_parser("generate", help="buat instance JSON baru di src/instances")
    generate.add_argument("--name", required=True)
    generate.add_argument("--seed", type=int, default=DEFAULT_SEED)
    generate.add_argument("--ship-width", type=int, default=DEFAULT_SHIP_WIDTH)
    generate.add_argument("--ship-length", type=int, default=DEFAULT_SHIP_LENGTH)
    capacity = generate.add_mutually_exclusive_group()
    capacity.add_argument("--capacity", type=int)
    capacity.add_argument("--capacity-ratio", type=float, default=DEFAULT_CAPACITY_RATIO)
    generate.add_argument("--vehicles", type=int, default=DEFAULT_RANDOM_VEHICLES)
    for key in ATTRIBUTE_KEYS:
        generate.add_argument(vehicle_flag(key), dest=f"vehicle_{key}", metavar="N|RENDAH:TINGGI")
    generate.add_argument("--vehicle", action="append", default=[], metavar="NAMA=NILAI,...")
    return parser


def vehicle_flag(key: str) -> str:
    return f"--vehicle-{key.replace('_', '-')}"


def run_command(arguments: argparse.Namespace) -> None:
    parameters = parse_parameters(arguments.algorithm, arguments.param)
    algorithm = create_algorithm(arguments.algorithm, parameters)
    problem = load_problem(arguments.instance, arguments.objective)
    experiment = execute_runs(problem, algorithm, arguments.runs, arguments.seed)
    prefix = experiment_prefix(experiment)
    print(write_experiment(experiment, OUTPUT_ROOT / arguments.out, prefix))


def run_all_command(arguments: argparse.Namespace) -> None:
    problem = load_problem(arguments.instance, arguments.objective)
    total = len(OFFICIAL_EXPERIMENTS)
    for number, config in enumerate(OFFICIAL_EXPERIMENTS, start=1):
        algorithm = create_algorithm(config.algorithm, config.parameters)
        experiment = execute_runs(problem, algorithm, RUNS_PER_CONFIGURATION, arguments.seed)
        prefix = experiment_prefix(experiment)
        path = write_experiment(experiment, OUTPUT_ROOT / FINAL_OUTPUT, prefix)
        print(f"[{number}/{total}] {path}", flush=True)


def generate_command(arguments: argparse.Namespace) -> None:
    overrides = {
        key: parse_range(text, vehicle_flag(key))
        for key in ATTRIBUTE_KEYS
        if (text := getattr(arguments, f"vehicle_{key}")) is not None
    }
    request = GenerationRequest(
        ship_width=arguments.ship_width,
        ship_length=arguments.ship_length,
        capacity=arguments.capacity,
        capacity_ratio=arguments.capacity_ratio,
        random_count=arguments.vehicles,
        ranges={**DEFAULT_RANGES, **overrides},
        specifications=tuple(
            parse_vehicle_specification(text, index)
            for index, text in enumerate(arguments.vehicle, start=1)
        ),
    )
    payload = generate_problem(request, random.Random(arguments.seed))
    path = write_instance(payload, INSTANCES_DIRECTORY, arguments.name).relative_to(PROJECT_ROOT)
    ship = payload["ship"]
    print(
        f"Instance dibuat: {path.as_posix()} ({len(payload['vehicles'])} kendaraan, "
        f"kapal {ship['width']}x{ship['length']}, kapasitas {ship['max_capacity']})"
    )
    print(
        f"Untuk menggunakan instance ini, tambahkan --instance {path.as_posix()} "
        "pada perintah run atau run-all, misalnya:"
    )
    print(
        f"  python -m src.cli run --algorithm {USAGE_EXAMPLE_ALGORITHM} "
        f"--instance {path.as_posix()} --runs {DEFAULT_RUNS} --seed 1 --out {DEFAULT_OUTPUT}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "run":
            run_command(arguments)
        elif arguments.command == "generate":
            generate_command(arguments)
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

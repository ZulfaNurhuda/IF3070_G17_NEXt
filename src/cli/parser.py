import argparse
from pathlib import Path
from typing import Final

from src.algorithms.registry import REGISTRY
from src.cli.paths import DEFAULT_INSTANCE, DEFAULT_OUTPUT, OUTPUT_FOLDERS
from src.core.objectives import DEFAULT_OBJECTIVE_NAME, OBJECTIVES

DEFAULT_RUNS: Final = 3
DEFAULT_SEED: Final = 0


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

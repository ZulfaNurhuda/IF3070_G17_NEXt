import random
import time
from dataclasses import dataclass
from datetime import datetime

from src.algorithms.base import Algorithm, SearchResult
from src.core.models import Problem


@dataclass(frozen=True, slots=True)
class RunRecord:
    run: int
    seed: int
    duration_seconds: float
    result: SearchResult


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    problem: Problem
    algorithm_name: str
    algorithm: Algorithm
    created_at: datetime
    runs: tuple[RunRecord, ...]


def execute_runs(
    problem: Problem, algorithm_name: str, algorithm: Algorithm, runs: int, base_seed: int
) -> ExperimentResult:
    if runs < 1:
        raise ValueError("runs harus minimal 1")
    created_at = datetime.now()
    records: list[RunRecord] = []
    for run_number in range(1, runs + 1):
        seed = base_seed + run_number
        started = time.perf_counter()
        result = algorithm.run(problem, random.Random(seed))
        duration = time.perf_counter() - started
        records.append(RunRecord(run_number, seed, duration, result))
    return ExperimentResult(problem, algorithm_name, algorithm, created_at, tuple(records))

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


def run_experiment(
    problem: Problem, algorithm_name: str, algorithm: Algorithm, runs: int, base_seed: int
) -> ExperimentResult:
    # TODO: Implementasikan eksekusi satu eksperimen (satu konfigurasi, banyak run).
    #   Input: problem, algorithm_name, algorithm, runs, base_seed. Output: ExperimentResult.
    #   Langkah: untuk run ke-k (mulai 1) buat rng = random.Random(base_seed + k); ukur
    #   durasi dengan time.perf_counter() di sekitar algorithm.run(problem, rng); simpan
    #   RunRecord(run=k, seed=base_seed + k, duration_seconds, result).
    #   created_at diisi datetime.now() sekali di awal eksperimen.
    raise NotImplementedError


def run_official_experiments(problem: Problem, base_seed: int) -> tuple[ExperimentResult, ...]:
    # TODO: Implementasikan eksekusi seluruh eksperimen resmi (perintah run-all).
    #   Input: problem dan base_seed. Output: satu ExperimentResult per ExperimentConfig di
    #   configs.OFFICIAL_EXPERIMENTS, dengan urutan yang sama.
    #   Langkah: untuk tiap config, buat algoritma lewat registry.create_algorithm(
    #   config.algorithm, config.parameters, problem) lalu panggil run_experiment dengan
    #   config.runs. Total 33 run (HC 4 x 3, SA 3, GA 6 konfigurasi x 3).
    raise NotImplementedError

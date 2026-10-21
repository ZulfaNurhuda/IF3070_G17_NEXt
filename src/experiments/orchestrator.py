from src.core.models import Problem
from src.experiments.runner import ExperimentResult


def orchestrate_official_experiments(
    problem: Problem, base_seed: int
) -> tuple[ExperimentResult, ...]:
    # TODO: Implementasikan pengaturan seluruh eksperimen resmi (perintah run-all).
    #   Input: problem dan base_seed. Output: satu ExperimentResult per ExperimentConfig di
    #   configs.OFFICIAL_EXPERIMENTS, dengan urutan yang sama, sehingga pemanggil bisa
    #   memasangkan tiap hasil dengan config.name untuk nama file.
    #   Langkah: untuk tiap config, buat algoritma lewat registry.create_algorithm(
    #   config.algorithm, config.parameters), lalu serahkan ke runner.execute_runs
    #   bersama configs.RUNS_PER_CONFIGURATION dan base_seed. Modul ini hanya mengatur;
    #   eksekusi run dan pengukuran durasi tetap tugas execute_runs.
    #   Total 33 run (HC 4 x 3, SA 3, GA 6 konfigurasi x 3).
    raise NotImplementedError

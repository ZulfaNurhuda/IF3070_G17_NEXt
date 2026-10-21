from collections.abc import Callable, Mapping
from typing import Final

from src.algorithms.base import Algorithm
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.hill_climbing import RandomRestart, SidewaysMove, SteepestAscent, Stochastic
from src.algorithms.simulated_annealing import SimulatedAnnealing

REGISTRY: Final[dict[str, Callable[..., Algorithm]]] = {
    "steepest-ascent": SteepestAscent,
    "sideways-move": SidewaysMove,
    "stochastic": Stochastic,
    "random-restart": RandomRestart,
    "simulated-annealing": SimulatedAnnealing,
    "genetic-algorithm": GeneticAlgorithm,
}


def create_algorithm(name: str, parameters: Mapping[str, object]) -> Algorithm:
    # TODO: Implementasikan pembuatan algoritma dari nama dan parameter.
    #   Input: name (kunci REGISTRY), parameters (nilai sudah bertipe benar).
    #   Output: instance Algorithm yang siap dijalankan.
    #   Langkah: bila name tidak ada di REGISTRY, raise ValueError berisi daftar nama valid.
    #   Parameter yang tidak diisi memakai default dataclass (random-restart sudah
    #   default ke steepest-ascent; simulated-annealing menghitung sendiri suhu yang
    #   bernilai None di awal run). Aturan algoritma bersarang berlaku umum, bukan khusus
    #   random-restart: nilai parameter yang berupa nama algoritma (string kunci REGISTRY)
    #   atau mapping {"algorithm": <nama>, ...parameter lain} dibuat lewat panggilan
    #   create_algorithm rekursif, sehingga bentuk "params" yang ditulis ke JSON hasil
    #   eksperimen bisa dipakai ulang apa adanya. Nama di dalamnya juga harus divalidasi.
    raise NotImplementedError

from collections.abc import Callable, Mapping
from typing import Final

from src.algorithms.base import Algorithm
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.algorithms.hill_climbing import RandomRestart, SidewaysMove, SteepestAscent, Stochastic
from src.algorithms.simulated_annealing import SimulatedAnnealing
from src.core.models import Problem

REGISTRY: Final[dict[str, Callable[..., Algorithm]]] = {
    "steepest-ascent": SteepestAscent,
    "sideways-move": SidewaysMove,
    "stochastic": Stochastic,
    "random-restart": RandomRestart,
    "simulated-annealing": SimulatedAnnealing,
    "genetic-algorithm": GeneticAlgorithm,
}


def create_algorithm(name: str, parameters: Mapping[str, object], problem: Problem) -> Algorithm:
    # TODO: Implementasikan pembuatan algoritma dari nama dan parameter.
    #   Input: name (kunci REGISTRY), parameters (nilai sudah bertipe benar), problem.
    #   Output: instance Algorithm yang siap dijalankan.
    #   Langkah: bila name tidak ada di REGISTRY, raise ValueError berisi daftar nama valid.
    #   Untuk "random-restart", parameter "inner" berupa nama algoritma; buat algoritma
    #   dalamnya lewat REGISTRY lalu teruskan sebagai argumen `inner`.
    #   Untuk "simulated-annealing", panggil .resolved(problem) agar parameter otomatis
    #   terisi sebelum dikembalikan.
    raise NotImplementedError

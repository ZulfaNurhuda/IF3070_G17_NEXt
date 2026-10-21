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
    #   Untuk "random-restart", parameter "inner" berupa nama algoritma; buat algoritma
    #   dalamnya lewat REGISTRY lalu teruskan sebagai argumen `inner`. Parameter yang
    #   tidak diisi memakai default dataclass; simulated-annealing menghitung sendiri suhu
    #   yang bernilai None di awal run, jadi tidak ada langkah khusus untuknya.
    raise NotImplementedError

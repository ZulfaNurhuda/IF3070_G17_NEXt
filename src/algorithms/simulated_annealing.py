from __future__ import annotations

import random
from dataclasses import dataclass

from src.algorithms.base import SearchResult
from src.core.models import Problem


def acceptance_probability(delta: float, temperature: float) -> float:
    # TODO: Implementasikan peluang penerimaan move SA.
    #   Input: delta = value(next) - value(current), temperature > 0.
    #   Output: min(1.0, e^(delta / temperature)). Untuk delta > 0 langsung kembalikan 1.0
    #   (hindari overflow math.exp). Nilai ini yang dicatat di history sebagai
    #   acceptance_probability untuk plot yang diminta spek.
    raise NotImplementedError


@dataclass(frozen=True, slots=True)
class SimulatedAnnealing:
    initial_temperature: float | None = None
    minimum_temperature: float | None = None
    max_iterations: int = 20000
    cooling_rate: float | None = None
    stuck_patience: int = 200

    def resolved(self, problem: Problem) -> SimulatedAnnealing:
        # TODO: Implementasikan pengisian parameter otomatis dari instance.
        #   Output: SimulatedAnnealing baru (dataclasses.replace) dengan semua field terisi.
        #   initial_temperature = 2 x rata-rata shipping_fee; minimum_temperature = 0.01 x
        #   rata-rata shipping_fee; cooling_rate = (minimum_temperature / initial_temperature)
        #   ** (1 / max_iterations). Nilai yang sudah diberikan pengguna tidak ditimpa.
        #   Nilai hasil resolusi inilah yang disimpan di params JSON.
        raise NotImplementedError

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan SIMULATED-ANNEALING AIMA dengan schedule geometrik.
        #   Pra-syarat: self sudah resolved(problem), semua field bukan None.
        #   Langkah: current = random_state; T = initial_temperature; ulangi sampai
        #   T < minimum_temperature atau iterasi mencapai max_iterations: ambil
        #   random_neighbor; delta = value(next) - value(current); terima bila delta > 0,
        #   selain itu terima dengan peluang acceptance_probability(delta, T); lalu
        #   T = T * cooling_rate. Bila random_neighbor mengembalikan None, iterasi dihitung
        #   tanpa perubahan. Kembalikan state saat berhenti, bukan best-so-far (sesuai AIMA).
        #   Catat history (iteration, value, acceptance_probability), steps untuk move yang
        #   diterima, iterations, evaluations, dan extra: stuck_events, longest_streak,
        #   best_seen_value.
        #   Stuck: state tidak berubah selama stuck_patience iterasi berturut-turut = 1
        #   event; streak yang berlanjut tidak dihitung ulang; move diterima mereset streak.
        raise NotImplementedError

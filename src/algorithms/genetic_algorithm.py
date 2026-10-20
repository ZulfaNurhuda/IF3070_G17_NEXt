import random
from collections.abc import Sequence
from dataclasses import dataclass

from src.algorithms.base import SearchResult
from src.core.models import Problem, State


def select_parent(
    population: Sequence[State], fitness: Sequence[float], rng: random.Random
) -> State:
    # TODO: Implementasikan seleksi fitness-proportionate (AIMA RANDOM-SELECTION).
    #   Input: population, fitness (sejajar dengan population), rng. Output: satu State.
    #   Peluang terpilih proporsional dengan fitness. Bila total fitness 0, pilih seragam.
    raise NotImplementedError


def crossover(first: State, second: State, problem: Problem, rng: random.Random) -> State:
    # TODO: Implementasikan REPRODUCE AIMA dengan satu titik potong.
    #   Input: dua parent valid, problem, rng. Output: anak yang selalu valid.
    #   Langkah: urutkan kendaraan berdasarkan id (urutan tetap); pilih titik potong c acak;
    #   anak dimulai dari State kosong; kendaraan sebelum c diambil dari first, sisanya dari
    #   second, masing-masing lewat evaluator.try_place. Gen yang gagal ditempatkan
    #   tetap di luar kapal. Bagian dari first selalu muat (subset state valid).
    #   Bila fill_after_crossover aktif, jalankan pass greedy.
    raise NotImplementedError


def mutate(state: State, problem: Problem, rng: random.Random) -> State:
    # TODO: Implementasikan mutasi satu move acak.
    #   Input: state valid, problem, rng. Output: State valid.
    #   Langkah: ambil neighbors.random_neighbor; bila mengembalikan None, kembalikan state
    #   apa adanya; selain itu kembalikan state.apply(move).
    raise NotImplementedError


@dataclass(frozen=True, slots=True)
class GeneticAlgorithm:
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.3
    elitism_count: int = 2
    fill_after_crossover: bool = False

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan GENETIC-ALGORITHM AIMA (generasional).
        #   Input: problem dan rng. Output: SearchResult.
        #   Langkah: populasi awal = population_size x random_state. Untuk tiap generasi:
        #   salin elitism_count individu terbaik; isi sisa populasi dengan: pilih dua parent
        #   lewat select_parent (fitness = problem.value), child = crossover, lalu dengan
        #   peluang mutation_rate child = mutate(child). Berhenti setelah `generations`.
        #   initial_state = individu terbaik generasi 0; final_state = individu terbaik
        #   generasi terakhir.
        #   Catat history per generasi (iteration, value = terbaik, maximum_value,
        #   average_value), steps = selisih individu terbaik antar generasi (satu step per
        #   generasi, changes berisi kendaraan yang berubah), iterations = generasi,
        #   evaluations = populasi x generasi, dan extra bila ada.
        raise NotImplementedError

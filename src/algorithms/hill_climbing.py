import random
from dataclasses import dataclass

from src.algorithms.base import Algorithm, SearchResult
from src.core.models import Problem


@dataclass(frozen=True, slots=True)
class SteepestAscent:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan HILL-CLIMBING AIMA (steepest ascent).
        #   Input: problem dan rng (untuk state awal dan tie-break). Output: SearchResult.
        #   Langkah: (1) current = random_state(problem, rng); (2) ulangi: enumerasi
        #   neighbor lewat enumerate_neighbors, pilih yang problem.value tertinggi (bila
        #   ada beberapa yang sama, pilih acak dengan rng); (3) bila nilainya <= nilai
        #   current, berhenti dan kembalikan current; selain itu pindah ke neighbor itu.
        #   Catat: history per iterasi (iteration, value), steps untuk setiap move yang
        #   diterima, iterations, evaluations (jumlah panggilan problem.value),
        #   initial_state, dan final_state. Tanpa parameter; pasti berhenti karena
        #   nilai naik strict.
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class SidewaysMove:
    max_sideways: int = 100

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan hill-climbing dengan sideways move (batas berturut-turut).
        #   Input: problem dan rng. Output: SearchResult.
        #   Langkah: seperti SteepestAscent, tetapi bila neighbor terbaik bernilai SAMA
        #   dengan current, pindah ke neighbor itu (sideways) selama sideways berturut-turut
        #   < max_sideways. Counter berturut-turut direset ke 0 setiap ada perbaikan strict.
        #   Berhenti bila neighbor terbaik lebih buruk, atau sideways berturut-turut sudah
        #   mencapai max_sideways.
        #   Catat extra: sideways_used (total sideways yang dilakukan), selain history,
        #   steps, iterations, dan evaluations.
        #   Catatan: batas sideways dihitung berturut-turut, mengikuti AIMA.
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Stochastic:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan stochastic hill climbing (pilih acak di antara uphill move).
        #   Input: problem dan rng. Output: SearchResult.
        #   Langkah: (1) current = random_state; (2) kumpulkan semua neighbor dari
        #   enumerate_neighbors yang nilainya STRICT lebih baik dari current; (3) bila
        #   kosong, berhenti; selain itu pilih satu secara seragam acak dengan rng dan
        #   pindah. Catat history, steps, iterations, dan evaluations.
        #   Ini bukan first-choice hill climbing.
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class RandomRestart:
    inner: Algorithm
    max_restart: int = 10

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        # TODO: Implementasikan random-restart hill climbing (AIMA).
        #   Input: problem dan rng. Output: SearchResult dengan final_state terbaik.
        #   Langkah: ulangi sampai max_restart restart: jalankan self.inner.run dengan rng
        #   yang sama (state awal acak baru tiap restart), simpan hasil dengan nilai final
        #   tertinggi. history dan steps disambung antar restart (iteration berlanjut,
        #   tidak direset).
        #   extra: restarts, serta iterations_restart_0, iterations_restart_1, dst
        #   (jumlah iterasi tiap restart; extra hanya menampung float).
        raise NotImplementedError

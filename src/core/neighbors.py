import random
from collections.abc import Iterator
from typing import Final

from src.core.models import Move, Problem, State

MAX_RANDOM_NEIGHBOR_ATTEMPTS: Final = 100


def enumerate_neighbors(state: State, problem: Problem) -> Iterator[Move]:
    # TODO: Implementasikan enumerasi seluruh neighbor valid dari `state`.
    #   Input: state valid dan problem. Output: iterator Move; setiap Move bila di-apply
    #   menghasilkan State yang lolos is_valid.
    #   Langkah: (1) swap tiap pasangan kendaraan (dalam/luar kapal); (2) relocate tiap
    #   kendaraan ke semua (x, y, orientation) valid serta ke "luar kapal"; (3) rotate
    #   tiap kendaraan yang ada di dalam kapal.
    #   Invarian: Move yang menyebabkan overlap, keluar geladak, atau melebihi kapasitas
    #   tidak boleh di-yield. Move yang tidak mengubah apa pun juga tidak di-yield.
    #   Dipakai oleh steepest-ascent, sideways-move, dan stochastic.
    raise NotImplementedError


def random_neighbor(
    state: State,
    problem: Problem,
    rng: random.Random,
    max_attempts: int = MAX_RANDOM_NEIGHBOR_ATTEMPTS,
) -> Move | None:
    # TODO: Implementasikan sampel acak satu neighbor valid.
    #   Input: state, problem, rng, max_attempts. Output: sebuah Move valid, atau None bila
    #   setelah max_attempts percobaan tidak ditemukan neighbor valid.
    #   Langkah: pilih jenis move (swap, relocate, rotate) dan parameternya secara acak
    #   lewat rng, bentuk Move, terima hanya bila is_valid(state.apply(move)); selain itu
    #   ulangi. Dilarang memakai random global.
    #   Dipakai oleh simulated-annealing dan mutasi GA.
    raise NotImplementedError

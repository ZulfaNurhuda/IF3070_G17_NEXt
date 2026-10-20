import random

from src.core.models import Problem, State


def random_state(problem: Problem, rng: random.Random) -> State:
    # TODO: Implementasikan pembuatan initial state acak yang selalu valid.
    #   Input: problem dan rng. Output: State valid.
    #   Langkah: mulai dari State kosong (semua kendaraan di luar kapal, selalu valid);
    #   acak urutan kendaraan dengan rng; untuk tiap kendaraan, coba satu posisi dan
    #   orientasi acak lewat evaluator.try_place; bila gagal, kendaraan tetap di luar.
    #   Dilarang memakai random global.
    raise NotImplementedError

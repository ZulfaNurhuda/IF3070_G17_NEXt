import math
import random
from dataclasses import dataclass
from statistics import fmean
from typing import Final

from src.core.models import Problem, State
from src.core.sampling import random_successor

TEMPERATURE_SAMPLES: Final = 100
INITIAL_TEMPERATURE_FACTOR: Final = 2.0
MINIMUM_TEMPERATURE_FACTOR: Final = 0.01
TEMPERATURE_RATIO: Final = MINIMUM_TEMPERATURE_FACTOR / INITIAL_TEMPERATURE_FACTOR


# Sumber: skala suhu awal SA diadaptasi dari penetapan suhu berdasarkan rasio penerimaan awal.
#   W. Ben-Ameur, "Computing the initial temperature of simulated annealing,"
#   Comput. Optim. Appl., vol. 29, no. 3, pp. 369-385, Dec. 2004,
#   doi: 10.1023/B:COAP.0000044187.23143.BD.
def temperature_scale(state: State, problem: Problem, rng: random.Random) -> tuple[float, int]:
    value = problem.value(state)
    deltas: list[float] = []
    for _ in range(TEMPERATURE_SAMPLES):
        successor = random_successor(state, problem, rng)
        if successor is not None:
            deltas.append(problem.value(successor[1]) - value)
    magnitudes = (
        [-delta for delta in deltas if delta < 0]
        or [abs(delta) for delta in deltas if delta != 0]
        or [1.0]
    )
    return fmean(magnitudes), len(deltas)


@dataclass(frozen=True, slots=True)
class Temperatures:
    initial: float
    minimum: float
    cooling_rate: float
    scale: float | None
    samples: int


def resolve_schedule(
    initial: float | None,
    minimum: float | None,
    cooling_rate: float | None,
    max_iterations: int,
    state: State,
    problem: Problem,
    rng: random.Random,
) -> Temperatures:
    scale: float | None = None
    samples = 0
    if initial is None:
        if minimum is None:
            scale, samples = temperature_scale(state, problem, rng)
            initial = INITIAL_TEMPERATURE_FACTOR * scale
            minimum = MINIMUM_TEMPERATURE_FACTOR * scale
        else:
            initial = minimum / TEMPERATURE_RATIO
    elif minimum is None:
        minimum = initial * TEMPERATURE_RATIO
    if not 0 < minimum < initial < math.inf:
        raise ValueError(
            "suhu harus berhingga dan memenuhi 0 < minimum_temperature < initial_temperature"
        )
    if cooling_rate is None:
        cooling_rate = (minimum / initial) ** (1 / max_iterations)
    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate harus berada di antara 0 dan 1")
    return Temperatures(initial, minimum, cooling_rate, scale, samples)

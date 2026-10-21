import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from statistics import fmean
from typing import Final

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.initial import random_state
from src.core.models import Problem, State
from src.core.neighbors import random_successor

TEMPERATURE_SAMPLES: Final = 100
INITIAL_TEMPERATURE_FACTOR: Final = 2.0
MINIMUM_TEMPERATURE_FACTOR: Final = 0.01
TEMPERATURE_RATIO: Final = MINIMUM_TEMPERATURE_FACTOR / INITIAL_TEMPERATURE_FACTOR


def acceptance_probability(delta: float, temperature: float) -> float:
    if delta > 0:
        return 1.0
    return math.exp(delta / temperature)


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


def stuck_runs(history: Sequence[HistoryRecord], patience: int) -> tuple[int, int]:
    events = 0
    longest = 0
    streak = 0
    for before, after in pairwise(record.value for record in history):
        if after == before:
            streak += 1
            if streak == patience:
                events += 1
            longest = max(longest, streak)
        else:
            streak = 0
    return events, longest


@dataclass(frozen=True, slots=True)
class SimulatedAnnealing:
    initial_temperature: float | None = None
    minimum_temperature: float | None = None
    max_iterations: int = 20000
    cooling_rate: float | None = None
    stuck_patience: int = 200

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations harus minimal 1")
        if self.stuck_patience < 1:
            raise ValueError("stuck_patience harus minimal 1")

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        current = random_state(problem, rng)
        initial_state = current
        current_value = problem.value(current)
        schedule = resolve_schedule(
            self.initial_temperature,
            self.minimum_temperature,
            self.cooling_rate,
            self.max_iterations,
            current,
            problem,
            rng,
        )
        evaluations = 1 + schedule.samples
        temperature = schedule.initial
        best_seen_value = current_value
        iteration = 0
        steps: list[Step] = []
        history = [HistoryRecord(iteration=0, value=current_value)]
        while iteration < self.max_iterations and temperature >= schedule.minimum:
            successor = random_successor(current, problem, rng)
            if successor is None:
                break
            iteration += 1
            move, next_state = successor
            next_value = problem.value(next_state)
            evaluations += 1
            best_seen_value = max(best_seen_value, next_value)
            delta = next_value - current_value
            probability = acceptance_probability(delta, temperature)
            if delta > 0 or rng.random() < probability:
                current, current_value = next_state, next_value
                steps.append(Step(iteration=iteration, changes=move))
            history.append(
                HistoryRecord(
                    iteration=iteration,
                    value=current_value,
                    metrics={"acceptance_probability": probability},
                )
            )
            temperature *= schedule.cooling_rate
        stuck_events, longest_streak = stuck_runs(history, self.stuck_patience)
        extra = {
            "stuck_events": float(stuck_events),
            "stuck_frequency": stuck_events / iteration if iteration else 0.0,
            "longest_streak": float(longest_streak),
            "best_seen_value": best_seen_value,
            "initial_temperature": schedule.initial,
            "minimum_temperature": schedule.minimum,
            "cooling_rate": schedule.cooling_rate,
        }
        if schedule.scale is not None:
            extra["temperature_scale"] = schedule.scale
        return SearchResult(
            initial_state=initial_state,
            final_state=current,
            iterations=iteration,
            evaluations=evaluations,
            history=tuple(history),
            steps=tuple(steps),
            extra=extra,
        )

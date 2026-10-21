import math
import random
from dataclasses import dataclass
from statistics import fmean
from typing import Final

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.initial import random_state
from src.core.models import Problem, State
from src.core.neighbors import random_successor

TEMPERATURE_SAMPLES: Final = 100


def acceptance_probability(delta: float, temperature: float) -> float:
    if delta > 0:
        return 1.0
    return math.exp(delta / temperature)


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
class SimulatedAnnealing:
    initial_temperature: float | None = None
    minimum_temperature: float | None = None
    max_iterations: int = 20000
    cooling_rate: float | None = None
    stuck_patience: int = 200

    def schedule(self, scale: float) -> tuple[float, float, float]:
        if self.max_iterations < 1:
            raise ValueError("max_iterations harus minimal 1")
        if self.stuck_patience < 1:
            raise ValueError("stuck_patience harus minimal 1")
        initial_temperature = self.initial_temperature
        if initial_temperature is None:
            initial_temperature = 2.0 * scale
        minimum_temperature = self.minimum_temperature
        if minimum_temperature is None:
            minimum_temperature = 0.01 * scale
        if not 0 < minimum_temperature < initial_temperature < math.inf:
            raise ValueError(
                "suhu harus berhingga dan memenuhi 0 < minimum_temperature < initial_temperature"
            )
        cooling_rate = self.cooling_rate
        if cooling_rate is None:
            cooling_rate = (minimum_temperature / initial_temperature) ** (1 / self.max_iterations)
        if not 0 < cooling_rate < 1:
            raise ValueError("cooling_rate harus berada di antara 0 dan 1")
        return initial_temperature, minimum_temperature, cooling_rate

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        current = random_state(problem, rng)
        initial_state = current
        current_value = problem.value(current)
        evaluations = 1
        scale = 1.0
        if self.initial_temperature is None or self.minimum_temperature is None:
            scale, sampled = temperature_scale(current, problem, rng)
            evaluations += sampled
        initial_temperature, minimum_temperature, cooling_rate = self.schedule(scale)
        temperature = initial_temperature
        best_seen_value = current_value
        stuck_streak = 0
        stuck_events = 0
        longest_streak = 0
        iteration = 0
        steps: list[Step] = []
        history = [HistoryRecord(iteration=0, value=current_value)]
        while iteration < self.max_iterations and temperature >= minimum_temperature:
            iteration += 1
            previous_value = current_value
            successor = random_successor(current, problem, rng)
            probability: float | None = None
            if successor is not None:
                move, next_state = successor
                next_value = problem.value(next_state)
                evaluations += 1
                best_seen_value = max(best_seen_value, next_value)
                delta = next_value - current_value
                probability = acceptance_probability(delta, temperature)
                if delta > 0 or rng.random() < probability:
                    current, current_value = next_state, next_value
                    steps.append(Step(iteration=iteration, changes=move))
            if current_value == previous_value:
                stuck_streak += 1
                if stuck_streak == self.stuck_patience:
                    stuck_events += 1
                longest_streak = max(longest_streak, stuck_streak)
            else:
                stuck_streak = 0
            history.append(
                HistoryRecord(
                    iteration=iteration,
                    value=current_value,
                    acceptance_probability=probability,
                )
            )
            temperature *= cooling_rate
        return SearchResult(
            initial_state=initial_state,
            final_state=current,
            iterations=iteration,
            evaluations=evaluations,
            history=tuple(history),
            steps=tuple(steps),
            extra={
                "stuck_events": float(stuck_events),
                "stuck_frequency": stuck_events / iteration if iteration else 0.0,
                "longest_streak": float(longest_streak),
                "best_seen_value": best_seen_value,
                "temperature_scale": scale,
                "initial_temperature": initial_temperature,
                "minimum_temperature": minimum_temperature,
                "cooling_rate": cooling_rate,
            },
        )

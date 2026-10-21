import math
import random
from dataclasses import dataclass

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.initial import random_state
from src.core.models import Problem
from src.core.neighbors import random_successor


def acceptance_probability(delta: float, temperature: float) -> float:
    if delta > 0:
        return 1.0
    return math.exp(delta / temperature)


@dataclass(frozen=True, slots=True)
class SimulatedAnnealing:
    initial_temperature: float | None = None
    minimum_temperature: float | None = None
    max_iterations: int = 20000
    cooling_rate: float | None = None
    stuck_patience: int = 200

    def schedule(self, problem: Problem) -> tuple[float, float, float]:
        if self.max_iterations < 1:
            raise ValueError("max_iterations harus minimal 1")
        if self.stuck_patience < 1:
            raise ValueError("stuck_patience harus minimal 1")
        average_fee = sum(vehicle.shipping_fee for vehicle in problem.vehicles) / len(
            problem.vehicles
        )
        initial_temperature = self.initial_temperature
        if initial_temperature is None:
            initial_temperature = 2.0 * average_fee
        minimum_temperature = self.minimum_temperature
        if minimum_temperature is None:
            minimum_temperature = 0.01 * average_fee
        if not 0 < minimum_temperature < initial_temperature:
            raise ValueError("suhu harus memenuhi 0 < minimum_temperature < initial_temperature")
        cooling_rate = self.cooling_rate
        if cooling_rate is None:
            cooling_rate = (minimum_temperature / initial_temperature) ** (1 / self.max_iterations)
        if not 0 < cooling_rate < 1:
            raise ValueError("cooling_rate harus berada di antara 0 dan 1")
        return initial_temperature, minimum_temperature, cooling_rate

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        initial_temperature, minimum_temperature, cooling_rate = self.schedule(problem)
        current = random_state(problem, rng)
        initial_state = current
        current_value = problem.value(current)
        evaluations = 1
        temperature = initial_temperature
        best_seen_value = current_value
        stuck_streak = 0
        stuck_events = 0
        longest_streak = 0
        iteration = 0
        steps: list[Step] = []
        history: list[HistoryRecord] = [
            HistoryRecord(iteration=0, value=current_value, acceptance_probability=0.0)
        ]
        while iteration < self.max_iterations and temperature >= minimum_temperature:
            iteration += 1
            successor = random_successor(current, problem, rng)
            probability = 0.0
            accepted = False
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
                    accepted = True
            if accepted:
                stuck_streak = 0
            else:
                stuck_streak += 1
                if stuck_streak == self.stuck_patience:
                    stuck_events += 1
                longest_streak = max(longest_streak, stuck_streak)
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
                "longest_streak": float(longest_streak),
                "best_seen_value": best_seen_value,
                "initial_temperature": initial_temperature,
                "minimum_temperature": minimum_temperature,
                "cooling_rate": cooling_rate,
            },
        )

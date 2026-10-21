from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.initial import random_state
from src.core.models import Move, Problem
from src.core.neighbors import random_neighbor


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

    def resolved(self, problem: Problem) -> SimulatedAnnealing:
        if not problem.vehicles:
            raise ValueError("problem tidak memiliki kendaraan")
        if self.max_iterations < 1:
            raise ValueError("max_iterations harus minimal 1")
        average_fee = sum(vehicle.shipping_fee for vehicle in problem.vehicles) / len(
            problem.vehicles
        )
        initial_temperature = self.initial_temperature
        if initial_temperature is None:
            initial_temperature = 2.0 * average_fee
        minimum_temperature = self.minimum_temperature
        if minimum_temperature is None:
            minimum_temperature = 0.01 * average_fee
        cooling_rate = self.cooling_rate
        if cooling_rate is None:
            cooling_rate = (minimum_temperature / initial_temperature) ** (1 / self.max_iterations)
        return replace(
            self,
            initial_temperature=initial_temperature,
            minimum_temperature=minimum_temperature,
            cooling_rate=cooling_rate,
        )

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        initial_temperature = self.initial_temperature
        minimum_temperature = self.minimum_temperature
        cooling_rate = self.cooling_rate
        if initial_temperature is None or minimum_temperature is None or cooling_rate is None:
            raise ValueError("SimulatedAnnealing harus resolved terlebih dahulu")
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
            move = random_neighbor(current, problem, rng)
            next_state = current
            next_value = current_value
            probability = 0.0
            accepted_move: Move | None = None
            if move is not None:
                next_state = current.apply(move)
                next_value = problem.value(next_state)
                evaluations += 1
                best_seen_value = max(best_seen_value, next_value)
                delta = next_value - current_value
                probability = acceptance_probability(delta, temperature)
                if delta > 0 or rng.random() < probability:
                    accepted_move = move
            if accepted_move is not None:
                current = next_state
                current_value = next_value
                steps.append(Step(iteration=iteration, changes=accepted_move))
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
            },
        )
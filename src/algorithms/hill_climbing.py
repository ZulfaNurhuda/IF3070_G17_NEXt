import random
from collections.abc import Callable
from dataclasses import dataclass, replace
from itertools import pairwise

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.initial import random_state
from src.core.models import Move, Problem, State
from src.core.neighbors import successors

type Candidate = tuple[Move, State, float]
type Choice = Callable[[float, list[Candidate], random.Random], Candidate | None]


def scored_successors(state: State, problem: Problem) -> list[Candidate]:
    return [
        (move, successor, problem.value(successor))
        for move, successor in successors(state, problem)
    ]


def best_candidates(candidates: list[Candidate]) -> tuple[float, list[Candidate]]:
    best_value = max(candidate[2] for candidate in candidates)
    return best_value, [candidate for candidate in candidates if candidate[2] == best_value]


def choose_steepest(
    current_value: float, candidates: list[Candidate], rng: random.Random
) -> Candidate | None:
    if not candidates:
        return None
    best_value, best = best_candidates(candidates)
    return rng.choice(best) if best_value > current_value else None


def choose_stochastic(
    current_value: float, candidates: list[Candidate], rng: random.Random
) -> Candidate | None:
    improving = [candidate for candidate in candidates if candidate[2] > current_value]
    return rng.choice(improving) if improving else None


def climb(problem: Problem, rng: random.Random, choose: Choice) -> SearchResult:
    current = random_state(problem, rng)
    initial_state = current
    current_value = problem.value(current)
    evaluations = 1
    history = [HistoryRecord(iteration=0, value=current_value)]
    steps: list[Step] = []
    iteration = 0
    while True:
        candidates = scored_successors(current, problem)
        evaluations += len(candidates)
        chosen = choose(current_value, candidates, rng)
        if chosen is None:
            break
        move, current, current_value = chosen
        iteration += 1
        steps.append(Step(iteration=iteration, changes=move))
        history.append(HistoryRecord(iteration=iteration, value=current_value))
    return SearchResult(
        initial_state=initial_state,
        final_state=current,
        iterations=iteration,
        evaluations=evaluations,
        history=tuple(history),
        steps=tuple(steps),
        extra={},
    )


@dataclass(frozen=True, slots=True)
class SteepestAscent:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        return climb(problem, rng, choose_steepest)


def sideways_chooser(max_sideways: int) -> Choice:
    sideways_streak = 0

    def choose(
        current_value: float, candidates: list[Candidate], rng: random.Random
    ) -> Candidate | None:
        nonlocal sideways_streak
        if not candidates:
            return None
        best_value, best = best_candidates(candidates)
        if best_value < current_value:
            return None
        if best_value == current_value:
            if sideways_streak >= max_sideways:
                return None
            sideways_streak += 1
        else:
            sideways_streak = 0
        return rng.choice(best)

    return choose


@dataclass(frozen=True, slots=True)
class SidewaysMove:
    max_sideways: int = 100

    def __post_init__(self) -> None:
        if self.max_sideways < 0:
            raise ValueError("max_sideways harus non-negatif")

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        result = climb(problem, rng, sideways_chooser(self.max_sideways))
        values = [record.value for record in result.history]
        sideways_used = sum(1 for before, after in pairwise(values) if before == after)
        return replace(result, extra={"sideways_used": float(sideways_used)})


@dataclass(frozen=True, slots=True)
class Stochastic:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        return climb(problem, rng, choose_stochastic)

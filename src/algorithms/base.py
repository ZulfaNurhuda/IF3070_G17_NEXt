import random
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from src.core.models import Move, Problem, State


@dataclass(frozen=True, slots=True)
class HistoryRecord:
    iteration: int
    value: float
    acceptance_probability: float | None = None
    average_value: float | None = None


@dataclass(frozen=True, slots=True)
class Step:
    iteration: int
    changes: Move


@dataclass(frozen=True, slots=True)
class SearchResult:
    initial_state: State
    final_state: State
    iterations: int
    evaluations: int
    history: tuple[HistoryRecord, ...]
    steps: tuple[Step, ...]
    extra: Mapping[str, float]


class Algorithm(Protocol):
    def run(self, problem: Problem, rng: random.Random) -> SearchResult: ...

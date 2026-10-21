import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, Protocol

from src.core.models import Move, Problem, State

type Unit = Literal["iteration", "generation"]


@dataclass(frozen=True, slots=True)
class HistoryRecord:
    iteration: int
    value: float
    metrics: Mapping[str, float] = field(default_factory=dict)


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
    unit: Unit = "iteration"


class Algorithm(Protocol):
    def run(self, problem: Problem, rng: random.Random) -> SearchResult: ...

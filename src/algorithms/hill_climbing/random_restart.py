import random
from dataclasses import dataclass, field, replace

from src.algorithms.base import Algorithm, HistoryRecord, SearchResult, Step
from src.algorithms.hill_climbing.climbing import SteepestAscent
from src.core.models import Problem


def stitch_trajectories(
    results: list[SearchResult], best: SearchResult
) -> tuple[list[HistoryRecord], list[Step]]:
    history = list(results[0].history)
    steps = list(results[0].steps)
    reached = results[0].final_state
    for result in results[1:]:
        offset = history[-1].iteration + 1
        steps.append(Step(iteration=offset, changes=reached.diff(result.initial_state)))
        history.extend(
            replace(record, iteration=record.iteration + offset) for record in result.history
        )
        steps.extend(replace(step, iteration=step.iteration + offset) for step in result.steps)
        reached = result.final_state
    if reached != best.final_state:
        iteration = history[-1].iteration + 1
        steps.append(Step(iteration=iteration, changes=reached.diff(best.final_state)))
        history.append(HistoryRecord(iteration=iteration, value=best.history[-1].value))
    return history, steps


@dataclass(frozen=True, slots=True)
class RandomRestart:
    inner: Algorithm = field(default_factory=SteepestAscent)
    max_restart: int = 10

    def __post_init__(self) -> None:
        if self.max_restart < 1:
            raise ValueError("max_restart harus minimal 1")

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        results = [self.inner.run(problem, rng) for _ in range(self.max_restart)]
        best_index = max(range(len(results)), key=lambda index: results[index].history[-1].value)
        best = results[best_index]
        history, steps = stitch_trajectories(results, best)
        extra = {
            "restarts": float(self.max_restart),
            "best_restart": float(best_index),
            **{
                f"iterations_restart_{index}": float(result.iterations)
                for index, result in enumerate(results)
            },
        }
        return SearchResult(
            initial_state=results[0].initial_state,
            final_state=best.final_state,
            iterations=history[-1].iteration,
            evaluations=sum(result.evaluations for result in results),
            history=tuple(history),
            steps=tuple(steps),
            extra=extra,
            unit=results[0].unit,
        )

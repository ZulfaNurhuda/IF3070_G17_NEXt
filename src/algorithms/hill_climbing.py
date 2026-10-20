import random
from collections.abc import Iterator
from dataclasses import dataclass, replace
from typing import Iterator as TypingIterator

from src.algorithms.base import HistoryRecord, SearchResult, Step
from src.core.models import Problem, State
from src.core.neighbors import enumerate_neighbors
from src.core.initial import random_state
from src.core.evaluator import is_valid
from src.core.objectives import total_shipping_fee


@dataclass(frozen=True, slots=True)
class SteepestAscent:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        current: State = random_state(problem, rng)
        initial_state: State = current
        iterations: int = 0
        steps_list: list[Step] = []
        best_value: float = problem.value(current)

        while True:
            neighbors: TypingIterator = enumerate_neighbors(current, problem)
            valid_moves: list = list(neighbors)
            if not valid_moves:
                break

            best_val: float = float("-inf")
            best_move: tuple = ()

            for move in valid_moves:
                next_state: State = current.apply(move)
                val: float = problem.value(next_state)
                if val > best_val:
                    best_val = val
                    best_move = move

            if best_val <= best_value:
                break

            current: State = current.apply(best_move)
            best_value: float = best_val
            iterations += 1
            steps_list.append(Step(iteration=iterations, changes=best_move))

        hist_vals: list[float] = [problem.value(initial_state)]
        hist_current: State = initial_state
        for step in steps_list:
            hist_current = hist_current.apply(step.changes)
            hist_vals.append(problem.value(hist_current))

        history: tuple[HistoryRecord, ...] = tuple(
            HistoryRecord(iteration=i, value=v) for i, v in enumerate(hist_vals)
        )

        evaluations: int = 0
        for i in range(iterations + 1):
            s: State = initial_state if i == 0 else current
            for m in enumerate_neighbors(s if i < iterations else current, problem):
                evaluations += 1

        return SearchResult(
            initial_state=initial_state,
            final_state=current,
            iterations=iterations,
            evaluations=evaluations,
            history=history,
            steps=tuple(steps_list),
            extra={},
        )


@dataclass(frozen=True, slots=True)
class SidewaysMove:
    max_sideways: int = 100

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        current: State = random_state(problem, rng)
        initial_state: State = current
        iterations: int = 0
        steps_list: list[Step] = []
        sideways_used: int = 0
        sideways_count: int = 0
        best_value: float = problem.value(current)
        evaluations: int = 0

        while True:
            neighbors: TypingIterator = enumerate_neighbors(current, problem)
            valid_moves: list = list(neighbors)
            if not valid_moves:
                break

            best_val: float = float("-inf")
            best_move: tuple = ()

            for move in valid_moves:
                next_state: State = current.apply(move)
                val: float = problem.value(next_state)
                if val > best_val:
                    best_val = val
                    best_move = move
                evaluations += 1

            if best_val > best_value:
                current: State = current.apply(best_move)
                best_value: float = best_val
                sideways_count = 0
                iterations += 1
                steps_list.append(Step(iteration=iterations, changes=best_move))
            elif best_val == best_value and sideways_count < self.max_sideways:
                current: State = current.apply(best_move)
                sideways_count += 1
                sideways_used += 1
                best_value: float = best_val
                iterations += 1
                steps_list.append(Step(iteration=iterations, changes=best_move))
            else:
                break

        hist_vals: list[float] = [problem.value(initial_state)]
        hist_current: State = initial_state
        for step in steps_list:
            hist_current = hist_current.apply(step.changes)
            hist_vals.append(problem.value(hist_current))

        history: tuple[HistoryRecord, ...] = tuple(
            HistoryRecord(iteration=i, value=v) for i, v in enumerate(hist_vals)
        )

        extra: dict[str, float] = {"sideways_used": float(sideways_used)}

        return SearchResult(
            initial_state=initial_state,
            final_state=current,
            iterations=iterations,
            evaluations=evaluations,
            history=history,
            steps=tuple(steps_list),
            extra=extra,
        )


@dataclass(frozen=True, slots=True)
class Stochastic:
    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        current: State = random_state(problem, rng)
        initial_state: State = current
        iterations: int = 0
        steps_list: list[Step] = []
        best_value: float = problem.value(current)
        evaluations: int = 0

        while True:
            neighbors: TypingIterator = enumerate_neighbors(current, problem)
            valid_moves: list = list(neighbors)
            if not valid_moves:
                break

            better_moves: list = []
            for move in valid_moves:
                next_state: State = current.apply(move)
                val: float = problem.value(next_state)
                if val > best_value:
                    better_moves = [move]
                evaluations += 1

            if not better_moves:
                break

            idx: int = rng.randint(0, len(better_moves) - 1)
            best_move: tuple = better_moves[idx]
            current: State = current.apply(best_move)
            best_value: float = problem.value(current)
            iterations += 1
            steps_list.append(Step(iteration=iterations, changes=best_move))

        hist_vals: list[float] = [problem.value(initial_state)]
        hist_current: State = initial_state
        for step in steps_list:
            hist_current = hist_current.apply(step.changes)
            hist_vals.append(problem.value(hist_current))

        history: tuple[HistoryRecord, ...] = tuple(
            HistoryRecord(iteration=i, value=v) for i, v in enumerate(hist_vals)
        )

        return SearchResult(
            initial_state=initial_state,
            final_state=current,
            iterations=iterations,
            evaluations=evaluations,
            history=history,
            steps=tuple(steps_list),
            extra={},
        )


@dataclass(frozen=True, slots=True)
class RandomRestart:
    inner: object
    max_restart: int = 10

    def run(self, problem: Problem, rng: random.Random) -> SearchResult:
        best_result: object | None = None
        best_value: float = float("-inf")
        total_iterations: int = 0
        total_evaluations: int = 0
        all_history: list[HistoryRecord] = []
        all_steps: list[Step] = []
        restart_iterations: list[int] = []
        restart_evaluations: list[int] = []

        for restarts in range(1, self.max_restart + 1):
            sub_rng: random.Random = random.Random(rng.randint(0, 2**31 - 1))

            from src.algorithms.hill_climbing import SteepestAscent
            inner_sa = SteepestAscent()
            result: SearchResult = inner_sa.run(problem, sub_rng)

            total_iterations += result.iterations
            total_evaluations += result.evaluations

            final_val: float = problem.value(result.final_state)

            if final_val > best_value:
                best_value = final_val
                best_result = result

            restart_iterations.append(result.iterations)
            restart_evaluations.append(result.evaluations)

            if all_history:
                all_history.extend(result.history[1:])
            else:
                all_history.extend(result.history)

            steps_offset: int = all_steps[-1].iteration + 1 if all_steps else 0
            for step in result.steps:
                all_steps.append(
                    Step(iteration=step.iteration + steps_offset, changes=step.changes)
                )

            restart_idx: int = restarts - 1
            restart_iterations[restart_idx] = result.iterations
            restart_evaluations[restart_idx] = result.evaluations

        if best_result is None:
            raise RuntimeError("RandomRestart: no valid result from inner algorithm")

        hist_vals: list[float] = [problem.value(best_result.initial_state)]
        hist_current: State = best_result.initial_state
        for step in best_result.steps:
            hist_current = hist_current.apply(step.changes)
            hist_vals.append(problem.value(hist_current))

        history: tuple[HistoryRecord, ...] = tuple(
            HistoryRecord(iteration=i, value=v) for i, v in enumerate(hist_vals)
        )

        extra: dict[str, float] = {"restarts": float(self.max_restart)}
        for i, it in enumerate(restart_iterations):
            extra[f"iterations_restart_{i}"] = float(it)
        for i, ev in enumerate(restart_evaluations):
            extra[f"evaluations_restart_{i}"] = float(ev)

        final_steps: tuple[Step, ...] = tuple(all_steps)

        return replace(
            best_result,
            initial_state=best_result.initial_state,
            history=history,
            steps=final_steps,
            extra=extra,
        )
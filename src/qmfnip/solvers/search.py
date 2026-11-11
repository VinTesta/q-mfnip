import math
import time

import numpy as np

from ..grover import SearchSpace, classical_search, durr_hoyer, search_space
from ..instances import Instance
from .base import Solver, SolveResult, register_solver

SEARCH_KEYS = (
    "oracle_queries",
    "classical_evaluations",
    "queries_to_optimum",
    "evaluations_to_optimum",
    "found_optimum",
    "rounds",
    "query_budget",
    "within_query_budget",
)


def search_result(space: SearchSpace, outcome: dict, elapsed: float, certified: bool) -> SolveResult:
    return SolveResult(
        interdicted=space.interdictions[outcome["best_index"]].copy(),
        status="optimal" if certified else "completed",
        objective=float(outcome["best_flow"]),
        certified_optimal=certified,
        solver_time=elapsed,
        metadata={
            "search_space_size": space.size,
            "optimal_count": space.optimal_count,
            "enumeration_time_s": space.build_time,
            **{key: outcome[key] for key in SEARCH_KEYS},
        },
    )


def guarded_space(instance: Instance, max_space: int) -> SearchSpace | SolveResult:
    feasible = SearchSpace.count_feasible(instance)
    if feasible > max_space:
        return SolveResult(None, "skipped", metadata={"reason": f"|F|={feasible} > max_space={max_space}"})
    return search_space(instance)


@register_solver
class DurrHoyerSolver(Solver):
    name = "Durr-Hoyer quantum minimum finding (simulated at query level)"
    short_name = "durr_hoyer"

    def solve(self, instance: Instance, seed: int, time_limit: float) -> SolveResult:
        space = guarded_space(instance, self.params.get("max_space", 2_000_000))
        if isinstance(space, SolveResult):
            return space
        start = time.perf_counter()
        budget = self.params.get("query_budget")
        outcome = durr_hoyer(
            space,
            np.random.default_rng(seed),
            method=self.params.get("method", "reduced"),
            query_budget=math.inf if budget == "unbounded" else budget,
            stop_at_optimum=budget == "unbounded",
        )
        return search_result(space, outcome, time.perf_counter() - start, certified=False)


@register_solver
class RandomOrderSolver(Solver):
    name = "Classical search over the feasible interdictions in random order"
    short_name = "random_order"

    def solve(self, instance: Instance, seed: int, time_limit: float) -> SolveResult:
        space = guarded_space(instance, self.params.get("max_space", 2_000_000))
        if isinstance(space, SolveResult):
            return space
        start = time.perf_counter()
        outcome = classical_search(space, np.random.default_rng(seed), order="random")
        return search_result(space, outcome, time.perf_counter() - start, certified=False)

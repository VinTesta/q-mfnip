import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

from ..grover import classical_search
from ..instances import Instance
from .base import Solver, SolveResult, register_solver
from .search import guarded_space, search_result

MILP_STATUS = {0: "optimal", 1: "time_limit", 2: "infeasible", 3: "unbounded", 4: "error"}


@register_solver
class MILPSolver(Solver):
    name = "Mixed-integer linear programming (HiGHS via SciPy)"
    short_name = "milp"

    def solve(self, instance: Instance, seed: int, time_limit: float) -> SolveResult:
        n, m = instance.n, instance.m
        n_variables = n + 2 * m
        arc_index = np.arange(m)
        tail, head = instance.arcs[:, 0], instance.arcs[:, 1]
        rows = np.concatenate([arc_index] * 4)
        cols = np.concatenate([head, tail, n + arc_index, n + m + arc_index])
        values = np.concatenate([np.ones(m), -np.ones(m), -np.ones(m), -np.ones(m)])
        cut_rows = coo_matrix((values, (rows, cols)), shape=(m, n_variables))
        budget_row = coo_matrix(
            (instance.cost, (np.zeros(m, dtype=int), n + m + arc_index)), shape=(1, n_variables)
        )
        constraints = LinearConstraint(
            vstack([cut_rows, budget_row]).tocsr(), -np.inf, np.concatenate([np.zeros(m), [instance.budget]])
        )
        lower, upper = np.zeros(n_variables), np.ones(n_variables)
        lower[instance.t] = 1
        upper[instance.s] = 0
        objective = np.concatenate([np.zeros(n), instance.capacity, np.zeros(m)])
        options = {"time_limit": time_limit, "disp": False, **self.params.get("highs_options", {})}

        start = time.perf_counter()
        result = milp(
            objective, constraints=constraints, integrality=np.ones(n_variables), bounds=Bounds(lower, upper),
            options=options,
        )
        elapsed = time.perf_counter() - start

        status = MILP_STATUS.get(int(result.status), "error")
        interdicted = None if result.x is None else np.round(result.x[n + m:]).astype(bool)
        return SolveResult(
            interdicted=interdicted,
            status=status,
            objective=None if result.x is None else float(result.fun),
            certified_optimal=status == "optimal",
            solver_time=elapsed,
            metadata={
                "mip_gap": None if result.x is None else float(getattr(result, "mip_gap", np.nan)),
                "milp_variables": n_variables,
                "milp_constraints": m + 1,
            },
        )


@register_solver
class BruteForceSolver(Solver):
    name = "Exhaustive enumeration of the feasible interdiction sets"
    short_name = "brute_force"

    def solve(self, instance: Instance, seed: int, time_limit: float) -> SolveResult:
        space = guarded_space(instance, self.params.get("max_space", 2_000_000))
        if isinstance(space, SolveResult):
            return space
        start = time.perf_counter()
        outcome = classical_search(space, np.random.default_rng(seed), order="sequential")
        return search_result(space, outcome, time.perf_counter() - start, certified=True)

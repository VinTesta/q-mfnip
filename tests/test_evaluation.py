import numpy as np
import pandas as pd
import pytest

from qmfnip.evaluation import evaluate_run, fit_scaling_exponent, frontier, summarize
from qmfnip.instances import generate_layered
from qmfnip.solvers import MILPSolver, SolveResult

INSTANCE = generate_layered(3, seed=0, budget_fraction=0.5, layers=2, out_degree=2)


def make_runs(rows: list[dict]) -> pd.DataFrame:
    defaults = {
        "family": "layered",
        "budget_fraction": 0.5,
        "n_arcs": 10,
        "delivered": True,
        "feasible": True,
        "within_time": True,
        "certified_optimal": False,
        "reference_certified": True,
        "non_degenerate": True,
        "wall_time_s": 1.0,
    }
    return pd.DataFrame([{**defaults, **row} for row in rows])


def test_certified_run_is_its_own_reference():
    result = MILPSolver().solve(INSTANCE, seed=0, time_limit=60)
    evaluation = evaluate_run(INSTANCE, result, wall_time=0.1, time_limit=1.0)
    assert evaluation["reference_certified"]
    assert evaluation["gap"] == 0.0
    assert evaluation["feasible"]
    assert evaluation["within_time"]


def test_infeasible_solution_is_reported_raw_without_gap():
    result = SolveResult(np.ones(INSTANCE.m, dtype=bool), "sampled")
    reference = {"certified": True, "optimal_flow": 1}
    evaluation = evaluate_run(INSTANCE, result, wall_time=0.1, time_limit=1.0, reference=reference)
    assert not evaluation["feasible"]
    assert evaluation["gap"] is None
    assert evaluation["flow_after_interdiction"] == 0


def test_uncertified_reference_leaves_gap_undefined():
    result = SolveResult(np.zeros(INSTANCE.m, dtype=bool), "time_limit")
    evaluation = evaluate_run(INSTANCE, result, wall_time=0.1, time_limit=1.0, reference={"certified": False})
    assert evaluation["feasible"]
    assert not evaluation["reference_certified"]
    assert evaluation["gap"] is None


def test_overtime_run_counts_as_failure():
    runs = make_runs([{"solver": "a", "n_nodes": 10, "gap": 0.0, "within_time": False}])
    assert summarize(runs, z=0.05)["success_rate"].iloc[0] == 0.0


def test_run_without_reference_is_excluded_from_success_rate():
    runs = make_runs(
        [
            {"solver": "a", "n_nodes": 10, "gap": 0.0},
            {"solver": "a", "n_nodes": 10, "gap": None, "reference_certified": False},
        ]
    )
    summary = summarize(runs, z=0.05)
    assert summary["judged_runs"].iloc[0] == 1
    assert summary["success_rate"].iloc[0] == 1.0


def test_frontier_stops_at_first_failure():
    runs = make_runs(
        [
            {"solver": "a", "n_nodes": 10, "gap": 0.0},
            {"solver": "a", "n_nodes": 20, "gap": 0.01},
            {"solver": "a", "n_nodes": 30, "gap": 0.5},
            {"solver": "b", "n_nodes": 10, "gap": 0.0},
            {"solver": "b", "n_nodes": 20, "gap": 0.0},
            {"solver": "b", "n_nodes": 30, "gap": 0.0},
            {"solver": "c", "n_nodes": 10, "gap": 0.0},
            {"solver": "c", "n_nodes": 20, "gap": 0.9},
            {"solver": "c", "n_nodes": 30, "gap": 0.0},
        ]
    )
    summary = summarize(runs, z=0.05)
    contiguous = frontier(summary, p=1.0).set_index("solver")
    assert contiguous.loc["a", "n_star_nodes"] == 20
    assert contiguous.loc["a", "first_failure_nodes"] == 30
    assert not contiguous.loc["a", "reached_largest"]
    assert contiguous.loc["b", "n_star_nodes"] == 30
    assert contiguous.loc["b", "reached_largest"]
    assert contiguous.loc["c", "n_star_nodes"] == 10
    assert frontier(summary, p=1.0, contiguous=False).set_index("solver").loc["c", "n_star_nodes"] == 30


def test_frontier_is_empty_when_smallest_size_fails():
    runs = make_runs([{"solver": "a", "n_nodes": 10, "gap": 0.5}, {"solver": "a", "n_nodes": 20, "gap": 0.0}])
    result = frontier(summarize(runs, z=0.05), p=1.0).iloc[0]
    assert pd.isna(result["n_star_nodes"])
    assert result["first_failure_nodes"] == 10


@pytest.mark.parametrize("gap, expected", [(0.05, 1.0), (0.0501, 0.0)])
def test_success_threshold_is_inclusive(gap, expected):
    runs = make_runs([{"solver": "a", "n_nodes": 10, "gap": gap}])
    assert summarize(runs, z=0.05)["success_rate"].iloc[0] == expected


def test_fit_scaling_exponent_recovers_known_slope():
    rng = np.random.default_rng(0)
    sizes = np.repeat(10 ** np.linspace(1, 6, 10), 3)
    frame = pd.DataFrame(
        {
            "instance_id": range(30),
            "solver": "quantum",
            "size": sizes,
            "cost": 2.0 * sizes**0.5 * np.exp(rng.normal(0, 0.05, 30)),
        }
    )
    fit = fit_scaling_exponent(frame, "size", "cost", n_boot=300).iloc[0]
    assert fit["ci_low"] <= 0.5 <= fit["ci_high"]
    assert abs(fit["beta"] - 0.5) < 0.02

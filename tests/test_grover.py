import itertools
import math

import numpy as np
import pytest

from qmfnip.grover import GroverSampler, SearchSpace, classical_search, durr_hoyer, search_space
from qmfnip.instances import Scenario, generate_layered, generate_random, max_flow
from qmfnip.playground import ExperimentConfig, run_experiment
from qmfnip.solvers import BruteForceSolver, DurrHoyerSolver, MILPSolver, RandomOrderSolver

UNIT = [generate_layered(width, seed, budget=budget, cost_range=(1, 1)) for width, budget in ((2, 1), (3, 2)) for seed in (0, 1)]
GENERAL = [generate_random(7, seed, budget_fraction=0.5, arc_factor=2.0) for seed in range(3)]
TINY = UNIT + GENERAL + [generate_layered(3, seed, budget_fraction=0.5, layers=2, out_degree=2) for seed in range(4)]


@pytest.mark.parametrize("instance", UNIT + GENERAL, ids=lambda instance: instance.instance_id)
def test_feasible_enumeration_matches_product_filter(instance):
    space = SearchSpace.from_instance(instance)
    expected = {
        mask
        for mask in itertools.product((False, True), repeat=instance.m)
        if instance.cost[np.array(mask)].sum() <= instance.budget
    } if instance.m <= 16 else None
    found = {tuple(row) for row in space.interdictions.tolist()}
    assert len(found) == space.size
    if expected is not None:
        assert found == expected
    assert SearchSpace.count_feasible(instance) == space.size
    if (instance.cost == 1).all():
        assert space.size == sum(math.comb(instance.m, i) for i in range(instance.budget + 1))
    sample = np.random.default_rng(0).choice(space.size, size=min(40, space.size), replace=False)
    assert all(space.flows[i] == max_flow(instance, space.interdictions[i]) for i in sample)


@pytest.mark.parametrize("instance", TINY, ids=lambda instance: instance.instance_id)
def test_search_space_optimum_matches_milp(instance):
    milp = MILPSolver().solve(instance, seed=0, time_limit=60)
    assert milp.certified_optimal
    assert search_space(instance).optimum == pytest.approx(milp.objective)


@pytest.mark.parametrize("instance", UNIT + GENERAL[:1], ids=lambda instance: instance.instance_id)
def test_reduced_sampler_matches_statevector(instance):
    space = search_space(instance)
    assert space.size <= 2**10
    reduced = GroverSampler(space, np.random.default_rng(0), "reduced")
    full = GroverSampler(space, np.random.default_rng(0), "statevector")
    for threshold in np.unique(space.flows).tolist() + [space.flows.max() + 1]:
        for iterations in range(2 * math.isqrt(space.size) + 2):
            assert np.abs(reduced.probabilities(threshold, iterations) - full.probabilities(threshold, iterations)).max() <= 1e-10


@pytest.mark.parametrize("instance", UNIT + GENERAL, ids=lambda instance: instance.instance_id)
def test_durr_hoyer_finds_optimum_within_theoretical_budget(instance):
    space = search_space(instance)
    rng = np.random.default_rng(1)
    outcomes = [durr_hoyer(space, rng) for _ in range(100)]
    assert np.mean([outcome["found_optimum"] for outcome in outcomes]) >= 0.5
    assert all(outcome["oracle_queries"] <= space.query_budget for outcome in outcomes)
    assert all(outcome["within_query_budget"] == outcome["found_optimum"] for outcome in outcomes)


def test_durr_hoyer_statevector_and_reduced_agree_in_distribution():
    space = search_space(UNIT[2])
    reduced = [durr_hoyer(space, np.random.default_rng(seed), "reduced", math.inf, True)["queries_to_optimum"] for seed in range(300)]
    full = [durr_hoyer(space, np.random.default_rng(seed), "statevector", math.inf, True)["queries_to_optimum"] for seed in range(300)]
    spread = math.sqrt(np.var(reduced) / 300 + np.var(full) / 300)
    assert abs(np.mean(reduced) - np.mean(full)) <= 4 * spread


def test_random_order_matches_theoretical_mean():
    space = search_space(UNIT[3])
    rng = np.random.default_rng(2)
    samples = np.array([classical_search(space, rng, "random")["evaluations_to_optimum"] for _ in range(4000)])
    expected = (space.size + 1) / (space.optimal_count + 1)
    assert abs(samples.mean() - expected) <= 3 * samples.std(ddof=1) / math.sqrt(len(samples))


def test_sequential_enumeration_certifies_with_all_evaluations():
    space = search_space(UNIT[3])
    outcome = classical_search(space, np.random.default_rng(0), "sequential")
    assert outcome["classical_evaluations"] == space.size
    assert outcome["best_flow"] == space.optimum


def test_search_solvers_run_in_playground(tmp_path):
    scenario = Scenario("layered", sizes=(2, 3), budgets=(1, 2), seeds=(0,), params={"cost_range": (1, 1)}, skip_degenerate=True)
    solvers = [
        DurrHoyerSolver(query_budget="unbounded"),
        DurrHoyerSolver(label="durr_hoyer_budget"),
        RandomOrderSolver(),
        BruteForceSolver(label="enumeration"),
    ]
    config = ExperimentConfig(scenario=scenario, solvers=solvers, repetitions=3, time_limit=60, output_root=tmp_path)
    runs = run_experiment(config, verbose=False).load_runs()
    assert len(runs) == 3 * 4 * 3
    expected = {"search_space_size", "optimal_count", "oracle_queries", "classical_evaluations", "queries_to_optimum",
                "evaluations_to_optimum", "found_optimum", "within_query_budget", "enumeration_time_s"}
    assert expected <= set(runs.columns)
    found = runs[runs["found_optimum"].astype(bool)]
    assert (found["gap"] == 0.0).all()
    assert (runs.loc[runs["solver"] != "durr_hoyer_budget", "found_optimum"].astype(bool)).all()
    assert (runs.loc[runs["solver"] == "enumeration", "classical_evaluations"] == runs.loc[runs["solver"] == "enumeration", "search_space_size"]).all()

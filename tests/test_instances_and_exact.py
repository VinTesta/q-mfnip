import pytest

from qmfnip.instances import Instance, Scenario, full_cut_cost, generate_layered, generate_random, max_flow
from qmfnip.solvers import BruteForceSolver, MILPSolver

SMALL_INSTANCES = [generate_random(6, seed, budget_fraction=0.5, arc_factor=2.0) for seed in range(6)] + [
    generate_layered(3, seed, budget_fraction=0.5, layers=2, out_degree=2) for seed in range(6)
]


@pytest.mark.parametrize("instance", SMALL_INSTANCES, ids=lambda instance: instance.instance_id)
def test_milp_matches_brute_force(instance):
    assert instance.m <= 16
    milp_result = MILPSolver().solve(instance, seed=0, time_limit=60)
    brute_result = BruteForceSolver().solve(instance, seed=0, time_limit=60)
    assert milp_result.certified_optimal
    assert brute_result.certified_optimal
    assert milp_result.objective == pytest.approx(brute_result.objective)
    assert max_flow(instance, milp_result.interdicted) == pytest.approx(milp_result.objective)
    assert instance.cost[milp_result.interdicted].sum() <= instance.budget


@pytest.mark.parametrize("size", [3, 4, 5])
def test_random_generator_terminates_on_dense_small_graphs(size):
    instance = generate_random(size, seed=0, arc_factor=10.0)
    assert instance.m == (size - 1) ** 2 - (size - 2)


def test_budget_scales_with_full_cut_not_with_network_size():
    assert generate_random(2560, seed=0).budget < 10 * generate_random(40, seed=0).budget


def test_scenario_is_deterministic():
    scenario = Scenario("layered", sizes=(3, 4), budget_fractions=(0.25, 0.5), seeds=(0, 1))
    first = [instance.content_hash for instance in scenario.instances()]
    second = [instance.content_hash for instance in scenario.instances()]
    identifiers = [instance.instance_id for instance in scenario.instances()]
    assert first == second
    assert len(first) == 8
    assert len(set(identifiers)) == 8


def test_instance_roundtrip_preserves_identity():
    instance = generate_layered(4, seed=3, budget_fraction=0.75)
    restored = Instance.from_dict(instance.to_dict())
    assert restored.content_hash == instance.content_hash
    assert restored.instance_id == instance.instance_id
    assert max_flow(restored) == max_flow(instance)


def test_brute_force_skips_large_search_spaces():
    result = BruteForceSolver(max_space=5).solve(generate_random(10, seed=0), seed=0, time_limit=1)
    assert result.status == "skipped"
    assert result.interdicted is None


@pytest.mark.parametrize(
    ("instance", "expected"),
    [
        (generate_layered(3, 0, budget_fraction=0.25), "ba3007641e3d1315"),
        (generate_layered(4, 0, budget_fraction=0.25), "94fe3361cb10be79"),
        (generate_layered(6, 2, budget_fraction=0.75), "4753f19b3577770f"),
        (generate_random(10, 0, budget_fraction=0.25), "0680aee33e296a61"),
        (generate_random(40, 1, budget_fraction=0.25), "7a3d5a650b7e73b4"),
    ],
    ids=lambda value: getattr(value, "instance_id", value),
)
def test_notebook_01_instances_keep_their_hashes(instance, expected):
    assert instance.content_hash == expected


def test_explicit_budget_overrides_fraction_without_changing_the_graph():
    by_fraction = generate_layered(4, 1, budget_fraction=0.5, cost_range=(1, 1))
    by_budget = generate_layered(4, 1, budget=3, cost_range=(1, 1))
    assert by_budget.budget == 3
    assert by_budget.budget_fraction is None
    assert by_budget.instance_id.endswith("-B3-s1")
    assert (by_budget.arcs == by_fraction.arcs).all()
    assert (by_budget.capacity == by_fraction.capacity).all()


def test_skip_degenerate_keeps_only_budgets_below_the_full_cut():
    scenario = Scenario(
        "layered", sizes=(2, 3, 4), budgets=(1, 2, 3, 4), seeds=(0, 1), params={"cost_range": (1, 1)},
        skip_degenerate=True,
    )
    instances = list(scenario.instances())
    assert len(instances) == 2 * (1 + 2 + 3)
    assert all(instance.budget < full_cut_cost(instance) for instance in instances)

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import pairwise, product

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow


@dataclass(frozen=True, eq=False)
class Instance:
    n: int
    arcs: np.ndarray
    capacity: np.ndarray
    cost: np.ndarray
    budget: int
    family: str = "custom"
    seed: int | None = None
    budget_fraction: float | None = None
    generator_params: dict = field(default_factory=dict)
    s: int = 0

    @property
    def t(self) -> int:
        return self.n - 1

    @property
    def m(self) -> int:
        return len(self.arcs)

    @property
    def instance_id(self) -> str:
        budget_label = f"b{self.budget_fraction:.2f}" if self.budget_fraction is not None else f"B{self.budget}"
        seed_label = f"s{self.seed}" if self.seed is not None else self.content_hash[:8]
        return f"{self.family}-n{self.n}-m{self.m}-{budget_label}-{seed_label}"

    @property
    def content_hash(self) -> str:
        digest = hashlib.sha256()
        digest.update(np.array([self.n, self.s, self.t, self.budget], dtype=np.int64).tobytes())
        for array in (self.arcs, self.capacity, self.cost):
            digest.update(np.ascontiguousarray(array, dtype=np.int64).tobytes())
        return digest.hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "content_hash": self.content_hash,
            "family": self.family,
            "seed": self.seed,
            "budget_fraction": self.budget_fraction,
            "generator_params": self.generator_params,
            "n": self.n,
            "s": self.s,
            "t": self.t,
            "budget": self.budget,
            "arcs": self.arcs.tolist(),
            "capacity": self.capacity.tolist(),
            "cost": self.cost.tolist(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Instance":
        return cls(
            n=data["n"],
            arcs=np.array(data["arcs"], dtype=np.int64).reshape(-1, 2),
            capacity=np.array(data["capacity"], dtype=np.int64),
            cost=np.array(data["cost"], dtype=np.int64),
            budget=data["budget"],
            family=data.get("family", "custom"),
            seed=data.get("seed"),
            budget_fraction=data.get("budget_fraction"),
            generator_params=data.get("generator_params", {}),
            s=data.get("s", 0),
        )


def max_flow(instance: Instance, interdicted: np.ndarray | None = None, weights: np.ndarray | None = None) -> int:
    values = (instance.capacity if weights is None else weights).copy()
    if interdicted is not None:
        values[np.asarray(interdicted, dtype=bool)] = 0
    graph = csr_matrix(
        (values, (instance.arcs[:, 0], instance.arcs[:, 1])), shape=(instance.n, instance.n), dtype=np.int32
    )
    return int(maximum_flow(graph, instance.s, instance.t).flow_value)


def full_cut_cost(instance: Instance) -> int:
    return max_flow(instance, weights=instance.cost)


def _build_instance(
    n: int,
    arcs: set,
    rng: np.random.Generator,
    family: str,
    seed: int,
    budget_fraction: float,
    capacity_range: tuple[int, int],
    cost_range: tuple[int, int],
    generator_params: dict,
    budget: int | None = None,
) -> Instance:
    arc_array = np.array(sorted(arcs), dtype=np.int64)
    capacity = rng.integers(capacity_range[0], capacity_range[1] + 1, size=len(arc_array))
    cost = rng.integers(cost_range[0], cost_range[1] + 1, size=len(arc_array))
    if budget is None:
        draft = Instance(n, arc_array, capacity, cost, 0)
        budget = max(1, int(np.ceil(budget_fraction * full_cut_cost(draft))))
    else:
        budget_fraction = None
    return Instance(
        n=n,
        arcs=arc_array,
        capacity=capacity,
        cost=cost,
        budget=int(budget),
        family=family,
        seed=seed,
        budget_fraction=budget_fraction,
        generator_params=generator_params,
    )


def generate_random(
    size: int,
    seed: int,
    budget_fraction: float = 0.5,
    arc_factor: float = 3.0,
    capacity_range: tuple[int, int] = (1, 10),
    cost_range: tuple[int, int] = (1, 5),
    budget: int | None = None,
) -> Instance:
    rng = np.random.default_rng(seed)
    source, sink = 0, size - 1
    path = [source, *rng.permutation(np.arange(1, size - 1)).tolist(), sink]
    arcs = set(pairwise(path))
    possible_arcs = (size - 1) ** 2 - (size - 2)
    target = min(max(len(arcs), int(arc_factor * size)), possible_arcs)
    while len(arcs) < target:
        i, j = rng.integers(0, size, size=2)
        if i != j and j != source and i != sink:
            arcs.add((int(i), int(j)))
    params = {"arc_factor": arc_factor, "capacity_range": list(capacity_range), "cost_range": list(cost_range)}
    return _build_instance(size, arcs, rng, "random", seed, budget_fraction, capacity_range, cost_range, params, budget)


def generate_layered(
    size: int,
    seed: int,
    budget_fraction: float = 0.5,
    layers: int | None = None,
    out_degree: int = 3,
    capacity_range: tuple[int, int] = (1, 10),
    cost_range: tuple[int, int] = (1, 5),
    budget: int | None = None,
) -> Instance:
    rng = np.random.default_rng(seed)
    width = size
    depth = layers if layers is not None else size
    n = depth * width + 2
    source, sink = 0, n - 1
    arcs = {(source, 1 + k) for k in range(width)}
    arcs |= {(1 + (depth - 1) * width + k, sink) for k in range(width)}
    for layer in range(depth - 1):
        for k in range(width):
            for target in rng.choice(width, size=min(out_degree, width), replace=False):
                arcs.add((1 + layer * width + k, 1 + (layer + 1) * width + int(target)))
    params = {
        "width": width,
        "layers": depth,
        "out_degree": out_degree,
        "capacity_range": list(capacity_range),
        "cost_range": list(cost_range),
    }
    return _build_instance(n, arcs, rng, "layered", seed, budget_fraction, capacity_range, cost_range, params, budget)


GENERATORS = {"random": generate_random, "layered": generate_layered}


@dataclass(frozen=True)
class Scenario:
    family: str
    sizes: tuple[int, ...]
    budget_fractions: tuple[float, ...] = (0.5,)
    seeds: tuple[int, ...] = (0, 1, 2)
    params: dict = field(default_factory=dict)
    budgets: tuple[int, ...] = ()
    skip_degenerate: bool = False

    def instances(self) -> Iterator[Instance]:
        generator = GENERATORS[self.family]
        options = [{"budget": budget} for budget in self.budgets] or [
            {"budget_fraction": fraction} for fraction in self.budget_fractions
        ]
        for size, option, seed in product(self.sizes, options, self.seeds):
            instance = generator(size, seed, **option, **self.params)
            if self.skip_degenerate and instance.budget >= full_cut_cost(instance):
                continue
            yield instance

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "sizes": list(self.sizes),
            "budget_fractions": list(self.budget_fractions),
            "seeds": list(self.seeds),
            "params": self.params,
            "budgets": list(self.budgets),
            "skip_degenerate": self.skip_degenerate,
        }

import math
import time
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

from .instances import Instance

BBHT_LAMBDA = 6 / 5
CACHE_SIZE = 2


def durr_hoyer_budget(size: int) -> float:
    return 22.5 * math.sqrt(size) + 1.4 * math.log2(size) ** 2 if size > 1 else 1.0


def enumerate_feasible(cost: np.ndarray, budget: int) -> np.ndarray:
    m = len(cost)
    min_cost = int(cost.min()) if m else 0
    levels = [np.zeros((1, 0), dtype=np.int64)]
    spent = np.zeros(1, dtype=np.int64)
    while True:
        current = levels[-1]
        extendable = budget - spent >= min_cost
        if not extendable.any() or current.shape[1] == m:
            break
        last = current[:, -1] if current.shape[1] else np.full(len(current), -1)
        rows, columns = np.nonzero(
            extendable[:, None]
            & (np.arange(m)[None, :] > last[:, None])
            & (spent[:, None] + cost[None, :] <= budget)
        )
        if len(rows) == 0:
            break
        levels.append(np.hstack([current[rows], columns[:, None]]))
        spent = spent[rows] + cost[columns]
    size = sum(len(level) for level in levels)
    masks = np.zeros((size, m), dtype=bool)
    offset = 0
    for level in levels:
        if level.shape[1]:
            masks[np.repeat(np.arange(offset, offset + len(level)), level.shape[1]), level.ravel()] = True
        offset += len(level)
    return masks


class FlowEvaluator:
    def __init__(self, instance: Instance):
        order = np.lexsort((instance.arcs[:, 1], instance.arcs[:, 0]))
        self.instance = instance
        self.indptr = np.searchsorted(instance.arcs[order, 0], np.arange(instance.n + 1)).astype(np.int32)
        self.indices = instance.arcs[order, 1].astype(np.int32)
        self.base = instance.capacity[order].astype(np.int32)
        self.position = np.empty(instance.m, dtype=np.int64)
        self.position[order] = np.arange(instance.m)

    def __call__(self, interdicted: np.ndarray) -> int:
        data = self.base.copy()
        data[self.position[np.asarray(interdicted, dtype=bool)]] = 0
        graph = csr_matrix((data, self.indices, self.indptr), shape=(self.instance.n, self.instance.n))
        return int(maximum_flow(graph, self.instance.s, self.instance.t).flow_value)


@dataclass
class SearchSpace:
    instance: Instance
    interdictions: np.ndarray
    flows: np.ndarray
    build_time: float = 0.0
    order: np.ndarray = field(init=False, repr=False)
    sorted_flows: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        self.order = np.argsort(self.flows, kind="stable")
        self.sorted_flows = self.flows[self.order]

    @classmethod
    def from_instance(cls, instance: Instance) -> "SearchSpace":
        start = time.perf_counter()
        interdictions = enumerate_feasible(instance.cost.astype(np.int64), int(instance.budget))
        evaluate = FlowEvaluator(instance)
        flows = np.fromiter((evaluate(mask) for mask in interdictions), dtype=np.int64, count=len(interdictions))
        return cls(instance, interdictions, flows, time.perf_counter() - start)

    @staticmethod
    def count_feasible(instance: Instance) -> int:
        budget = int(instance.budget)
        counts = [1] + [0] * budget
        for cost in instance.cost.astype(int):
            for spent in range(budget, cost - 1, -1):
                counts[spent] += counts[spent - cost]
        return sum(counts)

    @property
    def size(self) -> int:
        return len(self.flows)

    @property
    def optimum(self) -> int:
        return int(self.sorted_flows[0])

    @property
    def optimal_count(self) -> int:
        return self.marked_count(self.optimum + 1)

    @property
    def optimal_indices(self) -> np.ndarray:
        return self.order[: self.optimal_count]

    @property
    def query_budget(self) -> float:
        return durr_hoyer_budget(self.size)

    def marked_count(self, threshold: float) -> int:
        return int(np.searchsorted(self.sorted_flows, threshold, side="left"))


_CACHE: OrderedDict[str, SearchSpace] = OrderedDict()


def search_space(instance: Instance) -> SearchSpace:
    key = instance.content_hash
    if key in _CACHE:
        _CACHE.move_to_end(key)
        return _CACHE[key]
    space = SearchSpace.from_instance(instance)
    _CACHE[key] = space
    while len(_CACHE) > CACHE_SIZE:
        _CACHE.popitem(last=False)
    return space


class GroverSampler:
    def __init__(self, space: SearchSpace, rng: np.random.Generator, method: str = "reduced"):
        if method not in ("reduced", "statevector"):
            raise ValueError(f"Unknown method {method!r}")
        self.space = space
        self.rng = rng
        self.method = method

    def marked_probability(self, threshold: float, iterations: int) -> float:
        marked, size = self.space.marked_count(threshold), self.space.size
        if marked == 0:
            return 0.0
        theta = math.asin(math.sqrt(marked / size))
        return math.sin((2 * iterations + 1) * theta) ** 2

    def probabilities(self, threshold: float, iterations: int) -> np.ndarray:
        size = self.space.size
        marked = self.space.flows < threshold
        if self.method == "statevector":
            amplitudes = np.full(size, 1 / math.sqrt(size))
            for _ in range(iterations):
                amplitudes[marked] *= -1
                amplitudes = 2 * amplitudes.mean() - amplitudes
            return amplitudes**2
        count = int(marked.sum())
        probability = self.marked_probability(threshold, iterations)
        result = np.empty(size)
        result[marked] = probability / count if count else 0.0
        result[~marked] = (1 - probability) / (size - count) if count < size else 0.0
        return result

    def sample(self, threshold: float, iterations: int) -> int:
        if self.method == "statevector":
            return int(self.rng.choice(self.space.size, p=self.probabilities(threshold, iterations)))
        marked, size = self.space.marked_count(threshold), self.space.size
        if self.rng.random() < self.marked_probability(threshold, iterations):
            return int(self.space.order[self.rng.integers(marked)])
        return int(self.space.order[marked + self.rng.integers(size - marked)])


def durr_hoyer(
    space: SearchSpace,
    rng: np.random.Generator,
    method: str = "reduced",
    query_budget: float | None = None,
    stop_at_optimum: bool = False,
) -> dict:
    budget = space.query_budget if query_budget is None else query_budget
    if math.isinf(budget) and not stop_at_optimum:
        raise ValueError("An unbounded query budget requires stop_at_optimum=True")
    sampler = GroverSampler(space, rng, method)
    flows, optimum, size = space.flows, space.optimum, space.size
    best_index = int(rng.integers(size))
    queries, evaluations, rounds = 0, 1, 0
    queries_to_optimum = 0 if flows[best_index] == optimum else None
    evaluations_to_optimum = 1 if queries_to_optimum is not None else None
    exhausted = False
    while not exhausted and not (stop_at_optimum and queries_to_optimum is not None):
        rounds += 1
        threshold, scale = flows[best_index], 1.0
        while True:
            iterations = int(rng.integers(math.ceil(scale)))
            if queries + iterations > budget:
                exhausted = True
                break
            queries += iterations
            candidate = sampler.sample(threshold, iterations)
            evaluations += 1
            if flows[candidate] < threshold:
                best_index = candidate
                if flows[candidate] == optimum:
                    queries_to_optimum, evaluations_to_optimum = queries, evaluations
                break
            scale = min(BBHT_LAMBDA * scale, math.sqrt(size))
    return {
        "best_index": best_index,
        "best_flow": int(flows[best_index]),
        "oracle_queries": queries,
        "classical_evaluations": evaluations,
        "queries_to_optimum": queries_to_optimum,
        "evaluations_to_optimum": evaluations_to_optimum,
        "found_optimum": bool(flows[best_index] == optimum),
        "rounds": rounds,
        "query_budget": space.query_budget,
        "within_query_budget": queries_to_optimum is not None and queries_to_optimum <= space.query_budget,
    }


def classical_search(space: SearchSpace, rng: np.random.Generator, order: str = "random") -> dict:
    optimal = space.optimal_indices
    if order == "random":
        positions = rng.choice(space.size, size=len(optimal), replace=False)
        first = int(np.argmin(positions))
        best_index, evaluations_to_optimum = int(optimal[first]), int(positions[first]) + 1
        evaluations = evaluations_to_optimum
    elif order == "sequential":
        best_index = int(optimal.min())
        evaluations_to_optimum, evaluations = best_index + 1, space.size
    else:
        raise ValueError(f"Unknown order {order!r}")
    return {
        "best_index": best_index,
        "best_flow": int(space.flows[best_index]),
        "oracle_queries": 0,
        "classical_evaluations": evaluations,
        "queries_to_optimum": 0,
        "evaluations_to_optimum": evaluations_to_optimum,
        "found_optimum": True,
        "rounds": 1,
        "query_budget": None,
        "within_query_budget": None,
    }

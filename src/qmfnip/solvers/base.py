from dataclasses import dataclass, field

import numpy as np

from ..instances import Instance


@dataclass
class SolveResult:
    interdicted: np.ndarray | None
    status: str
    objective: float | None = None
    certified_optimal: bool = False
    solver_time: float | None = None
    qpu_time: float | None = None
    queue_time: float | None = None
    compile_time: float | None = None
    metadata: dict = field(default_factory=dict)


class Solver:
    name = "solver"
    short_name = "solver"

    def __init__(self, **params):
        self.params = params

    @property
    def label(self) -> str:
        return self.params.get("label", self.short_name)

    def solve(self, instance: Instance, seed: int, time_limit: float) -> SolveResult:
        raise NotImplementedError

    def requires_hardware(self) -> bool:
        return False

    def describe(self) -> dict:
        return {
            "name": self.name,
            "short_name": self.short_name,
            "label": self.label,
            "class": f"{type(self).__module__}.{type(self).__qualname__}",
            "params": self.params,
            "requires_hardware": self.requires_hardware(),
        }


SOLVERS: dict[str, type[Solver]] = {}


def register_solver(solver_class: type[Solver]) -> type[Solver]:
    SOLVERS[solver_class.short_name] = solver_class
    return solver_class

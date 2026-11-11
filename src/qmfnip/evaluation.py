import math

import numpy as np
import pandas as pd

from .instances import Instance, max_flow
from .solvers import SolveResult

SUMMARY_GROUP = ("solver", "family", "budget_fraction", "n_nodes")
FRONTIER_GROUP = ("solver", "family", "budget_fraction")
BOOLEAN_COLUMNS = ("delivered", "feasible", "within_time", "certified_optimal", "reference_certified", "non_degenerate")
NUMERIC_COLUMNS = (
    "gap",
    "n_arcs",
    "wall_time_s",
    "logical_qubits",
    "physical_qubits",
    "two_qubit_gates",
    "circuit_depth",
)


def evaluate_run(
    instance: Instance,
    result: SolveResult,
    wall_time: float,
    time_limit: float,
    reference: dict | None = None,
) -> dict:
    flow_without_interdiction = max_flow(instance)
    delivered = result.interdicted is not None
    budget_used = int(instance.cost[result.interdicted].sum()) if delivered else None
    feasible = delivered and budget_used <= instance.budget
    flow_after_interdiction = max_flow(instance, result.interdicted) if delivered else None

    optimal_flow, reference_certified = None, False
    if reference is not None and reference.get("certified"):
        optimal_flow, reference_certified = reference["optimal_flow"], True
    elif result.certified_optimal and feasible:
        optimal_flow, reference_certified = flow_after_interdiction, True

    gap = None
    if feasible and reference_certified:
        if flow_after_interdiction == optimal_flow:
            gap = 0.0
        elif optimal_flow > 0:
            gap = (flow_after_interdiction - optimal_flow) / optimal_flow
        else:
            gap = math.inf

    return {
        "delivered": delivered,
        "feasible": feasible,
        "within_time": wall_time <= time_limit,
        "budget_used": budget_used,
        "flow_without_interdiction": flow_without_interdiction,
        "flow_after_interdiction": flow_after_interdiction,
        "optimal_flow": optimal_flow,
        "reference_certified": reference_certified,
        "gap": gap,
        "non_degenerate": (0 < optimal_flow < flow_without_interdiction) if reference_certified else None,
    }


def _as_float(series: pd.Series) -> pd.Series:
    mapping = {True: 1.0, False: 0.0, "True": 1.0, "False": 0.0}
    return pd.to_numeric(series.map(lambda value: mapping.get(value, value)), errors="coerce")


def summarize(runs: pd.DataFrame, z: float, by: tuple[str, ...] = SUMMARY_GROUP) -> pd.DataFrame:
    data = runs.copy()
    for column in BOOLEAN_COLUMNS:
        data[column] = _as_float(data[column]) if column in data else np.nan
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce") if column in data else np.nan
    usable = (data["delivered"] == 1) & (data["feasible"] == 1) & (data["within_time"] == 1)
    judged = np.where(data["gap"].isna(), np.nan, (data["gap"] <= z).astype(float))
    data["success"] = np.where(usable, judged, 0.0)
    data["certified_in_time"] = ((data["certified_optimal"] == 1) & (data["within_time"] == 1)).astype(float)

    summary = (
        data.groupby(list(by), dropna=False)
        .agg(
            runs=("success", "size"),
            n_arcs=("n_arcs", "median"),
            delivered_rate=("delivered", "mean"),
            feasible_rate=("feasible", "mean"),
            within_time_rate=("within_time", "mean"),
            certified_rate=("certified_in_time", "mean"),
            reference_certified_rate=("reference_certified", "mean"),
            non_degenerate_rate=("non_degenerate", "mean"),
            judged_runs=("success", "count"),
            success_rate=("success", "mean"),
            median_gap=("gap", "median"),
            gap_q1=("gap", lambda values: values.quantile(0.25)),
            gap_q3=("gap", lambda values: values.quantile(0.75)),
            median_wall_time_s=("wall_time_s", "median"),
            max_wall_time_s=("wall_time_s", "max"),
            median_logical_qubits=("logical_qubits", "median"),
            median_physical_qubits=("physical_qubits", "median"),
            median_two_qubit_gates=("two_qubit_gates", "median"),
            median_circuit_depth=("circuit_depth", "median"),
        )
        .reset_index()
    )
    summary["z"] = z
    return summary


def frontier(
    summary: pd.DataFrame,
    p: float,
    rate: str = "success_rate",
    by: tuple[str, ...] = FRONTIER_GROUP,
    contiguous: bool = True,
) -> pd.DataFrame:
    rows = []
    for keys, group in summary.groupby(list(by), dropna=False):
        group = group.sort_values("n_nodes").reset_index(drop=True)
        passed = (group[rate].fillna(-1.0) >= p).to_numpy()
        if contiguous:
            failures = np.flatnonzero(~passed)
            last = failures[0] - 1 if len(failures) else len(group) - 1
        else:
            hits = np.flatnonzero(passed)
            last = hits[-1] if len(hits) else -1
        row = dict(zip(by, keys if isinstance(keys, tuple) else (keys,)))
        row.update(
            {
                "n_star_nodes": group.loc[last, "n_nodes"] if last >= 0 else None,
                "n_star_arcs": group.loc[last, "n_arcs"] if last >= 0 else None,
                "first_failure_nodes": group.loc[last + 1, "n_nodes"] if last + 1 < len(group) else None,
                "smallest_tested_nodes": group["n_nodes"].iloc[0],
                "largest_tested_nodes": group["n_nodes"].iloc[-1],
                "reached_largest": bool(last == len(group) - 1),
                "rate": rate,
                "p": p,
                "contiguous": contiguous,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def comparison_table(
    summary: pd.DataFrame, metric: str, index: tuple[str, ...] = ("family", "budget_fraction", "n_nodes")
) -> pd.DataFrame:
    return summary.pivot_table(index=list(index), columns="solver", values=metric, aggfunc="first", dropna=False)


def fit_scaling_exponent(
    frame: pd.DataFrame,
    x: str,
    y: str,
    by: str = "solver",
    n_boot: int = 2000,
    seed: int = 0,
    unit: str = "instance_id",
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for key, group in frame.groupby(by, sort=False):
        data = group[[unit, x, y]].dropna()
        log_x, log_y = np.log10(data[x].to_numpy(float)), np.log10(data[y].to_numpy(float))
        slope, intercept = np.polyfit(log_x, log_y, 1)
        residual = log_y - (slope * log_x + intercept)
        r2 = 1 - residual.var() / log_y.var() if log_y.var() > 0 else np.nan
        units = data[unit].unique()
        index = {name: np.flatnonzero(data[unit].to_numpy() == name) for name in units}
        slopes = []
        for _ in range(n_boot):
            chosen = np.concatenate([index[name] for name in rng.choice(units, size=len(units), replace=True)])
            if np.ptp(log_x[chosen]) > 0:
                slopes.append(np.polyfit(log_x[chosen], log_y[chosen], 1)[0])
        rows.append(
            {
                by: key,
                "x": x,
                "y": y,
                "beta": slope,
                "intercept": intercept,
                "ci_low": float(np.quantile(slopes, 0.025)),
                "ci_high": float(np.quantile(slopes, 0.975)),
                "r2": r2,
                "points": len(data),
                "units": len(units),
                "n_boot": n_boot,
            }
        )
    return pd.DataFrame(rows)

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
from matplotlib.ticker import NullLocator

PALETTE = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*")
PAPER_STYLE = {
    "axes.prop_cycle": cycler(color=PALETTE),
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "legend.fontsize": 7.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": "#d9d9d6",
    "lines.linewidth": 1.5,
    "pdf.fonttype": 42,
    "svg.hashsalt": "qmfnip",
}


def plot_metric(
    summary: pd.DataFrame,
    metric: str,
    facet: str | None = "budget_fraction",
    log_x: bool = True,
    log_y: bool = False,
    ylabel: str | None = None,
    path: Path | str | None = None,
) -> plt.Figure:
    facet_values = sorted(summary[facet].dropna().unique()) if facet else [None]
    figure, axes = plt.subplots(
        1, len(facet_values), figsize=(5 * len(facet_values), 4), sharey=True, squeeze=False
    )
    for axis, value in zip(axes[0], facet_values):
        subset = summary if value is None else summary[summary[facet] == value]
        for (solver, family), group in subset.groupby(["solver", "family"]):
            group = group.sort_values("n_nodes")
            axis.plot(group["n_nodes"], group[metric], marker="o", label=f"{solver} ({family})")
        axis.set_title(metric if value is None else f"{facet} = {value}")
        axis.set_xlabel("nodes")
        if log_x:
            axis.set_xscale("log")
            sizes = sorted(subset["n_nodes"].dropna().unique())
            axis.xaxis.set_minor_locator(NullLocator())
            axis.set_xticks(sizes)
            axis.set_xticklabels([f"{size:g}" for size in sizes], rotation=45 if len(sizes) > 6 else 0)
        if log_y:
            axis.set_yscale("log")
        axis.grid(alpha=0.3)
    axes[0][0].set_ylabel(ylabel or metric)
    axes[0][-1].legend()
    figure.tight_layout()
    if path is not None:
        figure.savefig(path, dpi=150)
    return figure


def plot_frontier(frontier_table: pd.DataFrame, path: Path | str | None = None) -> plt.Figure:
    data = frontier_table.copy()
    data["scenario"] = data["family"] + " | b=" + data["budget_fraction"].astype(str)
    scenarios = list(dict.fromkeys(data["scenario"]))
    solvers = list(dict.fromkeys(data["solver"]))
    width = 0.8 / max(len(solvers), 1)
    positions = np.arange(len(scenarios))
    figure, axis = plt.subplots(figsize=(max(6, 1.6 * len(scenarios)), 4))
    for index, solver in enumerate(solvers):
        solver_rows = data[data["solver"] == solver].set_index("scenario").reindex(scenarios)
        heights = pd.to_numeric(solver_rows["n_star_nodes"], errors="coerce").fillna(0).to_numpy()
        bars = axis.bar(positions + index * width, heights, width, label=solver)
        for bar, reached in zip(bars, solver_rows["reached_largest"].fillna(False)):
            if reached:
                bar.set_hatch("//")
    axis.set_xticks(positions + width * (len(solvers) - 1) / 2)
    axis.set_xticklabels(scenarios, rotation=20, ha="right")
    axis.set_ylabel("n* (nodes)")
    axis.set_title("Frontier n* per solver (hatched: lower bound, largest size tested still passed)")
    axis.legend()
    figure.tight_layout()
    if path is not None:
        figure.savefig(path, dpi=150)
    return figure


def plot_scaling(
    frame: pd.DataFrame,
    x: str,
    y: str,
    fits: pd.DataFrame | None = None,
    by: str = "solver",
    labels: dict | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    path: Path | str | None = None,
) -> plt.Figure:
    labels = labels or {}
    figure, axis = plt.subplots(figsize=(6, 4.2))
    span = np.logspace(np.log10(frame[x].min()), np.log10(frame[x].max()), 50)
    for index, (key, group) in enumerate(frame.groupby(by, sort=False)):
        color = f"C{index}"
        axis.scatter(
            group[x], group[y], s=22, color=color, marker=MARKERS[index % len(MARKERS)], alpha=0.85,
            edgecolors="white", linewidths=0.6, label=labels.get(key, key),
        )
        if fits is not None and key in set(fits[by]):
            fit = fits[fits[by] == key].iloc[0]
            axis.plot(
                span, 10 ** fit["intercept"] * span ** fit["beta"], color=color, lw=1.2,
                label=f"fit: $\\beta$ = {fit['beta']:.3f} [{fit['ci_low']:.3f}, {fit['ci_high']:.3f}]",
            )
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel(xlabel or x)
    axis.set_ylabel(ylabel or y)
    axis.grid(alpha=0.3, which="both", lw=0.4)
    axis.legend(fontsize=8)
    figure.tight_layout()
    if path is not None:
        figure.savefig(path, bbox_inches="tight")
    return figure


def plot_amplification(
    frame: pd.DataFrame,
    theory: pd.DataFrame,
    shots: int,
    titles: dict | None = None,
    path: Path | str | None = None,
) -> plt.Figure:
    titles = titles or {}
    variants = list(dict.fromkeys(theory["variant"]))
    environments = list(dict.fromkeys(frame["environment"]))
    figure, axes = plt.subplots(1, len(variants), figsize=(5.2 * len(variants), 3.8), sharey=True, squeeze=False)
    markers = ("o", "s", "^", "D")
    for axis, variant in zip(axes[0], variants):
        expected = theory[theory["variant"] == variant].sort_values("iterations")
        axis.plot(expected["iterations"], expected["probability"], color="black", lw=1, ls="--", marker="x", label="theory")
        for index, environment in enumerate(environments):
            data = frame[(frame["variant"] == variant) & (frame["environment"] == environment)].sort_values("iterations")
            error = np.sqrt(data["frequency"] * (1 - data["frequency"]) / shots)
            offset = (index - (len(environments) - 1) / 2) * 0.08
            axis.errorbar(
                data["iterations"] + offset, data["frequency"], yerr=1.96 * error, fmt=markers[index % len(markers)],
                color=f"C{index}", ms=5, capsize=2, label=environment,
            )
        uniform = float(expected["uniform"].iloc[0])
        axis.axhline(uniform, color="grey", lw=0.8, ls=":", label="uniform baseline 1/N")
        axis.set_title(titles.get(variant, variant))
        axis.set_xlabel("Grover iterations")
        axis.set_xticks(sorted(expected["iterations"].unique()))
        axis.set_ylim(0, 1.05)
        axis.grid(alpha=0.3)
    axes[0][0].set_ylabel("probability of measuring the optimum")
    handles, labels = axes[0][-1].get_legend_handles_labels()
    figure.legend(handles, labels, fontsize=8, loc="lower center", ncol=len(labels), frameon=False, bbox_to_anchor=(0.5, -0.02))
    figure.tight_layout(rect=(0, 0.07, 1, 1))
    if path is not None:
        figure.savefig(path, bbox_inches="tight")
    return figure


def plot_counts(
    frame: pd.DataFrame,
    optimum: str,
    feasible: set[str] | None = None,
    titles: dict | None = None,
    path: Path | str | None = None,
) -> plt.Figure:
    titles = titles or {}
    panels = list(dict.fromkeys(frame["panel"]))
    environments = list(dict.fromkeys(frame["environment"]))
    figure, axes = plt.subplots(1, len(panels), figsize=(5.2 * len(panels), 3.8), sharey=True, squeeze=False)
    width = 0.8 / max(len(environments), 1)
    for axis, panel in zip(axes[0], panels):
        data = frame[frame["panel"] == panel]
        states = sorted(data["state"].unique(), key=lambda state: (state.count("1"), state))
        positions = np.arange(len(states))
        for index, environment in enumerate(environments):
            values = data[data["environment"] == environment].set_index("state").reindex(states)["frequency"].fillna(0)
            bars = axis.bar(positions + index * width, values, width, color=f"C{index}", label=environment)
            for bar, state in zip(bars, states):
                if feasible is not None and state not in feasible:
                    bar.set_hatch("//")
        axis.set_xticks(positions + width * (len(environments) - 1) / 2)
        axis.set_xticklabels([f"{state}*" if state == optimum else state for state in states], rotation=45)
        axis.set_title(titles.get(panel, panel))
        axis.set_xlabel("measured interdiction x (arc order; * optimum)")
        axis.grid(alpha=0.3, axis="y")
    axes[0][0].set_ylabel("relative frequency")
    axes[0][-1].legend(fontsize=8)
    figure.tight_layout()
    if path is not None:
        figure.savefig(path, bbox_inches="tight")
    return figure


def layered_positions(instance, end_gap: float = 1.0) -> dict:
    width = instance.generator_params.get("width")
    layers = instance.generator_params.get("layers")
    middle = (width - 1) / 2
    positions = {instance.s: (1.0 - end_gap, middle), instance.t: (layers + end_gap, middle)}
    for node in range(1, instance.n - 1):
        layer, slot = divmod(node - 1, width)
        positions[node] = (layer + 1.0, float(width - 1 - slot))
    return positions


def network_label_positions(instance, positions: dict, label_pos: float = 0.25) -> list[tuple[float, float]]:
    points = []
    for i, j in instance.arcs.tolist():
        fraction = 0.5 if i == instance.s or j == instance.t else label_pos
        (x0, y0), (x1, y1) = positions[i], positions[j]
        points.append((x0 + fraction * (x1 - x0), y0 + fraction * (y1 - y0)))
    return points


def write_network_tikz(
    instance,
    interdicted: np.ndarray | None = None,
    path: Path | str | None = None,
    positions: dict | None = None,
    x_scale: float = 2.4,
    y_scale: float = 1.3,
    label_pos: float = 0.25,
) -> str:
    if positions is None:
        positions = layered_positions(instance, end_gap=0.65)
    interdicted = np.zeros(instance.m, dtype=bool) if interdicted is None else np.asarray(interdicted, dtype=bool)
    names = {node: "s" if node == instance.s else ("t" if node == instance.t else f"v{node}") for node in positions}
    texts = {node: "$s$" if node == instance.s else ("$t$" if node == instance.t else str(node)) for node in positions}
    lines = [
        "\\begin{tikzpicture}[",
        "  font=\\footnotesize,",
        "  vertex/.style={circle, draw=black, line width=0.4pt, fill=white, inner sep=0pt, minimum size=4.4mm},",
        "  arc/.style={draw=black, line width=0.45pt, -{Stealth[length=1.6mm, width=1.1mm]}},",
        "  removed/.style={arc, draw=qaccent, line width=0.8pt, dash pattern=on 3pt off 1.5pt},",
        "  capacity/.style={fill=white, inner sep=1pt},",
        "]",
    ]
    for node in sorted(positions):
        x, y = positions[node]
        lines.append(f"\\node[vertex] ({names[node]}) at ({x * x_scale:.3f},{y * y_scale:.3f}) {{{texts[node]}}};")
    arcs = list(zip(instance.arcs.tolist(), instance.capacity.tolist(), interdicted.tolist()))
    for (i, j), _, removed in arcs:
        lines.append(f"\\draw[{'removed' if removed else 'arc'}] ({names[i]}) -- ({names[j]});")
    for (x, y), (_, capacity, removed) in zip(network_label_positions(instance, positions, label_pos), arcs):
        style = "capacity, text=qaccent" if removed else "capacity"
        lines.append(f"\\node[{style}] at ({x * x_scale:.3f},{y * y_scale:.3f}) {{{capacity}}};")
    lines.append("\\end{tikzpicture}")
    text = "\n".join(lines) + "\n"
    if path is not None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    return text


def write_scaling_data(
    frame: pd.DataFrame,
    x: str,
    y: str,
    fits: pd.DataFrame,
    directory: Path | str,
    by: str = "solver",
    unit: str = "instance_id",
    stem: str = "scaling",
) -> tuple[Path, Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    points = frame.pivot_table(index=[unit, x], columns=by, values=y, observed=True).reset_index()
    points.columns = [str(column) for column in points.columns]
    points = points.sort_values([x, unit]).reset_index(drop=True)
    span = np.array([frame[x].min(), frame[x].max()], dtype=float)
    lines = pd.DataFrame({x: span})
    for row in fits.itertuples(index=False):
        lines[str(getattr(row, by))] = 10 ** row.intercept * span ** row.beta
    points_path, lines_path = directory / f"{stem}_points.csv", directory / f"{stem}_fits.csv"
    points.to_csv(points_path, index=False, float_format="%.6g")
    lines.to_csv(lines_path, index=False, float_format="%.6g")
    return points_path, lines_path

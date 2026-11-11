import itertools
import math

import numpy as np
import pandas as pd

from qmfnip.grover import search_space
from qmfnip.instances import generate_layered
from qmfnip.plots import layered_positions, network_label_positions, write_network_tikz, write_scaling_data


def test_network_tikz_draws_every_arc_and_separates_labels(tmp_path):
    instance = generate_layered(3, 0, budget=2, cost_range=(1, 1))
    space = search_space(instance)
    plan = space.interdictions[space.optimal_indices[0]]
    path = tmp_path / "network.tex"
    text = write_network_tikz(instance, plan, path)
    assert path.read_text() == text
    assert text.startswith("\\begin{tikzpicture}") and text.rstrip().endswith("\\end{tikzpicture}")
    assert text.count("\\draw[arc]") + text.count("\\draw[removed]") == instance.m
    assert text.count("\\draw[removed]") == int(plan.sum())
    assert text.count("text=qaccent") == int(plan.sum())
    points = np.array(network_label_positions(instance, layered_positions(instance, end_gap=0.65))) * (2.4, 1.3)
    assert min(math.dist(a, b) for a, b in itertools.combinations(points, 2)) >= 0.3


def test_scaling_data_writes_points_and_fit_endpoints(tmp_path):
    frame = pd.DataFrame(
        {
            "solver": ["a", "b", "a", "b"],
            "instance_id": ["i1", "i1", "i2", "i2"],
            "N": [10, 10, 1000, 1000],
            "mean_cost": [3.0, 9.0, 30.0, 900.0],
        }
    )
    fits = pd.DataFrame({"solver": ["a", "b"], "beta": [0.5, 1.0], "intercept": [0.0, -0.05]})
    points_path, fits_path = write_scaling_data(frame, "N", "mean_cost", fits, tmp_path / "data")
    points = pd.read_csv(points_path)
    lines = pd.read_csv(fits_path)
    assert list(points.columns) == ["instance_id", "N", "a", "b"]
    assert points["b"].tolist() == [9.0, 900.0]
    assert lines["N"].tolist() == [10, 1000]
    assert np.allclose(lines["a"], [10**0.5, 10**1.5], rtol=1e-5)
    assert np.allclose(lines["b"], 10**-0.05 * np.array([10, 1000]), rtol=1e-5)

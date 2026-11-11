import json
import re

import pandas as pd
import pytest

from qmfnip.instances import Scenario
from qmfnip.outputs import latest_experiment
from qmfnip.playground import ExperimentConfig, run_experiment
from qmfnip.solvers import BruteForceSolver, MILPSolver, Solver

SCENARIO = Scenario("random", sizes=(5, 6), budget_fractions=(0.5,), seeds=(0, 1), params={"arc_factor": 2.0})


class HardwareSolver(Solver):
    short_name = "fake_qpu"

    def requires_hardware(self) -> bool:
        return True


def make_config(tmp_path, **overrides) -> ExperimentConfig:
    settings = {
        "scenario": SCENARIO,
        "solvers": [MILPSolver(), BruteForceSolver()],
        "repetitions": 2,
        "time_limit": 30.0,
        "output_root": tmp_path,
    }
    return ExperimentConfig(**{**settings, **overrides})


def test_experiment_writes_organized_outputs(tmp_path):
    output = run_experiment(make_config(tmp_path), verbose=False)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}__milp-brute_force__random__n5-6__runs2", output.path.name)
    manifest = output.read_json("manifest.json")
    environment = output.read_json("environment.json")
    assert manifest["status"] == "completed"
    assert len(manifest["instances"]) == 4
    assert {"python", "system", "hardware", "packages", "git"} <= environment.keys()
    assert len(list((output.path / "instances").glob("*.json"))) == 4
    assert (output.path / "runs" / "milp__random__n5-6__runs2.csv").exists()
    assert (output.path / "runs" / "brute_force__random__n5-6__runs2.csv").exists()
    runs = output.load_runs()
    assert len(runs) == 4 * 2 * 2
    assert (runs["gap"] == 0.0).all()
    assert runs["instance_hash"].nunique() == 4
    assert latest_experiment(tmp_path).path == output.path


def test_all_solvers_receive_identical_instances(tmp_path):
    runs = run_experiment(make_config(tmp_path, repetitions=1), verbose=False).load_runs()
    hashes = runs.groupby("instance_id")["instance_hash"].nunique()
    solvers = runs.groupby("instance_id")["solver"].nunique()
    assert (hashes == 1).all()
    assert (solvers == 2).all()


def test_resume_completes_only_missing_runs(tmp_path):
    config = make_config(tmp_path)
    output = run_experiment(config, verbose=False)
    records_path = output.path / "runs" / "records.jsonl"
    records = records_path.read_text().splitlines()
    records_path.write_text("\n".join(records[:5]) + "\n")
    (output.path / "runs_all.csv").unlink()
    resumed = run_experiment(config, resume=output.path, verbose=False)
    runs = resumed.load_runs()
    assert len(runs) == 16
    assert not runs.duplicated(["instance_id", "solver", "repetition"]).any()
    assert len(resumed.read_json("manifest.json")["resumed_at"]) == 1


def test_resume_rejects_different_instances(tmp_path):
    output = run_experiment(make_config(tmp_path, repetitions=1), verbose=False)
    other = make_config(tmp_path, scenario=Scenario("random", sizes=(5,), seeds=(7,)), repetitions=1)
    with pytest.raises(ValueError):
        run_experiment(other, resume=output.path, verbose=False)


def test_hardware_solvers_are_blocked_by_default(tmp_path):
    with pytest.raises(PermissionError):
        run_experiment(make_config(tmp_path, solvers=[HardwareSolver()]), verbose=False)
    assert list(tmp_path.iterdir()) == []


def test_duplicate_solver_labels_are_rejected(tmp_path):
    with pytest.raises(ValueError):
        run_experiment(make_config(tmp_path, solvers=[MILPSolver(), MILPSolver()]), verbose=False)


def test_reference_is_computed_once_per_instance(tmp_path):
    output = run_experiment(make_config(tmp_path), verbose=False)
    references = pd.DataFrame(output.read_records("references.jsonl"))
    assert len(references) == 4
    assert references["certified"].all()
    assert json.loads(output.load_runs()["solver_params"].iloc[0]) == {}

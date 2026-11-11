import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

from .instances import Instance

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
EXPERIMENT_NAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}__")
TRACKED_PACKAGES = (
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "psutil",
    "qiskit",
    "qiskit-aer",
    "qiskit-ibm-runtime",
    "qmfnip",
)


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def _run_command(arguments: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            arguments, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def capture_environment() -> dict:
    cpu_model = platform.processor() or platform.machine()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        models = [line.split(":", 1)[1].strip() for line in cpuinfo.read_text().splitlines() if line.startswith("model name")]
        cpu_model = models[0] if models else cpu_model
    frequency = psutil.cpu_freq()
    gpu = None
    if shutil.which("nvidia-smi"):
        gpu = _run_command(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    packages = {}
    for package in TRACKED_PACKAGES:
        try:
            packages[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            packages[package] = None
    git_status = _run_command(["git", "status", "--porcelain"])
    captured_at = datetime.now().astimezone()
    return {
        "captured_at": captured_at.isoformat(timespec="seconds"),
        "timezone": str(captured_at.tzinfo),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "virtual_environment": sys.prefix != sys.base_prefix,
        },
        "system": {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "hardware": {
            "cpu_model": cpu_model,
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_max_mhz": frequency.max if frequency else None,
            "memory_total_gb": round(psutil.virtual_memory().total / 2**30, 2),
            "gpu": gpu,
        },
        "packages": packages,
        "solver_backends": {
            "milp": "HiGHS bundled with SciPy; thread count is not configurable through scipy.optimize.milp",
        },
        "git": {
            "commit": _run_command(["git", "rev-parse", "HEAD"]),
            "branch": _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
            "dirty": None if git_status is None else bool(git_status),
        },
    }


class ExperimentOutput:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    @property
    def experiment_id(self) -> str:
        return self.path.name

    @classmethod
    def create(
        cls,
        solver_labels: list[str],
        family: str,
        n_nodes: list[int],
        repetitions: int,
        root: Path | str = DEFAULT_OUTPUT_ROOT,
    ) -> "ExperimentOutput":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        solvers_label = "-".join(solver_labels) if len(solver_labels) <= 4 else "multi"
        size_label = f"n{min(n_nodes)}-{max(n_nodes)}"
        base_name = f"{timestamp}__{solvers_label}__{family}__{size_label}__runs{repetitions}"
        path = Path(root) / base_name
        suffix = 1
        while path.exists():
            path = Path(root) / f"{base_name}-{suffix}"
            suffix += 1
        for folder in ("instances", "runs", "figures"):
            (path / folder).mkdir(parents=True)
        output = cls(path)
        output.update_manifest(
            {
                "experiment_id": output.experiment_id,
                "naming": {"family": family, "size_label": size_label, "repetitions": repetitions},
            }
        )
        return output

    def write_json(self, relative: str, data) -> Path:
        target = self.path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(to_jsonable(data), indent=2, ensure_ascii=False))
        return target

    def read_json(self, relative: str):
        target = self.path / relative
        return json.loads(target.read_text()) if target.exists() else None

    def update_manifest(self, fields: dict) -> dict:
        manifest = self.read_json("manifest.json") or {}
        manifest.update(to_jsonable(fields))
        self.write_json("manifest.json", manifest)
        return manifest

    def append_record(self, relative: str, record: dict) -> None:
        target = self.path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a") as handle:
            handle.write(json.dumps(to_jsonable(record), ensure_ascii=False) + "\n")

    def read_records(self, relative: str) -> list[dict]:
        target = self.path / relative
        if not target.exists():
            return []
        return [json.loads(line) for line in target.read_text().splitlines() if line.strip()]

    def write_instance(self, instance: Instance) -> Path:
        return self.write_json(f"instances/{instance.instance_id}.json", instance.to_dict())

    def load_instances(self) -> dict[str, Instance]:
        instances = {}
        for path in sorted((self.path / "instances").glob("*.json")):
            instance = Instance.from_dict(json.loads(path.read_text()))
            instances[instance.instance_id] = instance
        return instances

    def write_runs(self, runs: pd.DataFrame) -> None:
        naming = self.read_json("manifest.json")["naming"]
        suffix = f"{naming['family']}__{naming['size_label']}__runs{naming['repetitions']}"
        for solver, solver_runs in runs.groupby("solver", sort=False):
            solver_runs.to_csv(self.path / "runs" / f"{solver}__{suffix}.csv", index=False)
        runs.to_csv(self.path / "runs_all.csv", index=False)

    def load_runs(self, from_records: bool = False) -> pd.DataFrame:
        consolidated = self.path / "runs_all.csv"
        if consolidated.exists() and not from_records:
            return pd.read_csv(consolidated)
        return pd.DataFrame(self.read_records("runs/records.jsonl"))

    def write_table(self, name: str, table: pd.DataFrame) -> Path:
        target = self.path / f"{name}.csv"
        table.to_csv(target, index=False)
        return target

    def figure_path(self, name: str) -> Path:
        return self.path / "figures" / f"{name}.png"


def latest_experiment(root: Path | str = DEFAULT_OUTPUT_ROOT, contains: str | None = None) -> ExperimentOutput:
    candidates = sorted(
        path
        for path in Path(root).iterdir()
        if path.is_dir() and EXPERIMENT_NAME_PATTERN.match(path.name) and (contains is None or contains in path.name)
    )
    if not candidates:
        raise FileNotFoundError(f"No experiment found in {root}" + (f" containing '{contains}'" if contains else ""))
    return ExperimentOutput(candidates[-1])


def write_latex_table(
    frame: pd.DataFrame,
    path: Path | str,
    caption: str,
    label: str,
    column_format: str | None = None,
    headers: list[str] | None = None,
    notes: str | None = None,
    size: str = "small",
    wide: bool = False,
) -> Path:
    headers = headers or [str(column) for column in frame.columns]
    column_format = column_format or "l" + "r" * (len(frame.columns) - 1)
    environment = "table*" if wide else "table"
    lines = [
        f"\\begin{{{environment}}}[t]",
        "\\centering",
        f"\\caption{{{caption}}}\\label{{{label}}}",
        f"\\{size}",
        f"\\begin{{tabular}}{{{column_format}}}",
        "\\toprule",
        " & ".join(headers) + " \\\\",
        "\\midrule",
    ]
    for row in frame.itertuples(index=False):
        lines.append(" & ".join(str(value) for value in row) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    if notes:
        lines.append(f"\\par\\smallskip\\parbox{{0.95\\linewidth}}{{\\footnotesize {notes}}}")
    lines.append(f"\\end{{{environment}}}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n")
    return target

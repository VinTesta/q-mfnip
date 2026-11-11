import math
import time
from collections.abc import Callable, Sequence
from datetime import datetime

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit.library import IntegerComparatorGate, MCXGate, RYGate, WeightedSumGate, ZGate, grover_operator
from qiskit.transpiler import PassManager, generate_preset_pass_manager
from qiskit.transpiler.passes import HighLevelSynthesis

from .instances import Instance

BASIS = ["cx", "u"]
TWO_QUBIT_GATES = ("cx", "cz", "ecr", "swap", "rzz", "cy", "cp", "crx", "cry", "crz")
FREE_PRICING = "free"


def unary_weights(m: int, k: int) -> np.ndarray:
    counts = np.array([math.comb(m, weight) for weight in range(k + 1)], dtype=float)
    return counts / counts.sum()


def state_preparation(m: int, k: int | None = None) -> QuantumCircuit:
    circuit = QuantumCircuit(m, name=f"A_{m}" if k is None else f"A_{m},{k}")
    if k is None or k >= m:
        circuit.h(range(m))
        return circuit
    if k <= 0:
        return circuit
    weights = unary_weights(m, k)
    tail = np.cumsum(weights[::-1])[::-1]
    for level in range(1, k + 1):
        probability = tail[level] / tail[level - 1]
        angle = 2 * math.asin(math.sqrt(min(1.0, probability)))
        target = m - level
        if level == 1:
            circuit.ry(angle, target)
        else:
            circuit.cry(angle, target + 1, target)
    for size in range(m, 1, -1):
        block = min(k, size - 1)
        last = size - 1
        circuit.cx(last - 1, last)
        circuit.cry(2 * math.acos(math.sqrt(1 / size)), last, last - 1)
        circuit.cx(last - 1, last)
        for weight in range(2, block + 1):
            pivot = last - weight
            circuit.cx(pivot, last)
            circuit.append(RYGate(2 * math.acos(math.sqrt(weight / size))).control(2, annotated=False), [last, pivot + 1, pivot])
            circuit.cx(pivot, last)
    return circuit


def phase_oracle(m: int, marked: Sequence[Sequence[int]]) -> QuantumCircuit:
    circuit = QuantumCircuit(m, name="O_tau")
    for state in marked:
        zeros = [qubit for qubit in range(m) if not state[qubit]]
        if zeros:
            circuit.x(zeros)
        if m == 1:
            circuit.z(0)
        else:
            circuit.append(ZGate().control(m - 1, annotated=False), list(range(m)))
        if zeros:
            circuit.x(zeros)
    return circuit


def grover_circuit(
    preparation: QuantumCircuit, oracle: QuantumCircuit, iterations: int, measure: bool = True
) -> QuantumCircuit:
    circuit = QuantumCircuit(preparation.num_qubits, name=f"grover_{iterations}")
    circuit.compose(preparation, inplace=True)
    if iterations:
        operator = grover_operator(oracle, state_preparation=preparation)
        for _ in range(iterations):
            circuit.compose(operator, inplace=True)
    if measure:
        circuit.measure_all()
    return circuit


def synthesize(circuit: QuantumCircuit, qubits_initially_zero: bool) -> QuantumCircuit:
    manager = PassManager([HighLevelSynthesis(basis_gates=BASIS, qubits_initially_zero=qubits_initially_zero)])
    return transpile(manager.run(circuit), basis_gates=BASIS, optimization_level=0)


def arithmetic_oracle(instance: Instance, threshold: int) -> QuantumCircuit:
    m, inner = instance.m, [node for node in range(instance.n) if node not in (instance.s, instance.t)]
    position = {node: index for index, node in enumerate(inner)}
    active = [a for a, (i, j) in enumerate(instance.arcs.tolist()) if i != instance.t and j != instance.s]
    adder = WeightedSumGate(len(active), [int(instance.capacity[a]) for a in active])
    sum_bits = adder.num_sum_qubits
    comparator = IntegerComparatorGate(sum_bits, int(threshold), geq=False)
    x_register = QuantumRegister(m, "x")
    alpha_register = QuantumRegister(len(inner), "alpha")
    gamma_register = QuantumRegister(len(active), "gamma")
    sum_register = QuantumRegister(sum_bits, "sum")
    flag = QuantumRegister(1, "flag")
    carry = QuantumRegister(adder.num_qubits - len(active) - sum_bits, "carry")
    work = QuantumRegister(max(sum_bits - 1 + int(sum_bits > 2), 0), "work")
    registers = [x_register, alpha_register, gamma_register, sum_register, flag, carry, work]
    cuts = QuantumCircuit(x_register, alpha_register, gamma_register)
    for slot, a in enumerate(active):
        i, j = instance.arcs[a].tolist()
        controls, state = [x_register[a]], "0"
        if i != instance.s:
            controls.append(alpha_register[position[i]])
            state = "0" + state
        if j != instance.t:
            controls.append(alpha_register[position[j]])
            state = "1" + state
        cuts.append(MCXGate(len(controls), ctrl_state=state), [*controls, gamma_register[slot]])
    arithmetic = QuantumCircuit(gamma_register, sum_register, flag, carry, work)
    arithmetic.append(adder, [*gamma_register, *sum_register, *carry])
    arithmetic.append(comparator, [*sum_register, flag[0]])
    compute = QuantumCircuit(*registers)
    compute.compose(synthesize(cuts, False), qubits=[*x_register, *alpha_register, *gamma_register], inplace=True)
    compute.compose(
        synthesize(arithmetic, True), qubits=[*gamma_register, *sum_register, *flag, *carry, *work], inplace=True
    )
    circuit = QuantumCircuit(*registers, name="O_tau_arith")
    circuit.compose(compute, inplace=True)
    circuit.z(flag[0])
    circuit.compose(compute.inverse(), inplace=True)
    return circuit


def cut_capacity(instance: Instance, alpha: dict[int, int], interdicted: Sequence[int]) -> int:
    side = {instance.s: 0, instance.t: 1, **alpha}
    return int(
        sum(
            instance.capacity[a]
            for a, (i, j) in enumerate(instance.arcs.tolist())
            if side[i] == 0 and side[j] == 1 and not interdicted[a]
        )
    )


def circuit_resources(circuit: QuantumCircuit, backend=None, seed: int = 0, optimization_level: int = 1) -> dict:
    start = time.perf_counter()
    if backend is None:
        compiled = transpile(circuit, basis_gates=["cx", "u"], optimization_level=optimization_level, seed_transpiler=seed)
    else:
        manager = generate_preset_pass_manager(optimization_level=optimization_level, backend=backend, seed_transpiler=seed)
        compiled = manager.run(circuit)
    elapsed = time.perf_counter() - start
    operations = compiled.count_ops()
    active = {compiled.find_bit(qubit).index for instruction in compiled.data for qubit in instruction.qubits}
    return {
        "backend": "logical" if backend is None else backend.name,
        "logical_qubits": circuit.num_qubits,
        "physical_qubits": len(active),
        "two_qubit_gates": int(sum(count for name, count in operations.items() if name in TWO_QUBIT_GATES)),
        "total_gates": int(sum(count for name, count in operations.items() if name not in ("barrier", "measure"))),
        "circuit_depth": compiled.depth(),
        "two_qubit_depth": compiled.depth(lambda instruction: instruction.operation.num_qubits == 2),
        "compile_time_s": elapsed,
        "operations": dict(operations),
    }


def is_hardware(backend) -> bool:
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider.fake_backend import FakeBackendV2

    return not isinstance(backend, (AerSimulator, FakeBackendV2))


def free_plan_backend(name: str | None = None):
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.accounts import AccountManager

    instances = AccountManager.get().list_instances()
    free = [item for item in instances if item["pricing_type"] == FREE_PRICING]
    if not free:
        plans = sorted({f"{item['plan']} ({item['pricing_type']})" for item in instances})
        raise PermissionError(f"No free IBM Quantum instance; found {plans or 'no instances'}. Paid instances are never used")
    service = QiskitRuntimeService(instance=free[0]["crn"])
    return service.backend(name) if name else service.least_busy(operational=True, simulator=False)


def require_free_plan(backend) -> None:
    instance = getattr(backend, "_instance", None)
    pricing = {item["crn"]: item["pricing_type"] for item in backend.service.instances()}
    if pricing.get(instance) != FREE_PRICING:
        raise PermissionError(f"{backend.name} runs on instance with pricing {pricing.get(instance)!r}; only free plans are allowed")


def sample_circuits(
    circuits: Sequence[QuantumCircuit],
    backend,
    shots: int,
    seed: int = 0,
    allow_hardware: bool = False,
    optimization_level: int = 3,
    on_submit: Callable[[dict], None] | None = None,
    job=None,
) -> dict:
    from qiskit_ibm_runtime import SamplerV2

    hardware = is_hardware(backend)
    if hardware and not allow_hardware:
        raise PermissionError(f"{backend.name} is quantum hardware; validate on simulators and pass allow_hardware=True")
    if hardware and job is None:
        require_free_plan(backend)
    manager = generate_preset_pass_manager(optimization_level=optimization_level, backend=backend, seed_transpiler=seed)
    compiled = [manager.run(circuit) for circuit in circuits]
    if job is None:
        sampler = SamplerV2(mode=backend)
        if not hardware:
            sampler.options.simulator.seed_simulator = seed
        submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
        job = sampler.run(compiled, shots=shots)
        submission = {"job_id": job.job_id(), "backend": backend.name, "submitted_at": submitted_at, "shots": shots}
        if on_submit is not None:
            on_submit(submission)
    else:
        submission = {"job_id": job.job_id(), "backend": backend.name, "submitted_at": None, "shots": shots}
    result = job.result()
    counts = []
    for circuit, item in zip(circuits, result):
        raw = item.data.meas.get_counts()
        counts.append({key[::-1][: circuit.num_qubits]: value for key, value in raw.items()})
    metadata = {
        **submission,
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "hardware": hardware,
        "transpiled": [
            {
                "name": circuit.name,
                "depth": compiled_circuit.depth(),
                "two_qubit_gates": int(
                    sum(count for name, count in compiled_circuit.count_ops().items() if name in TWO_QUBIT_GATES)
                ),
                "operations": dict(compiled_circuit.count_ops()),
            }
            for circuit, compiled_circuit in zip(circuits, compiled)
        ],
    }
    if hardware:
        for attribute in ("usage", "metrics"):
            try:
                metadata[attribute] = getattr(job, attribute)()
            except Exception as error:
                metadata[attribute] = f"unavailable: {type(error).__name__}"
    return {"counts": counts, "metadata": metadata}

import itertools
import math

import numpy as np
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

from qmfnip.grover import GroverSampler, search_space
from qmfnip.instances import Instance, generate_layered
from qmfnip.oracle import (
    arithmetic_oracle,
    circuit_resources,
    cut_capacity,
    grover_circuit,
    phase_oracle,
    sample_circuits,
    state_preparation,
)


def basis_index(bits) -> int:
    return int(sum(int(bit) << position for position, bit in enumerate(bits)))


@pytest.mark.parametrize(("m", "k"), [(m, k) for m in range(1, 7) for k in range(m + 1)])
def test_state_preparation_is_uniform_over_budget(m, k):
    amplitudes = Statevector(state_preparation(m, k)).data
    feasible = np.array([index.bit_count() <= k for index in range(2**m)])
    expected = np.where(feasible, 1 / math.sqrt(feasible.sum()), 0.0)
    assert np.abs(amplitudes - expected).max() <= 1e-10


@pytest.mark.parametrize(
    "instance",
    [generate_layered(2, seed, budget=budget, cost_range=(1, 1)) for seed in (0, 2) for budget in (1, 2)],
    ids=lambda instance: instance.instance_id,
)
def test_grover_circuit_matches_query_level_model(instance):
    space = search_space(instance)
    sampler = GroverSampler(space, np.random.default_rng(0))
    preparation = state_preparation(instance.m, instance.budget)
    indices = [basis_index(row) for row in space.interdictions]
    for threshold in sorted({space.optimum + 1, int(np.median(space.flows))}):
        marked = space.interdictions[space.flows < threshold].astype(int).tolist()
        oracle = phase_oracle(instance.m, marked)
        for iterations in range(4):
            probabilities = Statevector(grover_circuit(preparation, oracle, iterations, measure=False)).probabilities()
            model = sampler.probabilities(threshold, iterations)
            assert np.abs(probabilities[indices] - model).max() <= 1e-10
            assert probabilities[indices].sum() == pytest.approx(1.0, abs=1e-10)


def test_arithmetic_oracle_marks_exactly_the_cheap_cuts():
    from qiskit_aer import AerSimulator

    instance = Instance(
        n=4,
        arcs=np.array([[0, 1], [0, 2], [1, 2], [1, 3], [2, 3]]),
        capacity=np.array([1, 1, 1, 1, 2]),
        cost=np.ones(5, dtype=int),
        budget=1,
    )
    threshold = 2
    oracle = arithmetic_oracle(instance, threshold)
    searched = instance.m + instance.n - 2
    circuit = QuantumCircuit(oracle.num_qubits)
    circuit.h(range(searched))
    circuit.compose(oracle, inplace=True)
    circuit.save_statevector()
    simulator = AerSimulator(method="statevector")
    state = np.asarray(simulator.run(transpile(circuit, simulator, optimization_level=0)).result().get_statevector())
    scale = 1 / math.sqrt(2**searched)
    assert np.abs(state[2**searched:]).max() <= 1e-9
    signs = []
    for bits in itertools.product((0, 1), repeat=searched):
        x, alpha = bits[: instance.m], bits[instance.m :]
        cut = cut_capacity(instance, {1: alpha[0], 2: alpha[1]}, x)
        sign = -1 if cut < threshold else 1
        signs.append(sign)
        assert state[basis_index(bits)] == pytest.approx(sign * scale, abs=1e-9)
    assert -1 in signs and 1 in signs


def test_circuit_resources_reports_two_qubit_gates():
    resources = circuit_resources(state_preparation(5, 2))
    assert resources["logical_qubits"] == 5
    assert resources["two_qubit_gates"] > 0
    assert resources["circuit_depth"] > 0


def test_sampling_refuses_hardware_without_permission():
    class RealBackend:
        name = "ibm_real_device"

    with pytest.raises(PermissionError):
        sample_circuits([QuantumCircuit(1)], RealBackend(), shots=10)


@pytest.mark.parametrize("pricing", ["paygo", "paid", "subscription", "unknown"])
def test_sampling_refuses_hardware_on_paid_plans(pricing):
    class Service:
        def instances(self):
            return [{"crn": "crn:paid", "plan": "pay-as-you-go", "pricing_type": pricing}]

    class PaidBackend:
        name = "ibm_paid_device"
        service = Service()
        _instance = "crn:paid"

    with pytest.raises(PermissionError, match="only free plans"):
        sample_circuits([QuantumCircuit(1)], PaidBackend(), shots=10, allow_hardware=True)


def test_ideal_sampling_returns_interdictions_in_arc_order():
    from qiskit_aer import AerSimulator

    circuit = QuantumCircuit(3)
    circuit.x(0)
    circuit.measure_all()
    result = sample_circuits([circuit], AerSimulator(), shots=50, seed=1)
    assert result["counts"][0] == {"100": 50}

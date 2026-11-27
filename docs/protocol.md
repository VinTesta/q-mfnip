# Experimental protocol (FROZEN on 2026-11-06, 09:40)

> **About this file.** This is the English version of the experimental protocol and the reference cited by the paper and by the README. Sections 0 to 7 are a translation, made on 2026-11-26, of the Portuguese text frozen on 2026-11-06 at 09:40 (local time, UTC−3), which is kept unchanged in [`protocol.pt.md`](protocol.pt.md). Section 8 is the log of deviations and is maintained only in this file.
>
> Notes on the translation:
> - The protocol numbers the two hypotheses H4 and H5, because an earlier version of the project had hypotheses H1 to H3 (Section 0.1). The paper calls them H1 (scaling in simulation) and H2 (hardware). The output files keep the original names (`h4.json`, `h5.json`).
> - The original cites three internal planning notes that are not part of this repository. They are replaced below by "[internal planning note, not in this repository]". D1 and D4 identify two decisions recorded in those notes, and P0 is the first step of one of them.
> - The table in Section 3 gives the largest N as approximately 971,000. The exact value, used in the paper, is 974,121.
> - Text in square brackets was added in translation.

Status: **frozen**. Rewritten on 2026-11-05 for the new direction of the paper ([internal planning note, not in this repository]) and adjusted on 2026-11-06 by decision D1. Freezing date (step P0 of [internal planning note, not in this repository], before E1): **2026-11-06, 09:40**, with the defaults of decision D4. Any change from this point on goes to Section 8 (deviations), with its reason.

## 0. Changes of scope

### 0.1 Removal of QUBO, QA and QAOA (2026-11-05)
This protocol used to cover the comparison between quantum annealing, QAOA and classical methods on a QUBO formulation of the MFNIP. **QUBO, QA and QAOA were removed from the paper**, and with them:
- hypotheses H1 (quality), H2 (time) and H3 (scale);
- the parameters Z, p and T of the frontier n\*.

The paper now studies the **quantum minimum search of Dürr–Høyer** applied to the MFNIP:
- the **interface** that allows the algorithm to run on the problem (encoding, state preparation and oracle);
- the **proven theoretical advantage** over classical exhaustive search;
- the **comparison with exhaustive search** in classical computing.

The MILP remains as the reference optimum and as practical context.

### 0.2 Feasible search space (decision D1, 2026-11-06)
- **Problem:** with a non-degenerate budget, the interdictions that fit in the budget are fewer than √(2^m) (m = 20: 222 against 1,024). Exhaustive search over 2^m would be a straw-man rival.
- **Decision:** the search, quantum and classical, is now over the feasible interdictions of the **cardinality variant**: unit cost and up to k arcs, F_k = {x : |x| ≤ k}, N = |F_k| = Σ_{i≤k} C(m, i).
- **Preparation:** the uniform initial state over F_k is prepared with the Dicke circuit.
- **Arbitrary costs:** they remain as a declared limitation.

Details in [internal planning note, not in this repository], Section 0.

## 1. Question, proposition and hypotheses
**Question:** what advantage does a quantum search algorithm offer over classical exhaustive search for the MFNIP, at what cost in resources, and how does this compare with the classical state of practice?

- **Proposition 1 (proved).** With N = |F_k|:
  - the Dürr–Høyer search, with the preparation A_k and the oracle O_τ (both with poly(n, m) gates), finds an optimal interdiction with probability ≥ 1/2 using O(√N) applications of A_k and O_τ;
  - a classical search that accesses the flows only by evaluation needs Ω(N) evaluations in the worst case.
- **H4 (scaling, simulation).** The mean cost (oracle queries + classical evaluations) until the optimum is measured grows as N^β with β ∈ [0.4, 0.6]. Classical search in random order over F_k grows with an exponent close to 1.
- **H5 (IBM hardware).** On an instance with m = 3, k = 1 and a unique optimum, the frequency of the optimal interdiction measured after the ideal number of iterations is significantly greater than 1/N.
- **Characterization:** qubits, two-qubit gates and depth of the Dicke preparation and of the realizations of the oracle, as a function of m and n.

## 2. Parameters and refutation criteria
The values below are the defaults of decision D4, adopted at freezing (the user [the author] asked for the plan to be followed without changing them).
- **Interval of β (H4):** [0.4, 0.6].
- **Significance level (H5):** 0.05, one-sided binomial test.
- **H4 is refuted if:** the fitted β, with a 95% CI from a *bootstrap* over instances, falls outside the interval.
- **H5 is refuted if:** the frequency of the optimum on the hardware is not significantly greater than 1/N.

## 3. Instances
- Families of `src/qmfnip/instances.py`, with fixed seeds and a hash of the content.
- **Unit cost and budget k < κ** (κ = cost of the cut that brings the flow to zero). This guarantees an optimum greater than zero; the degeneracy at the other extreme (optimum equal to the original flow) is checked on each instance.
- **H4 (E1):**
  - layered family, widths w = 2 to 5 (κ = w), k = 1 to w − 1, seeds 0, 1 and 2;
  - 30 instances, with N = |F_k| from 9 to ~971 thousand.

  | w | m | k = 1 | k = 2 | k = 3 | k = 4 |
  |---|---|---|---|---|---|
  | 2 | 8 | 9 | — | — | — |
  | 3 | 24 | 25 | 301 | — | — |
  | 4 | 44 | 45 | 991 | 14,235 | — |
  | 5 | 70 | 71 | 2,486 | 57,226 | ~971,000 |

- **H5 (E3):** m = 3, k = 1, κ ≥ 2, unique optimum (M = 1), chosen automatically among small instances of the generator.

## 4. Methods
| Method | Role | Platform |
|---|---|---|
| Dürr–Høyer, full state vector | Validation of the reduced simulator | numpy, N ≤ 2^14 |
| Dürr–Høyer, reduced simulator (two-state plane) | Scaling (H4) | numpy, N up to ~10⁶ |
| Grover with Dicke preparation and truth-table oracle | Demonstration (H5), "interface" variant (N = 4) | Qiskit: ideal simulator, `FakeFez`, IBM hardware |
| Grover with H^⊗m and truth-table oracle | Demonstration (H5), "hypercube" variant (N = 8) | Same |
| Deterministic enumeration of F_k | Rival of Proposition 1 (certifies with N evaluations) | Classical |
| Classical search in random order over F_k | Rival with the same probabilistic guarantee (H4) | Classical |
| MILP (HiGHS) | Reference optimum and practical context | Classical |

## 5. Metrics
- **Cost:** oracle queries (each Grover iteration = 1) plus classical evaluations (each checked candidate = 1), until the optimum is measured for the first time.
- **Exponent β** of the log-log regression against N and against N/M, with 95% CI.
- **Success probability** within the theoretical query budget of Dürr–Høyer (22.5√N + 1.4 log₂²N; constant to be checked against the original paper).
- **Resources:** logical qubits, two-qubit gates and depth, logical and after transpilation to `FakeFez`.
- **Hardware:** frequency of each measured interdiction, p-value of the binomial test, device, date, transpiled depth, QPU and queue times, job id.
- **Context:** time of the MILP and of the enumeration on the instances of E1; scaling study of notebook `01`.

## 6. Repetitions
- Runs per instance and method in E1 (R): 200 (default of D4).
- *Shots* on the hardware: 4,096 per circuit (default of D4).
- Seeds derived and recorded in every run.

## 7. Hardware protocol
1. Every circuit runs first on the ideal simulator and then on `FakeFez` (with noise).
2. It goes to the IBM hardware only if the ideal simulator reproduces the theory (each frequency within 3 standard errors) and if `allow_hardware=True` is explicitly enabled.
3. The job id is written to `outputs/` before waiting for the result.
4. Record: device, date, SDK version, number of iterations, *shots*, depth and two-qubit gates after transpilation, QPU and queue times.

## 8. Deviations from the protocol

The frozen text has no entry in this section, only the placeholder "(record here any change made after freezing, with its reason)". The entries below were written on 2026-11-26, during the revision of the paper for submission. Each one states when the deviation happened.

### 8.1 Exploratory comparison of the hardware with theory and with the noise model
- **What:** besides the test of H5 against 1/N, the frequency of the optimal interdiction on `ibm_fez` is compared with the theoretical probability (ratio and 95% Wilson interval) and with the frequency on `FakeFez` (two-sided Fisher exact test).
- **When:** defined after the hardware run of 2026-11-06, with the results already known. The exact date was not recorded. The comparison was already in the first public version of this repository (2026-11-11).
- **Reason:** the baseline 1/N of H5 is weak, because any circuit that works at all passes it.
- **Effect:** none on the verdict of H5. The paper reports the comparison as exploratory and not as a test of a hypothesis fixed in advance. It is computed by notebook `05` from the stored counts, with no new run.

### 8.2 Reading of the refutation criterion of H4 and additional check
- **What:** Section 2 states the criterion as "the fitted β, with a 95% CI [...], falls outside the interval". The paper takes the decision on the point estimate and reports the confidence interval. The paper also reports whether the confidence interval contains the theoretical value 0.5.
- **When:** the reading of the criterion is the one implemented in notebook `02` for E1. The check against 0.5 was added after E1.
- **Reason:** the sentence in Section 2 does not say whether the point estimate or the whole interval decides. The check against 0.5 was added because the interval [0.4, 0.6] is wide for a theoretical value of 0.5.
- **Effect:** none on the verdict of H4. The point estimate (0.494) and the whole confidence interval ([0.460, 0.523]) lie inside [0.4, 0.6], and `h4.json` records both. The check against 0.5 is not part of the criterion.

### 8.3 Tolerance of the acceptance check on the ideal simulator
- **What:** Section 7 requires each frequency on the ideal simulator to be within 3 standard errors of theory. Notebook `04` adds 1/shots to this tolerance.
- **When:** in the implementation used for E3 on 2026-11-06.
- **Reason:** the standard error is zero when the theoretical probability is 0 or 1, as in the interface variant after one iteration.
- **Effect:** none. The eight circuits of E3 also satisfy the criterion of Section 7 without the additional term.

### 8.4 Extension of the resource counts (E2) to larger networks
- **What:** the counts of qubits, two-qubit gates and depth of Section 1 ("Characterization") are repeated on larger networks, and their growth with m is fitted. The networks are (i) the random family of E2 (`arc_factor` 2, unit costs, k ∈ {1, 2} with k < κ, seed 0) with n ∈ {3, 4, 5, 6, 7, 8, 10, 12, 16, 20, 24, 32, 40}, which contains the nine instances of E2; and (ii) seed 0 of each of the ten (w, k) combinations of E1, read from the E1 output folder. The circuits are the Dicke preparation A_k, the arithmetic oracle over (x, α) with threshold F\* + 1, and, on the random family only, the truth-table oracle. Logical counts use the basis {cx, u}; transpiled counts use `FakeFez` at optimization level 1, seed 0, only for circuits with at most 156 qubits. The growth of the two-qubit gate count with m is fitted as a power law (least squares on log₁₀, 95% bootstrap interval with 2,000 resamples of instances, seed 0).
- **Control:** the nine instances of E2 must give the same counts as the folder of 2026-11-06 (all columns except compile time). If any differs, the extension is not used until the difference is explained.
- **When:** registered on 2026-11-26, before the run. Before registering, the build time of the arithmetic oracle was measured in a scratch run (not stored) on random instances with up to 40 nodes and on the four widths of E1, to choose sizes that run in minutes.
- **Reason:** the counts of 2026-11-06 stop at m = 14, which leaves the growth of the oracle with the size of the network undetermined. Requested in the review of the paper for submission.
- **Not covered:** the reversible maximum-flow oracle on which Proposition 1 relies is still not built, so it has no gate count. Counts of T or Toffoli gates are not reported, because the library adder used by the arithmetic oracle (`WeightedSumGate`) contains arbitrary-angle rotations and cannot be decomposed exactly into Clifford+T. The truth-table oracle is not counted on the E1 instances, because marking the optimal plans requires enumerating up to 974,121 plans and the oracle serves only the hardware demonstration.
- **Effect:** no change to the nine stored counts or to H4 and H5.
- **Outcome (added after the run, 2026-11-26):** the control passed (54 of 54 counts identical). The rule k < κ excluded the random instances with n ∈ {24, 32, 40}, where κ = 1, and the instance with n = 8 and k = 2, where κ = 2. The extension therefore has 25 instances, 15 random (n from 3 to 20, m from 3 to 40) and 10 from E1 (m from 8 to 70). The arithmetic oracles with m = 70 have 184 qubits and were not transpiled to `FakeFez`. Data in `outputs/2026-11-26_21-17-06__dicke-truth_table-arithmetic__random-layered__n3-27__runs1`.

### 8.5 Additional analyses of the stored data of E1 and E3
- **What:** analyses of data already recorded, with no new run. For E1, the distribution over the 6,000 runs of minimum finding of the cost to the optimum as a fraction of the budget Q of Proposition 1, and the success rate per instance at fractions of Q below one. For E3, for all eight circuits and the three environments (not only at the optimal number of iterations): the frequency of the optimal interdiction with a 95% Wilson interval; the fraction of shots inside F_1; the frequency of the optimum among the shots inside F_1 (post-selection, which the classical loop can apply at no cost because checking |x| ≤ k is free); and the total variation distance of the measured distribution to the theoretical one and to the one measured on `FakeFez`.
- **When:** defined on 2026-11-26, after all results were known.
- **Reason:** H4 checks the implementation and H5 has a weak baseline. These analyses describe the data in more detail. Requested in the review of the paper for submission.
- **Effect:** none on the verdicts of H4 and H5. The paper reports these analyses as exploratory. They are computed by notebook `05` from `runs/durr_hoyer__layered__n6-27__runs200.csv` of E1 and from `counts_*.csv` and `run_ibm.json` of E3.

# Resultados da entrega 2 (gerado pelo notebook `05_article_figures`)

Não editar à mão: reexecutar o notebook. Todo número citado no artigo sai desta lista.

## Experimentos de origem

- **E1:** `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200`
- **E2:** `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1`
- **E3:** `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096`
- **MILP (random):** `outputs/2026-11-02_19-08-14__milp__random__n10-5120__runs1`
- **MILP (layered):** `outputs/2026-11-02_19-14-18__milp__layered__n18-4098__runs1`

## Números

| Chave | Valor | Origem | Nota |
|---|---|---|---|
| `e1_acceptance_milp_certified` | 30/30 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/acceptance.json` |  |
| `e1_acceptance_enumeration_matches_milp` | 30/30 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/acceptance.json` |  |
| `e1_acceptance_non_degenerate` | 30/30 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/acceptance.json` |  |
| `e1_acceptance_found_runs_with_zero_gap` | 18000/18000 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/acceptance.json` |  |
| `h4_beta` | 0.4935152469840707 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/h4.json` |  |
| `h4_ci_low` | 0.46046066907623684 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/h4.json` |  |
| `h4_ci_high` | 0.5232358989480635 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/h4.json` |  |
| `h4_verdict` | not refuted | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/h4.json` |  |
| `e1_min_within_cost_budget_rate` | 1.0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_mean_within_cost_budget_rate` | 1.0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_max_mean_cost_over_budget` | 0.10116919647053015 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_min_within_budget_rate` | 1.0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_mean_within_budget_rate` | 1.0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_instances_below_one_half` | 0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_max_mean_queries_over_budget` | 0.09451444483562954 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/query_budget_summary.json` |  |
| `e1_instances` | 30 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `e1_N_min` | 9 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `e1_N_max` | 974121 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `e1_M_max` | 4 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `beta_durr_hoyer_vs_N` | 0.4935 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t2_scaling_fits.csv` | CI [0.4605, 0.5232], R2 0.9765 |
| `beta_random_order_vs_N` | 0.975 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t2_scaling_fits.csv` | CI [0.9401, 1.0063], R2 0.9928 |
| `beta_durr_hoyer_vs_N_over_M` | 0.5101 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t2_scaling_fits.csv` | CI [0.4971, 0.5293], R2 0.9951 |
| `beta_random_order_vs_N_over_M` | 1.0008 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t2_scaling_fits.csv` | CI [0.9838, 1.0222], R2 0.9978 |
| `dh_cost_over_sqrtN_min` | 0.902 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` |  |
| `dh_cost_over_sqrtN_max` | 2.666 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` |  |
| `largest_N_mean_cost_durr_hoyer` | 1750.1 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` | mean over the 3 seeds with the largest N |
| `largest_N_mean_cost_random_order` | 383686.8 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` | mean over the 3 seeds with the largest N |
| `largest_N_mean_cost_enumeration` | 974121.0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` | mean over the 3 seeds with the largest N |
| `random_order_over_theory_mean` | 0.99 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/per_instance.csv` |  |
| `milp_time_max_ms_e1` | 23.9 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `enumeration_time_max_s_e1` | 568.2 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/t1_instances.csv` |  |
| `milp_nstar_random_0.25` | 320 | `outputs/2026-11-02_19-08-14__milp__random__n10-5120__runs1/frontier.json` | reached_largest=False |
| `milp_nstar_random_0.5` | 2560 | `outputs/2026-11-02_19-08-14__milp__random__n10-5120__runs1/frontier.json` | reached_largest=False |
| `milp_nstar_random_0.75` | 2560 | `outputs/2026-11-02_19-08-14__milp__random__n10-5120__runs1/frontier.json` | reached_largest=False |
| `milp_nstar_layered_0.25` | 2306 | `outputs/2026-11-02_19-14-18__milp__layered__n18-4098__runs1/frontier.json` | reached_largest=False |
| `milp_nstar_layered_0.5` | 4098 | `outputs/2026-11-02_19-14-18__milp__layered__n18-4098__runs1/frontier.json` | reached_largest=True |
| `milp_nstar_layered_0.75` | 4098 | `outputs/2026-11-02_19-14-18__milp__layered__n18-4098__runs1/frontier.json` | reached_largest=True |
| `f1_instance` | layered-n11-m24-B2-s0 | `outputs/2026-11-06_09-39-40__durr_hoyer-random_order-enumeration__layered__n6-27__runs200/instances/layered-n11-m24-B2-s0.json` | F0=19, F*=4, N=301, M=1 |
| `t0_feasible_below_sqrt` | 13/15 | `paper/tables/t0_feasible_vs_hypercube.csv` |  |
| `t0_above_sqrt_cases` | m=12: 67 > 64; m=12: 138 > 64 | `paper/tables/t0_feasible_vs_hypercube.csv` |  |
| `t0_min_m_all_below` | 15 | `paper/tables/t0_feasible_vs_hypercube.csv` | every instance with at least this m has fewer feasible plans than sqrt(2^m) |
| `t0_max_feasible_m25` | 374 | `paper/tables/t0_feasible_vs_hypercube.csv` | sqrt(2^m) = 5793 |
| `t0_non_degenerate` | 15/15 | `paper/tables/t0_feasible_vs_hypercube.csv` |  |
| `t0_largest_m` | m=25, feasible=49, sqrt=5793 | `paper/tables/t0_feasible_vs_hypercube.csv` |  |
| `e2_m_range` | 3-14 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/resources.csv` |  |
| `e2_arith_qubits_range` | 18-46 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/resources.csv` |  |
| `e2_arith_2q_logical_range` | 690-4202 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/resources.csv` |  |
| `e2_arith_2q_fake_range` | 2055-14296 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/resources.csv` |  |
| `e2_dicke_2q_logical_range` | 8-174 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/resources.csv` |  |
| `e2_x_alpha_beats_enumeration` | 7/9 | `outputs/2026-11-06_09-52-56__dicke-truth_table-arithmetic__random__n3-7__runs1/t3_analytic.csv` |  |
| `e3_ideal simulator_interface_j0_frequency` | 0.2534 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=3.12e-01 |
| `e3_noisy simulator (FakeFez)_interface_j0_frequency` | 0.2405 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=9.23e-01 |
| `e3_IBM hardware_interface_j0_frequency` | 0.2227 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=1.00e+00 |
| `e3_ideal simulator_interface_j1_frequency` | 1.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 1.0000, p=0.00e+00 |
| `e3_noisy simulator (FakeFez)_interface_j1_frequency` | 0.8979 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 1.0000, p=0.00e+00 |
| `e3_IBM hardware_interface_j1_frequency` | 0.8152 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 1.0000, p=0.00e+00 |
| `e3_ideal simulator_interface_j2_frequency` | 0.2473 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=6.60e-01 |
| `e3_noisy simulator (FakeFez)_interface_j2_frequency` | 0.2297 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=9.99e-01 |
| `e3_IBM hardware_interface_j2_frequency` | 0.2146 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=1.00e+00 |
| `e3_ideal simulator_interface_j3_frequency` | 0.2593 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=8.84e-02 |
| `e3_noisy simulator (FakeFez)_interface_j3_frequency` | 0.2151 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=1.00e+00 |
| `e3_IBM hardware_interface_j3_frequency` | 0.2329 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.2500, p=9.95e-01 |
| `e3_ideal simulator_hypercube_j0_frequency` | 0.125 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.1250, p=5.07e-01 |
| `e3_noisy simulator (FakeFez)_hypercube_j0_frequency` | 0.1292 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.1250, p=2.17e-01 |
| `e3_IBM hardware_hypercube_j0_frequency` | 0.1235 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.1250, p=6.19e-01 |
| `e3_ideal simulator_hypercube_j1_frequency` | 0.7834 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.7813, p=0.00e+00 |
| `e3_noisy simulator (FakeFez)_hypercube_j1_frequency` | 0.7429 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.7813, p=0.00e+00 |
| `e3_IBM hardware_hypercube_j1_frequency` | 0.6472 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.7813, p=0.00e+00 |
| `e3_ideal simulator_hypercube_j2_frequency` | 0.9424 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.9453, p=0.00e+00 |
| `e3_noisy simulator (FakeFez)_hypercube_j2_frequency` | 0.8335 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.9453, p=0.00e+00 |
| `e3_IBM hardware_hypercube_j2_frequency` | 0.8176 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.9453, p=0.00e+00 |
| `e3_ideal simulator_hypercube_j3_frequency` | 0.3423 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.3301, p=7.76e-282 |
| `e3_noisy simulator (FakeFez)_hypercube_j3_frequency` | 0.3032 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.3301, p=4.17e-198 |
| `e3_IBM hardware_hypercube_j3_frequency` | 0.2729 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | theory 0.3301, p=5.24e-142 |
| `h5_verdict` | not refuted | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/h5.json` |  |
| `e3_ideal simulator_interface_j0_feasible_frequency` | 1.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_noisy simulator (FakeFez)_interface_j0_feasible_frequency` | 0.9915 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_IBM hardware_interface_j0_feasible_frequency` | 0.9832 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_ideal simulator_interface_j1_feasible_frequency` | 1.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_noisy simulator (FakeFez)_interface_j1_feasible_frequency` | 0.9504 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_IBM hardware_interface_j1_feasible_frequency` | 0.9175 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_ideal simulator_interface_j2_feasible_frequency` | 1.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_noisy simulator (FakeFez)_interface_j2_feasible_frequency` | 0.9194 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_IBM hardware_interface_j2_feasible_frequency` | 0.908 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_ideal simulator_interface_j3_feasible_frequency` | 1.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_noisy simulator (FakeFez)_interface_j3_feasible_frequency` | 0.8943 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_IBM hardware_interface_j3_feasible_frequency` | 0.8801 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | fraction of shots inside F_1 |
| `e3_instance` | random-n3-m3-B1-s0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/manifest.json` | optimum 010 |
| `e3_ibm_backend` | ibm_fez | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/t4_hardware.csv` | job dbmujid8mdtc73d8m2h0, finished 2026-11-06T12:34:25-03:00 |
| `e3_ibm_qpu_seconds` | 11.0 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/t4_hardware.csv` | qpu_charge_time_seconds reported by IBM for the whole job |
| `e3_ibm_queue_minutes` | 41.2 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/t4_hardware.csv` | from creation to start of execution |
| `e3_ibm_total_minutes` | 41.5 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/t4_hardware.csv` | from creation to finish |
| `e3_exploratory_interface_ratio_to_theory` | 0.8152 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_interface_wilson_low` | 0.803 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_interface_wilson_high` | 0.8268 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_interface_difference_to_fake_fez` | -0.0828 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_interface_fisher_p` | 8.31e-27 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | two-sided Fisher exact test, hardware vs FakeFez; defined after the hardware run |
| `e3_exploratory_hypercube_ratio_to_theory` | 0.8649 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_hypercube_wilson_low` | 0.8055 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_hypercube_wilson_high` | 0.8292 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_hypercube_difference_to_fake_fez` | -0.0159 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | defined after the hardware run |
| `e3_exploratory_hypercube_fisher_p` | 6.24e-02 | `outputs/2026-11-06_09-51-19__grover_ideal-grover_fake_fez-grover_ibm__random__n3-3__runs4096/amplification.csv` | two-sided Fisher exact test, hardware vs FakeFez; defined after the hardware run |

# Benchmark 5 — Statistical Report
**Date:** 2026-04-22  
**SEED:** 2024  N_MC = 200  T = 30  γ = 0.97  
**Block bootstrap:** block_size = 10, B = 5000  
**Effective sample size:** ESS = 600  
**Multiple comparison:** Holm–Bonferroni, α = 0.05  

---

## Table 1 — Discounted Cumulative Reward (U_cum)

Mean ± SD with 95 % bootstrap CI. Regret = U_cum(MyopicEU) − U_cum(method).

### Condition: stationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 456.1 | 398.3 | [416.2, 499.5] | 460.1 | 429.3 |
| ELS_Pres | 342.2 | 519.3 | [266.2, 417.4] | 480.3 | 543.2 |
| ELS_Int | 361.1 | 492.1 | [300.8, 420.4] | 466.4 | 524.3 |
| SARSOP | 832.6 | 235.5 | [792.9, 876.5] | 821.0 | 52.8 |
| PBVI | 828.9 | 252.6 | [800.4, 856.4] | 825.3 | 56.5 |
| SDP_S | 905.1 | 223.8 | [875.6, 935.1] | 887.0 | -19.7 |
| SDP_NS | 934.7 | 230.3 | [907.9, 965.2] | 911.5 | -49.3 |
| MPC | 914.2 | 213.9 | [886.0, 945.0] | 883.0 | -28.8 |
| RDM | 922.7 | 214.6 | [890.0, 954.0] | 913.9 | -37.3 |
| InfoGap | 911.7 | 240.5 | [883.6, 943.8] | 876.6 | -26.3 |
| AlwaysRestricted | -203.7 | 623.3 | [-269.8, -141.1] | -146.0 | 1089.1 |
| MyopicEU | 885.4 | 232.8 | [860.0, 912.3] | 860.0 | — |
| SARSOP_Misspec | 761.0 | 281.6 | [730.1, 793.0] | 776.2 | 124.4 |
| SDP_S_Misspec | 884.6 | 236.1 | [850.7, 920.0] | 878.2 | 0.8 |
| ELS_Phil_T | 888.8 | 258.2 | [852.3, 923.4] | 866.5 | -3.4 |
| ELS_Int_T | 893.7 | 220.3 | [870.6, 917.4] | 884.8 | -8.3 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 463.1 | 413.8 | [391.9, 534.9] | 491.5 | 448.9 |
| ELS_Pres | 387.1 | 470.7 | [317.6, 450.1] | 481.0 | 525.0 |
| ELS_Int | 295.6 | 448.3 | [229.1, 358.6] | 336.8 | 616.5 |
| SARSOP | 881.7 | 250.6 | [855.6, 906.4] | 880.4 | 30.3 |
| PBVI | 877.3 | 258.6 | [841.2, 912.1] | 866.2 | 34.8 |
| SDP_S | 931.9 | 220.4 | [901.1, 959.9] | 942.1 | -19.8 |
| SDP_NS | 933.1 | 223.7 | [910.9, 955.0] | 915.5 | -21.0 |
| MPC | 892.7 | 238.3 | [864.2, 917.2] | 886.1 | 19.4 |
| RDM | 981.2 | 241.5 | [954.2, 1008.8] | 961.3 | -69.2 |
| InfoGap | 930.3 | 227.8 | [904.8, 956.1] | 905.9 | -18.3 |
| AlwaysRestricted | -359.5 | 643.9 | [-453.0, -269.6] | -316.5 | 1271.6 |
| MyopicEU | 912.0 | 236.9 | [884.9, 938.4] | 920.6 | — |
| SARSOP_Misspec | 768.5 | 266.3 | [742.7, 795.0] | 763.2 | 143.5 |
| SDP_S_Misspec | 910.5 | 227.7 | [873.3, 945.1] | 894.3 | 1.6 |
| ELS_Phil_T | 936.8 | 255.3 | [899.5, 978.9] | 949.5 | -24.8 |
| ELS_Int_T | 878.4 | 235.4 | [844.5, 913.5] | 871.2 | 33.6 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.925 | [0.890, 0.955] | 9.5 | 8.0 |
| ELS_Pres | 0.955 | [0.925, 0.980] | 8.0 | 7.0 |
| ELS_Int | 0.945 | [0.915, 0.975] | 9.2 | 8.0 |
| SARSOP | 0.890 | [0.855, 0.925] | 9.9 | 9.0 |
| PBVI | 0.870 | [0.840, 0.900] | 8.4 | 6.5 |
| SDP_S | 0.835 | [0.785, 0.885] | 10.9 | 10.0 |
| SDP_NS | 0.820 | [0.765, 0.870] | 9.5 | 8.0 |
| MPC | 0.805 | [0.740, 0.865] | 9.9 | 8.0 |
| RDM | 0.825 | [0.775, 0.875] | 10.0 | 9.0 |
| InfoGap | 0.845 | [0.790, 0.900] | 9.1 | 8.0 |
| AlwaysRestricted | 0.960 | [0.940, 0.980] | 8.5 | 6.0 |
| MyopicEU | 0.810 | [0.750, 0.865] | 9.1 | 7.0 |
| SARSOP_Misspec | 0.925 | [0.885, 0.960] | 9.1 | 8.0 |
| SDP_S_Misspec | 0.880 | [0.835, 0.925] | 9.4 | 8.0 |
| ELS_Phil_T | 0.905 | [0.860, 0.945] | 10.1 | 8.0 |
| ELS_Int_T | 0.865 | [0.825, 0.900] | 8.3 | 6.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.965 | [0.940, 0.990] | 10.1 | 9.0 |
| ELS_Pres | 0.950 | [0.925, 0.975] | 8.9 | 8.0 |
| ELS_Int | 0.965 | [0.940, 0.990] | 8.8 | 8.0 |
| SARSOP | 0.930 | [0.890, 0.965] | 9.4 | 8.5 |
| PBVI | 0.940 | [0.900, 0.970] | 9.4 | 7.5 |
| SDP_S | 0.910 | [0.865, 0.955] | 9.8 | 8.0 |
| SDP_NS | 0.880 | [0.835, 0.920] | 11.5 | 12.0 |
| MPC | 0.910 | [0.880, 0.940] | 10.5 | 9.0 |
| RDM | 0.915 | [0.885, 0.945] | 9.0 | 8.0 |
| InfoGap | 0.900 | [0.870, 0.930] | 10.3 | 9.0 |
| AlwaysRestricted | 0.980 | [0.960, 0.995] | 8.0 | 6.0 |
| MyopicEU | 0.925 | [0.895, 0.955] | 10.9 | 10.0 |
| SARSOP_Misspec | 0.965 | [0.935, 0.990] | 9.6 | 8.0 |
| SDP_S_Misspec | 0.910 | [0.875, 0.940] | 10.7 | 10.0 |
| ELS_Phil_T | 0.920 | [0.875, 0.960] | 9.9 | 8.0 |
| ELS_Int_T | 0.900 | [0.860, 0.935] | 11.2 | 10.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 1637.000 | 0.0000 | 0.0000 | ✓ | -1.222 |
| PBVI | wilcoxon_sr | 2021.000 | 0.0000 | 0.0000 | ✓ | -1.196 |
| SDP_S | wilcoxon_sr | 1138.000 | 0.0000 | 0.0000 | ✓ | -1.423 |
| SDP_NS | wilcoxon_sr | 1029.000 | 0.0000 | 0.0000 | ✓ | -1.493 |
| MPC | wilcoxon_sr | 1191.000 | 0.0000 | 0.0000 | ✓ | -1.458 |
| RDM | wilcoxon_sr | 1023.000 | 0.0000 | 0.0000 | ✓ | -1.479 |
| InfoGap | wilcoxon_sr | 1188.000 | 0.0000 | 0.0000 | ✓ | -1.422 |
| AlwaysRestricted | paired_t | 10.075 | 0.0000 | 0.0000 | ✓ | 1.006 |
| MyopicEU | wilcoxon_sr | 1181.000 | 0.0000 | 0.0000 | ✓ | -1.362 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -16.476 | 0.0000 | 0.0000 | ✓ | -1.614 |
| PBVI | paired_t | -15.546 | 0.0000 | 0.0000 | ✓ | -1.589 |
| SDP_S | paired_t | -18.120 | 0.0000 | 0.0000 | ✓ | -1.801 |
| SDP_NS | wilcoxon_sr | 483.000 | 0.0000 | 0.0000 | ✓ | -1.799 |
| MPC | paired_t | -16.649 | 0.0000 | 0.0000 | ✓ | -1.663 |
| RDM | paired_t | -19.592 | 0.0000 | 0.0000 | ✓ | -1.904 |
| InfoGap | paired_t | -17.671 | 0.0000 | 0.0000 | ✓ | -1.785 |
| AlwaysRestricted | paired_t | 12.139 | 0.0000 | 0.0000 | ✓ | 1.181 |
| MyopicEU | paired_t | -16.688 | 0.0000 | 0.0000 | ✓ | -1.719 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 297.5 | 158.6 | 138.9 | 371.0 | 5.296 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 336.7 | 126.4 | 210.4 | 436.7 | 6.813 | 0.0000 | ✓ |
| ELS_Pres | stationary | 213.5 | 128.8 | 84.7 | 542.3 | 2.209 | 0.0283 | ✓ |
| ELS_Pres | nonstationary | 266.9 | 120.2 | 146.8 | 460.2 | 4.510 | 0.0000 | ✓ |
| ELS_Int | stationary | 256.5 | 104.5 | 152.0 | 507.2 | 4.238 | 0.0000 | ✓ |
| ELS_Int | nonstationary | 199.6 | 95.9 | 103.7 | 511.8 | 2.866 | 0.0046 | ✓ |
| SARSOP | stationary | 488.6 | 344.0 | 144.5 | 234.9 | 8.704 | 0.0000 | ✓ |
| SARSOP | nonstationary | 514.6 | 367.1 | 147.5 | 239.4 | 8.709 | 0.0000 | ✓ |
| PBVI | stationary | 482.9 | 346.0 | 137.0 | 239.9 | 8.073 | 0.0000 | ✓ |
| PBVI | nonstationary | 516.1 | 361.2 | 154.9 | 246.6 | 8.882 | 0.0000 | ✓ |
| SDP_S | stationary | 539.0 | 366.1 | 172.8 | 216.4 | 11.293 | 0.0000 | ✓ |
| SDP_S | nonstationary | 549.0 | 382.9 | 166.1 | 210.5 | 11.157 | 0.0000 | ✓ |
| SDP_NS | stationary | 548.6 | 386.1 | 162.5 | 218.3 | 10.526 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 545.8 | 387.3 | 158.5 | 221.6 | 10.115 | 0.0000 | ✓ |
| MPC | stationary | 535.1 | 379.1 | 156.0 | 212.0 | 10.411 | 0.0000 | ✓ |
| MPC | nonstationary | 511.3 | 381.3 | 130.0 | 203.5 | 9.037 | 0.0000 | ✓ |
| RDM | stationary | 550.4 | 372.3 | 178.2 | 215.1 | 11.715 | 0.0000 | ✓ |
| RDM | nonstationary | 576.5 | 404.7 | 171.9 | 243.2 | 9.994 | 0.0000 | ✓ |
| InfoGap | stationary | 542.1 | 369.5 | 172.6 | 235.3 | 10.377 | 0.0000 | ✓ |
| InfoGap | nonstationary | 536.6 | 393.7 | 143.0 | 235.9 | 8.573 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | -71.9 | -131.7 | 59.8 | 523.4 | 1.616 | 0.1077 | – |
| AlwaysRestricted | nonstationary | -87.0 | -272.5 | 185.5 | 574.6 | 4.566 | 0.0000 | ✓ |
| MyopicEU | stationary | 535.3 | 350.1 | 185.1 | 211.2 | 12.397 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 528.7 | 383.3 | 145.4 | 217.3 | 9.458 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 464.9 | 296.1 | 168.8 | 304.1 | 7.848 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 465.8 | 302.8 | 163.0 | 252.8 | 9.119 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 533.9 | 350.7 | 183.1 | 244.6 | 10.588 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 536.5 | 374.0 | 162.5 | 217.7 | 10.559 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 530.2 | 358.6 | 171.5 | 241.0 | 10.065 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 566.3 | 370.6 | 195.7 | 261.5 | 10.583 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 538.7 | 355.0 | 183.7 | 251.4 | 10.333 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 499.2 | 379.2 | 120.0 | 234.5 | 7.239 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | 29.57 | 315.22 | [-6.81, 63.18] |
| nonstationary | 1.21 | 301.63 | [-35.95, 38.90] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.3103 | 0.1108 | [0.2958, 0.3250] |
| nonstationary | 0.3102 | 0.1064 | [0.2947, 0.3263] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 47.40 | 39.17 | 31.56 | 28.17 | 0.7 % | ✓ |
| ELS_Phil | nonstationary | 57.29 | 43.15 | 33.39 | 29.26 | 0.9 % | ✓ |
| ELS_Pres | stationary | 69.30 | 50.82 | 41.33 | 36.72 | 1.3 % | ✗ |
| ELS_Pres | nonstationary | 67.44 | 50.22 | 39.80 | 33.28 | 1.7 % | ✗ |
| ELS_Int | stationary | 65.40 | 50.87 | 40.94 | 34.80 | 1.7 % | ✗ |
| ELS_Int | nonstationary | 65.20 | 43.29 | 35.79 | 31.70 | 1.4 % | ✗ |
| SARSOP | stationary | 32.23 | 23.83 | 18.88 | 16.65 | 0.3 % | ✓ |
| SARSOP | nonstationary | 34.43 | 24.09 | 19.70 | 17.72 | 0.2 % | ✓ |
| PBVI | stationary | 36.67 | 26.06 | 20.80 | 17.86 | 0.4 % | ✓ |
| PBVI | nonstationary | 37.88 | 26.17 | 21.24 | 18.29 | 0.3 % | ✓ |
| SDP_S | stationary | 33.57 | 21.14 | 17.76 | 15.82 | 0.2 % | ✓ |
| SDP_S | nonstationary | 34.15 | 22.87 | 19.10 | 15.59 | 0.4 % | ✓ |
| SDP_NS | stationary | 33.28 | 23.51 | 19.14 | 16.29 | 0.3 % | ✓ |
| SDP_NS | nonstationary | 31.84 | 21.82 | 18.22 | 15.82 | 0.3 % | ✓ |
| MPC | stationary | 28.31 | 20.90 | 17.13 | 15.13 | 0.2 % | ✓ |
| MPC | nonstationary | 28.44 | 20.76 | 19.63 | 16.85 | 0.3 % | ✓ |
| RDM | stationary | 28.71 | 22.59 | 17.53 | 15.17 | 0.3 % | ✓ |
| RDM | nonstationary | 32.55 | 24.34 | 19.14 | 17.08 | 0.2 % | ✓ |
| InfoGap | stationary | 31.44 | 23.50 | 19.26 | 17.00 | 0.2 % | ✓ |
| InfoGap | nonstationary | 33.50 | 23.62 | 18.66 | 16.11 | 0.3 % | ✓ |
| AlwaysRestricted | stationary | 91.49 | 65.83 | 52.11 | 44.07 | 3.9 % | ✗ |
| AlwaysRestricted | nonstationary | 107.84 | 66.35 | 53.76 | 45.53 | 2.3 % | ✗ |
| MyopicEU | stationary | 29.90 | 23.03 | 18.73 | 16.46 | 0.3 % | ✓ |
| MyopicEU | nonstationary | 33.82 | 25.10 | 20.06 | 16.75 | 0.4 % | ✓ |
| SARSOP_Misspec | stationary | 42.41 | 27.28 | 22.89 | 19.91 | 0.4 % | ✓ |
| SARSOP_Misspec | nonstationary | 39.69 | 23.89 | 21.98 | 18.83 | 0.4 % | ✓ |
| SDP_S_Misspec | stationary | 34.66 | 23.34 | 19.45 | 16.70 | 0.3 % | ✓ |
| SDP_S_Misspec | nonstationary | 29.41 | 20.15 | 18.67 | 16.10 | 0.3 % | ✓ |
| ELS_Phil_T | stationary | 33.04 | 23.45 | 21.41 | 18.26 | 0.4 % | ✓ |
| ELS_Phil_T | nonstationary | 33.60 | 23.74 | 20.04 | 18.05 | 0.2 % | ✓ |
| ELS_Int_T | stationary | 28.03 | 20.30 | 18.00 | 15.58 | 0.3 % | ✓ |
| ELS_Int_T | nonstationary | 27.29 | 22.44 | 18.59 | 16.65 | 0.2 % | ✓ |

---

## Notes

- **Convergence:** 26/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


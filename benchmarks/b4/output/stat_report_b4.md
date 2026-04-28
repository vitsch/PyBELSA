# Benchmark 4 — Statistical Report
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
| ELS_Phil | 421.3 | 424.0 | [354.0, 490.4] | 433.8 | 618.1 |
| ELS_Pres | 400.2 | 613.3 | [327.6, 470.4] | 490.1 | 639.2 |
| ELS_Int | 368.3 | 504.0 | [307.1, 424.6] | 402.1 | 671.1 |
| SARSOP | 1009.1 | 220.0 | [977.3, 1041.7] | 1012.5 | 30.3 |
| PBVI | 994.4 | 205.8 | [968.0, 1021.6] | 1010.2 | 45.0 |
| SDP_S | 1057.3 | 174.9 | [1043.8, 1072.0] | 1050.3 | -17.8 |
| SDP_NS | 1027.5 | 177.5 | [1005.1, 1049.9] | 1038.8 | 11.9 |
| MPC | 1044.7 | 169.5 | [1026.0, 1065.4] | 1053.8 | -5.3 |
| RDM | 1044.4 | 159.0 | [1025.8, 1062.3] | 1035.4 | -5.0 |
| InfoGap | 1032.2 | 155.6 | [1011.9, 1053.1] | 1040.1 | 7.2 |
| AlwaysRestricted | 600.2 | 365.6 | [555.4, 645.2] | 606.7 | 439.2 |
| MyopicEU | 1039.4 | 171.7 | [1023.7, 1056.8] | 1059.6 | — |
| SARSOP_Misspec | 980.2 | 207.5 | [949.5, 1010.8] | 964.1 | 59.2 |
| SDP_S_Misspec | 1008.1 | 178.2 | [979.8, 1036.4] | 1018.6 | 31.3 |
| ELS_Phil_T | 964.2 | 212.4 | [931.9, 996.1] | 979.4 | 75.2 |
| ELS_Int_T | 961.1 | 223.7 | [929.5, 991.6] | 978.7 | 78.3 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 373.3 | 437.8 | [303.7, 440.1] | 418.6 | 647.2 |
| ELS_Pres | 376.8 | 541.4 | [288.8, 460.8] | 469.4 | 643.7 |
| ELS_Int | 337.4 | 472.3 | [272.4, 399.1] | 317.3 | 683.1 |
| SARSOP | 966.2 | 203.0 | [940.4, 989.6] | 956.9 | 54.3 |
| PBVI | 958.9 | 183.8 | [933.4, 986.5] | 973.7 | 61.6 |
| SDP_S | 1021.4 | 184.8 | [994.4, 1049.0] | 1045.1 | -0.9 |
| SDP_NS | 1030.4 | 143.5 | [1008.0, 1052.2] | 1035.1 | -9.8 |
| MPC | 996.8 | 182.1 | [973.4, 1018.5] | 1018.3 | 23.8 |
| RDM | 1018.7 | 176.3 | [995.0, 1041.8] | 1035.0 | 1.8 |
| InfoGap | 1024.1 | 167.6 | [1002.3, 1045.0] | 1031.6 | -3.6 |
| AlwaysRestricted | 531.2 | 406.1 | [468.1, 588.5] | 605.4 | 489.4 |
| MyopicEU | 1020.5 | 164.5 | [996.5, 1044.1] | 1037.6 | — |
| SARSOP_Misspec | 945.3 | 185.5 | [916.7, 969.3] | 950.8 | 75.2 |
| SDP_S_Misspec | 1006.9 | 160.2 | [989.5, 1025.2] | 1018.3 | 13.6 |
| ELS_Phil_T | 959.3 | 195.6 | [936.9, 982.0] | 950.9 | 61.2 |
| ELS_Int_T | 942.7 | 222.0 | [918.0, 969.5] | 948.1 | 77.8 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.795 | [0.735, 0.850] | 12.1 | 12.0 |
| ELS_Pres | 0.840 | [0.790, 0.885] | 8.3 | 7.0 |
| ELS_Int | 0.875 | [0.830, 0.915] | 9.6 | 9.0 |
| SARSOP | 0.485 | [0.425, 0.545] | 10.2 | 9.0 |
| PBVI | 0.545 | [0.480, 0.610] | 9.3 | 7.0 |
| SDP_S | 0.605 | [0.545, 0.665] | 10.5 | 9.0 |
| SDP_NS | 0.650 | [0.585, 0.715] | 10.0 | 8.0 |
| MPC | 0.655 | [0.600, 0.705] | 9.8 | 8.0 |
| RDM | 0.540 | [0.470, 0.610] | 9.4 | 9.0 |
| InfoGap | 0.540 | [0.485, 0.595] | 8.0 | 5.0 |
| AlwaysRestricted | 0.650 | [0.600, 0.700] | 9.8 | 7.0 |
| MyopicEU | 0.590 | [0.515, 0.665] | 7.7 | 5.0 |
| SARSOP_Misspec | 0.515 | [0.450, 0.580] | 7.7 | 4.0 |
| SDP_S_Misspec | 0.495 | [0.435, 0.555] | 9.8 | 6.0 |
| ELS_Phil_T | 0.585 | [0.520, 0.650] | 9.5 | 8.0 |
| ELS_Int_T | 0.645 | [0.590, 0.700] | 8.7 | 7.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.915 | [0.875, 0.950] | 11.9 | 12.0 |
| ELS_Pres | 0.915 | [0.885, 0.945] | 10.1 | 8.0 |
| ELS_Int | 0.915 | [0.870, 0.955] | 11.0 | 10.0 |
| SARSOP | 0.680 | [0.620, 0.735] | 10.2 | 7.5 |
| PBVI | 0.695 | [0.650, 0.745] | 11.5 | 10.0 |
| SDP_S | 0.795 | [0.745, 0.845] | 11.7 | 11.0 |
| SDP_NS | 0.755 | [0.705, 0.815] | 12.7 | 14.0 |
| MPC | 0.810 | [0.765, 0.855] | 11.7 | 10.0 |
| RDM | 0.745 | [0.690, 0.800] | 10.0 | 8.0 |
| InfoGap | 0.620 | [0.555, 0.690] | 12.2 | 11.0 |
| AlwaysRestricted | 0.800 | [0.735, 0.865] | 11.2 | 10.0 |
| MyopicEU | 0.685 | [0.625, 0.740] | 11.4 | 8.0 |
| SARSOP_Misspec | 0.675 | [0.610, 0.735] | 12.4 | 15.0 |
| SDP_S_Misspec | 0.565 | [0.500, 0.620] | 10.5 | 9.0 |
| ELS_Phil_T | 0.740 | [0.665, 0.805] | 11.9 | 10.5 |
| ELS_Int_T | 0.745 | [0.680, 0.805] | 12.4 | 13.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -15.955 | 0.0000 | 0.0000 | ✓ | -1.648 |
| PBVI | paired_t | -16.043 | 0.0000 | 0.0000 | ✓ | -1.626 |
| SDP_S | wilcoxon_sr | 665.000 | 0.0000 | 0.0000 | ✓ | -1.826 |
| SDP_NS | wilcoxon_sr | 540.000 | 0.0000 | 0.0000 | ✓ | -1.745 |
| MPC | paired_t | -17.413 | 0.0000 | 0.0000 | ✓ | -1.799 |
| RDM | paired_t | -18.172 | 0.0000 | 0.0000 | ✓ | -1.809 |
| InfoGap | wilcoxon_sr | 876.000 | 0.0000 | 0.0000 | ✓ | -1.780 |
| AlwaysRestricted | paired_t | -5.058 | 0.0000 | 0.0000 | ✓ | -0.527 |
| MyopicEU | paired_t | -17.803 | 0.0000 | 0.0000 | ✓ | -1.782 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 807.000 | 0.0000 | 0.0000 | ✓ | -1.730 |
| PBVI | paired_t | -17.787 | 0.0000 | 0.0000 | ✓ | -1.734 |
| SDP_S | paired_t | -19.445 | 0.0000 | 0.0000 | ✓ | -1.907 |
| SDP_NS | paired_t | -19.967 | 0.0000 | 0.0000 | ✓ | -1.985 |
| MPC | paired_t | -18.475 | 0.0000 | 0.0000 | ✓ | -1.842 |
| RDM | paired_t | -18.680 | 0.0000 | 0.0000 | ✓ | -1.911 |
| InfoGap | wilcoxon_sr | 378.000 | 0.0000 | 0.0000 | ✓ | -1.938 |
| AlwaysRestricted | paired_t | -4.553 | 0.0000 | 0.0000 | ✓ | -0.440 |
| MyopicEU | paired_t | -19.421 | 0.0000 | 0.0000 | ✓ | -1.932 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 310.5 | 110.8 | 199.6 | 497.0 | 5.681 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 351.9 | 21.4 | 330.6 | 566.3 | 8.256 | 0.0000 | ✓ |
| ELS_Pres | stationary | 246.0 | 154.3 | 91.7 | 597.5 | 2.170 | 0.0312 | ✓ |
| ELS_Pres | nonstationary | 355.0 | 21.8 | 333.2 | 569.7 | 8.272 | 0.0000 | ✓ |
| ELS_Int | stationary | 279.9 | 88.4 | 191.4 | 571.4 | 4.738 | 0.0000 | ✓ |
| ELS_Int | nonstationary | 300.6 | 36.8 | 263.9 | 650.6 | 5.736 | 0.0000 | ✓ |
| SARSOP | stationary | 605.4 | 403.7 | 201.6 | 194.9 | 14.629 | 0.0000 | ✓ |
| SARSOP | nonstationary | 598.7 | 367.5 | 231.2 | 195.8 | 16.705 | 0.0000 | ✓ |
| PBVI | stationary | 592.7 | 401.8 | 190.9 | 199.1 | 13.559 | 0.0000 | ✓ |
| PBVI | nonstationary | 608.3 | 350.6 | 257.7 | 186.3 | 19.564 | 0.0000 | ✓ |
| SDP_S | stationary | 639.4 | 417.9 | 221.5 | 164.9 | 18.996 | 0.0000 | ✓ |
| SDP_S | nonstationary | 638.5 | 382.9 | 255.6 | 178.0 | 20.312 | 0.0000 | ✓ |
| SDP_NS | stationary | 625.2 | 402.3 | 223.0 | 172.9 | 18.234 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 650.1 | 380.2 | 269.9 | 159.2 | 23.966 | 0.0000 | ✓ |
| MPC | stationary | 623.0 | 421.7 | 201.3 | 165.8 | 17.168 | 0.0000 | ✓ |
| MPC | nonstationary | 614.5 | 382.3 | 232.2 | 175.5 | 18.712 | 0.0000 | ✓ |
| RDM | stationary | 635.5 | 408.9 | 226.5 | 161.3 | 19.856 | 0.0000 | ✓ |
| RDM | nonstationary | 629.1 | 389.6 | 239.5 | 166.2 | 20.384 | 0.0000 | ✓ |
| InfoGap | stationary | 616.1 | 416.1 | 200.0 | 173.1 | 16.335 | 0.0000 | ✓ |
| InfoGap | nonstationary | 627.9 | 396.2 | 231.7 | 158.5 | 20.681 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 391.5 | 208.8 | 182.7 | 339.9 | 7.600 | 0.0000 | ✓ |
| AlwaysRestricted | nonstationary | 342.1 | 189.0 | 153.1 | 399.5 | 5.419 | 0.0000 | ✓ |
| MyopicEU | stationary | 629.4 | 410.0 | 219.4 | 183.2 | 16.938 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 624.8 | 395.7 | 229.1 | 156.2 | 20.737 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 580.8 | 399.4 | 181.5 | 190.3 | 13.484 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 592.2 | 353.1 | 239.0 | 192.0 | 17.606 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 608.1 | 399.9 | 208.2 | 158.4 | 18.586 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 620.6 | 386.2 | 234.4 | 162.2 | 20.433 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 582.2 | 382.0 | 200.2 | 233.4 | 12.129 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 614.0 | 345.3 | 268.7 | 196.2 | 19.360 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 575.5 | 385.7 | 189.8 | 202.0 | 13.287 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 593.0 | 349.6 | 243.4 | 211.1 | 16.307 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | -29.75 | 258.73 | [-60.07, -1.46] |
| nonstationary | 8.94 | 224.56 | [-25.15, 44.41] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2762 | 0.0966 | [0.2665, 0.2862] |
| nonstationary | 0.2867 | 0.1049 | [0.2725, 0.3020] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 54.96 | 43.18 | 35.32 | 29.98 | 1.3 % | ✗ |
| ELS_Phil | nonstationary | 58.75 | 43.81 | 36.53 | 30.95 | 1.5 % | ✗ |
| ELS_Pres | stationary | 113.55 | 67.87 | 51.85 | 43.37 | 2.1 % | ✗ |
| ELS_Pres | nonstationary | 79.90 | 51.90 | 43.14 | 38.28 | 1.3 % | ✗ |
| ELS_Int | stationary | 70.63 | 52.20 | 42.57 | 35.64 | 1.9 % | ✗ |
| ELS_Int | nonstationary | 69.07 | 47.09 | 37.91 | 33.40 | 1.3 % | ✗ |
| SARSOP | stationary | 28.66 | 23.58 | 18.37 | 15.55 | 0.3 % | ✓ |
| SARSOP | nonstationary | 30.72 | 19.96 | 16.45 | 14.36 | 0.2 % | ✓ |
| PBVI | stationary | 25.32 | 19.80 | 16.54 | 14.55 | 0.2 % | ✓ |
| PBVI | nonstationary | 25.93 | 17.68 | 14.33 | 13.00 | 0.1 % | ✓ |
| SDP_S | stationary | 25.59 | 18.41 | 14.71 | 12.37 | 0.2 % | ✓ |
| SDP_S | nonstationary | 28.94 | 18.49 | 15.63 | 13.07 | 0.3 % | ✓ |
| SDP_NS | stationary | 24.45 | 17.62 | 14.69 | 12.55 | 0.2 % | ✓ |
| SDP_NS | nonstationary | 22.06 | 15.06 | 11.63 | 10.15 | 0.1 % | ✓ |
| MPC | stationary | 23.30 | 17.44 | 13.85 | 11.98 | 0.2 % | ✓ |
| MPC | nonstationary | 21.56 | 17.69 | 15.31 | 12.88 | 0.2 % | ✓ |
| RDM | stationary | 20.10 | 15.16 | 13.08 | 11.24 | 0.2 % | ✓ |
| RDM | nonstationary | 26.56 | 19.02 | 14.52 | 12.46 | 0.2 % | ✓ |
| InfoGap | stationary | 22.18 | 15.52 | 13.17 | 11.00 | 0.2 % | ✓ |
| InfoGap | nonstationary | 26.26 | 16.38 | 13.63 | 11.85 | 0.2 % | ✓ |
| AlwaysRestricted | stationary | 47.57 | 34.94 | 29.52 | 25.85 | 0.6 % | ✓ |
| AlwaysRestricted | nonstationary | 63.07 | 39.82 | 32.48 | 28.72 | 0.7 % | ✓ |
| MyopicEU | stationary | 25.97 | 18.66 | 14.38 | 12.14 | 0.2 % | ✓ |
| MyopicEU | nonstationary | 21.27 | 15.47 | 12.95 | 11.63 | 0.1 % | ✓ |
| SARSOP_Misspec | stationary | 27.79 | 19.33 | 16.15 | 14.67 | 0.2 % | ✓ |
| SARSOP_Misspec | nonstationary | 27.72 | 19.60 | 15.52 | 13.11 | 0.3 % | ✓ |
| SDP_S_Misspec | stationary | 25.61 | 18.43 | 14.21 | 12.60 | 0.2 % | ✓ |
| SDP_S_Misspec | nonstationary | 20.14 | 14.26 | 12.44 | 11.33 | 0.1 % | ✓ |
| ELS_Phil_T | stationary | 30.37 | 21.17 | 17.36 | 15.02 | 0.2 % | ✓ |
| ELS_Phil_T | nonstationary | 29.94 | 20.81 | 16.30 | 13.83 | 0.3 % | ✓ |
| ELS_Int_T | stationary | 31.13 | 23.87 | 18.29 | 15.82 | 0.3 % | ✓ |
| ELS_Int_T | nonstationary | 27.33 | 21.35 | 18.05 | 15.70 | 0.2 % | ✓ |

---

## Notes

- **Convergence:** 26/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


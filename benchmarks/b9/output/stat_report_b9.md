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
| ELS_Phil | 431.2 | 467.8 | [386.5, 477.0] | 465.8 | 611.5 |
| ELS_Pres | 248.1 | 896.4 | [107.2, 377.4] | 485.1 | 794.5 |
| ELS_Int | 277.8 | 711.6 | [178.6, 373.7] | 467.8 | 764.9 |
| SARSOP | 931.5 | 299.3 | [875.9, 991.2] | 938.8 | 111.2 |
| PBVI | 924.8 | 325.1 | [878.4, 971.0] | 911.4 | 117.9 |
| SDP_S | 1033.0 | 254.9 | [1002.8, 1063.5] | 985.3 | 9.6 |
| SDP_NS | 1063.2 | 257.3 | [1034.9, 1095.5] | 1015.7 | -20.6 |
| MPC | 1044.8 | 253.0 | [1013.3, 1079.9] | 1009.8 | -2.2 |
| RDM | 1041.1 | 248.0 | [1001.4, 1079.0] | 1029.3 | 1.6 |
| InfoGap | 1055.7 | 279.3 | [1016.2, 1095.1] | 1005.8 | -13.1 |
| AlwaysRestricted | -133.6 | 754.3 | [-230.3, -44.9] | -47.0 | 1176.2 |
| MyopicEU | 1042.6 | 277.3 | [1003.5, 1084.3] | 1010.7 | — |
| SARSOP_Misspec | 967.5 | 317.9 | [931.0, 1003.3] | 950.3 | 75.1 |
| SDP_S_Misspec | 1051.4 | 262.3 | [1027.6, 1079.7] | 1002.4 | -8.8 |
| ELS_Phil_T | 994.5 | 295.2 | [958.8, 1032.2] | 1000.1 | 48.1 |
| ELS_Int_T | 992.3 | 280.8 | [967.4, 1017.8] | 999.3 | 50.3 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 448.1 | 500.6 | [347.8, 542.1] | 513.2 | 592.9 |
| ELS_Pres | 326.5 | 554.1 | [232.4, 409.6] | 423.9 | 714.5 |
| ELS_Int | 212.2 | 643.0 | [132.8, 283.1] | 319.3 | 828.8 |
| SARSOP | 967.8 | 311.3 | [944.7, 990.3] | 966.7 | 73.2 |
| PBVI | 955.3 | 329.1 | [920.9, 989.7] | 956.1 | 85.6 |
| SDP_S | 1043.6 | 251.0 | [1011.8, 1077.6] | 1031.9 | -2.7 |
| SDP_NS | 1066.2 | 278.7 | [1030.1, 1101.4] | 1045.4 | -25.2 |
| MPC | 1053.9 | 257.7 | [1017.8, 1091.1] | 1039.9 | -12.9 |
| RDM | 1132.9 | 302.4 | [1090.2, 1178.0] | 1081.0 | -91.9 |
| InfoGap | 1035.1 | 258.7 | [1001.0, 1067.9] | 991.3 | 5.8 |
| AlwaysRestricted | -332.6 | 889.7 | [-446.5, -225.1] | -252.4 | 1373.5 |
| MyopicEU | 1041.0 | 277.0 | [1014.7, 1066.5] | 1016.2 | — |
| SARSOP_Misspec | 957.0 | 321.6 | [914.5, 996.6] | 959.6 | 83.9 |
| SDP_S_Misspec | 1072.7 | 253.8 | [1030.1, 1111.7] | 1070.1 | -31.8 |
| ELS_Phil_T | 1078.4 | 290.1 | [1033.7, 1127.9] | 1046.7 | -37.4 |
| ELS_Int_T | 989.2 | 290.5 | [957.4, 1019.8] | 993.9 | 51.8 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.915 | [0.880, 0.945] | 11.0 | 11.0 |
| ELS_Pres | 0.940 | [0.915, 0.965] | 8.1 | 7.0 |
| ELS_Int | 0.885 | [0.845, 0.925] | 9.8 | 9.0 |
| SARSOP | 0.805 | [0.770, 0.840] | 11.5 | 10.0 |
| PBVI | 0.780 | [0.745, 0.815] | 9.3 | 7.5 |
| SDP_S | 0.750 | [0.690, 0.805] | 11.8 | 11.5 |
| SDP_NS | 0.745 | [0.690, 0.800] | 10.0 | 9.0 |
| MPC | 0.740 | [0.665, 0.805] | 10.2 | 9.0 |
| RDM | 0.760 | [0.715, 0.805] | 10.5 | 10.0 |
| InfoGap | 0.765 | [0.725, 0.805] | 9.3 | 8.0 |
| AlwaysRestricted | 0.935 | [0.900, 0.965] | 9.3 | 7.0 |
| MyopicEU | 0.710 | [0.640, 0.770] | 9.1 | 8.0 |
| SARSOP_Misspec | 0.820 | [0.775, 0.870] | 9.8 | 9.0 |
| SDP_S_Misspec | 0.785 | [0.740, 0.835] | 10.2 | 9.0 |
| ELS_Phil_T | 0.815 | [0.775, 0.855] | 10.6 | 9.0 |
| ELS_Int_T | 0.815 | [0.770, 0.860] | 8.7 | 7.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.910 | [0.875, 0.945] | 10.6 | 9.0 |
| ELS_Pres | 0.955 | [0.935, 0.975] | 8.4 | 8.0 |
| ELS_Int | 0.925 | [0.880, 0.965] | 9.5 | 9.0 |
| SARSOP | 0.855 | [0.815, 0.895] | 10.3 | 9.0 |
| PBVI | 0.880 | [0.835, 0.925] | 9.7 | 8.5 |
| SDP_S | 0.845 | [0.785, 0.900] | 10.5 | 9.0 |
| SDP_NS | 0.815 | [0.775, 0.860] | 11.9 | 12.0 |
| MPC | 0.830 | [0.780, 0.880] | 11.0 | 10.0 |
| RDM | 0.830 | [0.790, 0.865] | 9.5 | 8.0 |
| InfoGap | 0.855 | [0.825, 0.885] | 11.4 | 10.0 |
| AlwaysRestricted | 0.950 | [0.925, 0.975] | 8.6 | 8.0 |
| MyopicEU | 0.840 | [0.790, 0.885] | 11.6 | 11.0 |
| SARSOP_Misspec | 0.895 | [0.850, 0.935] | 10.2 | 9.0 |
| SDP_S_Misspec | 0.815 | [0.760, 0.870] | 11.7 | 12.0 |
| ELS_Phil_T | 0.860 | [0.810, 0.910] | 10.4 | 8.5 |
| ELS_Int_T | 0.840 | [0.790, 0.890] | 11.8 | 10.5 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 1789.000 | 0.0000 | 0.0000 | ✓ | -1.198 |
| PBVI | wilcoxon_sr | 1860.000 | 0.0000 | 0.0000 | ✓ | -1.170 |
| SDP_S | wilcoxon_sr | 871.000 | 0.0000 | 0.0000 | ✓ | -1.413 |
| SDP_NS | wilcoxon_sr | 617.000 | 0.0000 | 0.0000 | ✓ | -1.468 |
| MPC | wilcoxon_sr | 917.000 | 0.0000 | 0.0000 | ✓ | -1.436 |
| RDM | wilcoxon_sr | 814.000 | 0.0000 | 0.0000 | ✓ | -1.433 |
| InfoGap | wilcoxon_sr | 836.000 | 0.0000 | 0.0000 | ✓ | -1.439 |
| AlwaysRestricted | paired_t | 5.658 | 0.0000 | 0.0000 | ✓ | 0.561 |
| MyopicEU | wilcoxon_sr | 988.000 | 0.0000 | 0.0000 | ✓ | -1.416 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 972.000 | 0.0000 | 0.0000 | ✓ | -1.496 |
| PBVI | wilcoxon_sr | 1054.000 | 0.0000 | 0.0000 | ✓ | -1.455 |
| SDP_S | wilcoxon_sr | 633.000 | 0.0000 | 0.0000 | ✓ | -1.703 |
| SDP_NS | wilcoxon_sr | 419.000 | 0.0000 | 0.0000 | ✓ | -1.723 |
| MPC | wilcoxon_sr | 470.000 | 0.0000 | 0.0000 | ✓ | -1.718 |
| RDM | wilcoxon_sr | 412.000 | 0.0000 | 0.0000 | ✓ | -1.832 |
| InfoGap | wilcoxon_sr | 532.000 | 0.0000 | 0.0000 | ✓ | -1.679 |
| AlwaysRestricted | wilcoxon_sr | 4753.000 | 0.0000 | 0.0000 | ✓ | 0.702 |
| MyopicEU | wilcoxon_sr | 584.000 | 0.0000 | 0.0000 | ✓ | -1.674 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 316.1 | 115.1 | 201.0 | 501.6 | 5.668 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 345.0 | 103.1 | 241.9 | 569.9 | 6.002 | 0.0000 | ✓ |
| ELS_Pres | stationary | 161.4 | 86.7 | 74.8 | 751.2 | 1.407 | 0.1609 | – |
| ELS_Pres | nonstationary | 257.9 | 68.6 | 189.3 | 566.7 | 4.724 | 0.0000 | ✓ |
| ELS_Int | stationary | 254.3 | 23.5 | 230.8 | 764.3 | 4.271 | 0.0000 | ✓ |
| ELS_Int | nonstationary | 164.4 | 47.8 | 116.5 | 727.1 | 2.267 | 0.0245 | ✓ |
| SARSOP | stationary | 559.4 | 372.1 | 187.3 | 290.1 | 9.127 | 0.0000 | ✓ |
| SARSOP | nonstationary | 569.9 | 397.9 | 172.1 | 300.9 | 8.086 | 0.0000 | ✓ |
| PBVI | stationary | 550.9 | 373.8 | 177.1 | 319.8 | 7.830 | 0.0000 | ✓ |
| PBVI | nonstationary | 584.2 | 371.2 | 213.0 | 340.7 | 8.841 | 0.0000 | ✓ |
| SDP_S | stationary | 615.9 | 417.1 | 198.7 | 231.6 | 12.137 | 0.0000 | ✓ |
| SDP_S | nonstationary | 632.8 | 410.8 | 222.0 | 249.2 | 12.597 | 0.0000 | ✓ |
| SDP_NS | stationary | 634.7 | 428.6 | 206.1 | 255.3 | 11.416 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 640.2 | 426.0 | 214.2 | 259.1 | 11.690 | 0.0000 | ✓ |
| MPC | stationary | 620.0 | 424.8 | 195.3 | 257.7 | 10.717 | 0.0000 | ✓ |
| MPC | nonstationary | 627.5 | 426.4 | 201.1 | 237.7 | 11.961 | 0.0000 | ✓ |
| RDM | stationary | 625.8 | 415.2 | 210.6 | 241.0 | 12.362 | 0.0000 | ✓ |
| RDM | nonstationary | 684.6 | 448.2 | 236.4 | 291.6 | 11.467 | 0.0000 | ✓ |
| InfoGap | stationary | 637.0 | 418.7 | 218.2 | 270.5 | 11.412 | 0.0000 | ✓ |
| InfoGap | nonstationary | 620.7 | 414.5 | 206.2 | 247.4 | 11.787 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | -27.7 | -105.9 | 78.3 | 692.4 | 1.598 | 0.1115 | – |
| AlwaysRestricted | nonstationary | -88.4 | -244.2 | 155.8 | 759.0 | 2.902 | 0.0041 | ✓ |
| MyopicEU | stationary | 637.4 | 405.2 | 232.2 | 255.3 | 12.862 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 612.5 | 428.5 | 184.0 | 239.2 | 10.880 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 583.9 | 383.6 | 200.3 | 300.5 | 9.423 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 568.7 | 388.4 | 180.3 | 300.3 | 8.491 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 636.1 | 415.3 | 220.8 | 262.4 | 11.899 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 642.9 | 429.9 | 213.0 | 230.8 | 13.055 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 592.3 | 402.2 | 190.0 | 289.2 | 9.293 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 663.7 | 414.7 | 248.9 | 298.8 | 11.783 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 604.2 | 388.1 | 216.0 | 293.5 | 10.408 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 576.4 | 412.7 | 163.7 | 303.6 | 7.627 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | 30.19 | 344.74 | [-8.36, 67.20] |
| nonstationary | 22.58 | 352.59 | [-30.52, 77.72] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2803 | 0.0967 | [0.2632, 0.2980] |
| nonstationary | 0.2733 | 0.1025 | [0.2553, 0.2907] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 54.34 | 47.07 | 39.23 | 33.08 | 1.4 % | ✗ |
| ELS_Phil | nonstationary | 61.38 | 47.09 | 39.74 | 35.40 | 1.0 % | ✓ |
| ELS_Pres | stationary | 188.41 | 107.59 | 80.38 | 63.39 | 6.9 % | ✗ |
| ELS_Pres | nonstationary | 72.37 | 55.72 | 45.00 | 39.18 | 1.8 % | ✗ |
| ELS_Int | stationary | 89.65 | 66.07 | 55.88 | 50.31 | 2.0 % | ✗ |
| ELS_Int | nonstationary | 106.69 | 63.86 | 51.69 | 45.47 | 2.9 % | ✗ |
| SARSOP | stationary | 41.44 | 31.81 | 25.09 | 21.16 | 0.4 % | ✓ |
| SARSOP | nonstationary | 41.06 | 27.18 | 24.56 | 22.01 | 0.3 % | ✓ |
| PBVI | stationary | 40.87 | 30.92 | 26.80 | 22.99 | 0.4 % | ✓ |
| PBVI | nonstationary | 40.50 | 30.47 | 26.55 | 23.27 | 0.3 % | ✓ |
| SDP_S | stationary | 35.56 | 23.20 | 19.28 | 18.02 | 0.1 % | ✓ |
| SDP_S | nonstationary | 41.33 | 26.56 | 21.20 | 17.75 | 0.3 % | ✓ |
| SDP_NS | stationary | 39.09 | 25.91 | 21.02 | 18.20 | 0.3 % | ✓ |
| SDP_NS | nonstationary | 41.30 | 26.91 | 23.10 | 19.70 | 0.3 % | ✓ |
| MPC | stationary | 36.74 | 24.60 | 18.58 | 17.89 | 0.1 % | ✓ |
| MPC | nonstationary | 28.98 | 20.40 | 21.25 | 18.22 | 0.3 % | ✓ |
| RDM | stationary | 30.68 | 25.86 | 20.44 | 17.54 | 0.3 % | ✓ |
| RDM | nonstationary | 45.15 | 31.98 | 24.42 | 21.38 | 0.3 % | ✓ |
| InfoGap | stationary | 39.10 | 28.37 | 22.73 | 19.75 | 0.3 % | ✓ |
| InfoGap | nonstationary | 35.37 | 26.09 | 21.27 | 18.30 | 0.3 % | ✓ |
| AlwaysRestricted | stationary | 115.98 | 82.22 | 64.35 | 53.34 | 8.2 % | ✗ |
| AlwaysRestricted | nonstationary | 152.87 | 94.76 | 74.90 | 62.91 | 3.6 % | ✗ |
| MyopicEU | stationary | 39.24 | 28.04 | 22.24 | 19.61 | 0.3 % | ✓ |
| MyopicEU | nonstationary | 38.11 | 28.16 | 23.17 | 19.58 | 0.3 % | ✓ |
| SARSOP_Misspec | stationary | 50.12 | 31.04 | 26.37 | 22.48 | 0.4 % | ✓ |
| SARSOP_Misspec | nonstationary | 45.38 | 28.91 | 26.24 | 22.74 | 0.4 % | ✓ |
| SDP_S_Misspec | stationary | 41.46 | 25.79 | 21.68 | 18.55 | 0.3 % | ✓ |
| SDP_S_Misspec | nonstationary | 28.38 | 22.14 | 20.09 | 17.95 | 0.2 % | ✓ |
| ELS_Phil_T | stationary | 35.04 | 26.48 | 24.15 | 20.88 | 0.3 % | ✓ |
| ELS_Phil_T | nonstationary | 36.87 | 27.37 | 22.39 | 20.52 | 0.2 % | ✓ |
| ELS_Int_T | stationary | 33.93 | 25.25 | 22.93 | 19.86 | 0.3 % | ✓ |
| ELS_Int_T | nonstationary | 28.88 | 27.37 | 22.02 | 20.54 | 0.1 % | ✓ |

---

## Notes

- **Convergence:** 25/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


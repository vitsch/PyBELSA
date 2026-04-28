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
| ELS_Phil | 141.7 | 860.6 | [52.9, 232.6] | 209.9 | 1209.7 |
| ELS_Pres | -19.1 | 1101.3 | [-149.0, 112.0] | 207.1 | 1370.5 |
| ELS_Int | 113.3 | 1142.6 | [-47.3, 259.4] | 227.2 | 1238.1 |
| SARSOP | 1217.1 | 344.7 | [1163.7, 1271.6] | 1202.9 | 134.3 |
| PBVI | 1244.4 | 366.5 | [1196.4, 1297.8] | 1229.4 | 107.0 |
| SDP_S | 1326.9 | 323.6 | [1279.4, 1373.5] | 1293.8 | 24.5 |
| SDP_NS | 1337.5 | 308.1 | [1305.9, 1370.3] | 1300.4 | 13.9 |
| MPC | 1294.5 | 322.0 | [1256.5, 1333.8] | 1267.8 | 56.9 |
| RDM | 1292.6 | 318.7 | [1259.5, 1324.5] | 1240.3 | 58.8 |
| InfoGap | 1115.7 | 387.0 | [1071.9, 1160.0] | 963.8 | 235.7 |
| AlwaysRestricted | -517.7 | 1462.4 | [-695.2, -329.8] | -131.2 | 1869.1 |
| MyopicEU | 1351.4 | 359.2 | [1300.3, 1412.0] | 1309.7 | — |
| SARSOP_Misspec | 1277.4 | 385.8 | [1219.2, 1338.0] | 1232.7 | 74.0 |
| SDP_S_Misspec | 1315.4 | 344.3 | [1266.3, 1374.4] | 1269.5 | 36.0 |
| ELS_Phil_T | 1304.2 | 345.9 | [1278.1, 1329.7] | 1258.6 | 47.2 |
| ELS_Int_T | 1302.0 | 325.3 | [1262.0, 1340.0] | 1276.2 | 49.4 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 202.1 | 893.3 | [79.8, 316.3] | 249.7 | 1121.2 |
| ELS_Pres | -102.7 | 992.8 | [-251.2, 42.7] | -29.2 | 1426.0 |
| ELS_Int | -149.1 | 1020.5 | [-278.1, -27.8] | -19.0 | 1472.4 |
| SARSOP | 1236.7 | 373.2 | [1185.2, 1290.9] | 1219.2 | 86.6 |
| PBVI | 1256.9 | 410.6 | [1212.8, 1301.7] | 1241.6 | 66.4 |
| SDP_S | 1303.2 | 315.9 | [1262.5, 1348.7] | 1259.1 | 20.1 |
| SDP_NS | 1335.9 | 330.8 | [1302.2, 1371.6] | 1294.1 | -12.6 |
| MPC | 1301.3 | 334.9 | [1257.8, 1346.8] | 1245.8 | 22.0 |
| RDM | 1355.1 | 322.9 | [1313.2, 1400.9] | 1314.2 | -31.8 |
| InfoGap | 1110.2 | 353.3 | [1069.1, 1146.8] | 972.4 | 213.1 |
| AlwaysRestricted | -648.4 | 1565.2 | [-800.1, -508.2] | -212.6 | 1971.7 |
| MyopicEU | 1323.3 | 315.5 | [1290.5, 1356.0] | 1282.9 | — |
| SARSOP_Misspec | 1229.1 | 345.0 | [1189.7, 1267.0] | 1231.7 | 94.2 |
| SDP_S_Misspec | 1309.6 | 330.8 | [1271.2, 1350.0] | 1264.3 | 13.8 |
| ELS_Phil_T | 1339.6 | 376.1 | [1293.6, 1384.6] | 1302.3 | -16.2 |
| ELS_Int_T | 1272.9 | 345.8 | [1236.0, 1312.8] | 1239.0 | 50.4 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.775 | [0.705, 0.835] | 12.1 | 11.0 |
| ELS_Pres | 0.860 | [0.810, 0.905] | 8.7 | 8.0 |
| ELS_Int | 0.830 | [0.780, 0.875] | 9.8 | 9.0 |
| SARSOP | 0.575 | [0.520, 0.625] | 10.1 | 8.0 |
| PBVI | 0.600 | [0.540, 0.660] | 8.6 | 7.0 |
| SDP_S | 0.490 | [0.420, 0.560] | 9.5 | 6.0 |
| SDP_NS | 0.530 | [0.460, 0.605] | 9.9 | 8.0 |
| MPC | 0.555 | [0.490, 0.615] | 9.8 | 7.0 |
| RDM | 0.500 | [0.425, 0.580] | 9.4 | 8.0 |
| InfoGap | 0.425 | [0.360, 0.490] | 6.5 | 1.0 |
| AlwaysRestricted | 0.615 | [0.550, 0.670] | 8.1 | 5.0 |
| MyopicEU | 0.505 | [0.430, 0.575] | 6.9 | 3.0 |
| SARSOP_Misspec | 0.665 | [0.600, 0.730] | 9.0 | 7.0 |
| SDP_S_Misspec | 0.500 | [0.430, 0.570] | 8.3 | 6.0 |
| ELS_Phil_T | 0.555 | [0.495, 0.615] | 9.1 | 7.0 |
| ELS_Int_T | 0.650 | [0.600, 0.700] | 8.5 | 6.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.820 | [0.780, 0.865] | 11.2 | 9.5 |
| ELS_Pres | 0.885 | [0.825, 0.940] | 10.4 | 9.0 |
| ELS_Int | 0.850 | [0.790, 0.905] | 11.5 | 11.0 |
| SARSOP | 0.735 | [0.670, 0.795] | 10.8 | 9.0 |
| PBVI | 0.720 | [0.650, 0.790] | 10.9 | 9.5 |
| SDP_S | 0.595 | [0.535, 0.660] | 9.7 | 7.0 |
| SDP_NS | 0.570 | [0.520, 0.615] | 10.9 | 10.0 |
| MPC | 0.525 | [0.480, 0.570] | 10.9 | 11.0 |
| RDM | 0.655 | [0.610, 0.700] | 9.6 | 7.0 |
| InfoGap | 0.475 | [0.410, 0.540] | 9.5 | 5.0 |
| AlwaysRestricted | 0.655 | [0.600, 0.710] | 8.8 | 6.0 |
| MyopicEU | 0.575 | [0.520, 0.625] | 10.4 | 7.0 |
| SARSOP_Misspec | 0.710 | [0.630, 0.780] | 12.1 | 11.0 |
| SDP_S_Misspec | 0.510 | [0.445, 0.575] | 8.9 | 7.0 |
| ELS_Phil_T | 0.685 | [0.620, 0.750] | 9.9 | 7.0 |
| ELS_Int_T | 0.650 | [0.605, 0.690] | 12.7 | 13.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 1664.000 | 0.0000 | 0.0000 | ✓ | -1.308 |
| PBVI | wilcoxon_sr | 1456.000 | 0.0000 | 0.0000 | ✓ | -1.333 |
| SDP_S | wilcoxon_sr | 1244.000 | 0.0000 | 0.0000 | ✓ | -1.445 |
| SDP_NS | wilcoxon_sr | 1231.000 | 0.0000 | 0.0000 | ✓ | -1.463 |
| MPC | wilcoxon_sr | 1342.000 | 0.0000 | 0.0000 | ✓ | -1.407 |
| RDM | wilcoxon_sr | 1374.000 | 0.0000 | 0.0000 | ✓ | -1.406 |
| InfoGap | wilcoxon_sr | 2234.000 | 0.0000 | 0.0000 | ✓ | -1.175 |
| AlwaysRestricted | paired_t | 5.090 | 0.0000 | 0.0000 | ✓ | 0.481 |
| MyopicEU | wilcoxon_sr | 1155.000 | 0.0000 | 0.0000 | ✓ | -1.462 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -17.924 | 0.0000 | 0.0000 | ✓ | -1.804 |
| PBVI | wilcoxon_sr | 473.000 | 0.0000 | 0.0000 | ✓ | -1.808 |
| SDP_S | wilcoxon_sr | 370.000 | 0.0000 | 0.0000 | ✓ | -1.923 |
| SDP_NS | wilcoxon_sr | 213.000 | 0.0000 | 0.0000 | ✓ | -1.958 |
| MPC | wilcoxon_sr | 311.000 | 0.0000 | 0.0000 | ✓ | -1.910 |
| RDM | wilcoxon_sr | 246.000 | 0.0000 | 0.0000 | ✓ | -1.987 |
| InfoGap | wilcoxon_sr | 867.000 | 0.0000 | 0.0000 | ✓ | -1.649 |
| AlwaysRestricted | wilcoxon_sr | 7529.000 | 0.0021 | 0.0021 | ✓ | 0.378 |
| MyopicEU | paired_t | -19.257 | 0.0000 | 0.0000 | ✓ | -1.949 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 343.4 | -201.7 | 545.0 | 1126.7 | 6.841 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 445.3 | -243.2 | 688.4 | 1166.2 | 8.349 | 0.0000 | ✓ |
| ELS_Pres | stationary | 114.1 | -133.2 | 247.3 | 1117.0 | 3.132 | 0.0020 | ✓ |
| ELS_Pres | nonstationary | 263.1 | -365.8 | 628.9 | 1141.3 | 7.792 | 0.0000 | ✓ |
| ELS_Int | stationary | 388.6 | -275.2 | 663.8 | 1144.9 | 8.199 | 0.0000 | ✓ |
| ELS_Int | nonstationary | 263.2 | -412.3 | 675.5 | 1324.2 | 7.215 | 0.0000 | ✓ |
| SARSOP | stationary | 746.6 | 470.5 | 276.1 | 328.8 | 11.873 | 0.0000 | ✓ |
| SARSOP | nonstationary | 755.8 | 480.9 | 274.9 | 378.7 | 10.264 | 0.0000 | ✓ |
| PBVI | stationary | 753.5 | 490.9 | 262.6 | 332.0 | 11.188 | 0.0000 | ✓ |
| PBVI | nonstationary | 783.1 | 473.8 | 309.3 | 353.3 | 12.379 | 0.0000 | ✓ |
| SDP_S | stationary | 807.6 | 519.3 | 288.3 | 290.5 | 14.032 | 0.0000 | ✓ |
| SDP_S | nonstationary | 824.0 | 479.2 | 344.9 | 307.2 | 15.874 | 0.0000 | ✓ |
| SDP_NS | stationary | 790.3 | 547.3 | 243.0 | 298.2 | 11.525 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 834.8 | 501.1 | 333.6 | 315.2 | 14.970 | 0.0000 | ✓ |
| MPC | stationary | 778.4 | 516.1 | 262.2 | 297.9 | 12.450 | 0.0000 | ✓ |
| MPC | nonstationary | 790.2 | 511.1 | 279.1 | 305.9 | 12.907 | 0.0000 | ✓ |
| RDM | stationary | 793.2 | 499.4 | 293.9 | 255.9 | 16.242 | 0.0000 | ✓ |
| RDM | nonstationary | 841.3 | 513.7 | 327.6 | 324.3 | 14.288 | 0.0000 | ✓ |
| InfoGap | stationary | 698.3 | 417.4 | 280.8 | 319.0 | 12.450 | 0.0000 | ✓ |
| InfoGap | nonstationary | 679.9 | 430.3 | 249.6 | 289.9 | 12.175 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | -298.8 | -219.0 | -79.8 | 977.7 | -1.155 | 0.2497 | – |
| AlwaysRestricted | nonstationary | -357.4 | -291.0 | -66.3 | 1128.8 | -0.831 | 0.4069 | – |
| MyopicEU | stationary | 834.8 | 516.6 | 318.3 | 318.1 | 14.150 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 815.6 | 507.7 | 307.8 | 297.8 | 14.617 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 772.5 | 504.8 | 267.7 | 360.6 | 10.497 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 736.9 | 492.2 | 244.6 | 361.0 | 9.582 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 807.7 | 507.7 | 299.9 | 315.0 | 13.467 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 817.1 | 492.4 | 324.7 | 272.8 | 16.832 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 794.4 | 509.8 | 284.5 | 311.1 | 12.934 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 845.7 | 493.8 | 351.9 | 347.8 | 14.307 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 794.6 | 507.4 | 287.2 | 327.6 | 12.400 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 765.8 | 507.1 | 258.7 | 326.4 | 11.209 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | 10.63 | 440.46 | [-34.05, 58.37] |
| nonstationary | 32.70 | 433.48 | [-18.09, 83.06] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2778 | 0.0947 | [0.2682, 0.2875] |
| nonstationary | 0.2695 | 0.0921 | [0.2555, 0.2828] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 89.93 | 74.56 | 67.45 | 60.85 | 4.7 % | ✗ |
| ELS_Phil | nonstationary | 130.88 | 88.09 | 71.10 | 63.17 | 3.9 % | ✗ |
| ELS_Pres | stationary | 147.23 | 109.68 | 84.56 | 77.88 | 35.0 % | ✗ |
| ELS_Pres | nonstationary | 121.79 | 100.08 | 81.14 | 70.20 | 10.6 % | ✗ |
| ELS_Int | stationary | 165.38 | 116.74 | 95.25 | 80.79 | 12.8 % | ✗ |
| ELS_Int | nonstationary | 147.76 | 100.95 | 83.03 | 72.16 | 7.3 % | ✗ |
| SARSOP | stationary | 48.82 | 35.03 | 28.27 | 24.37 | 0.3 % | ✓ |
| SARSOP | nonstationary | 42.79 | 36.00 | 30.67 | 26.39 | 0.3 % | ✓ |
| PBVI | stationary | 53.30 | 37.11 | 31.86 | 25.92 | 0.5 % | ✓ |
| PBVI | nonstationary | 63.29 | 44.01 | 33.51 | 29.03 | 0.4 % | ✓ |
| SDP_S | stationary | 45.75 | 31.47 | 26.36 | 22.88 | 0.3 % | ✓ |
| SDP_S | nonstationary | 51.24 | 33.31 | 25.98 | 22.34 | 0.3 % | ✓ |
| SDP_NS | stationary | 42.54 | 30.45 | 25.82 | 21.79 | 0.3 % | ✓ |
| SDP_NS | nonstationary | 42.61 | 31.55 | 27.51 | 23.39 | 0.3 % | ✓ |
| MPC | stationary | 47.36 | 31.39 | 24.37 | 22.77 | 0.1 % | ✓ |
| MPC | nonstationary | 43.48 | 31.67 | 26.59 | 23.68 | 0.2 % | ✓ |
| RDM | stationary | 40.37 | 34.67 | 26.78 | 22.54 | 0.3 % | ✓ |
| RDM | nonstationary | 41.72 | 30.36 | 25.62 | 22.83 | 0.2 % | ✓ |
| InfoGap | stationary | 56.21 | 40.38 | 31.22 | 27.36 | 0.3 % | ✓ |
| InfoGap | nonstationary | 41.35 | 34.35 | 29.22 | 24.98 | 0.4 % | ✓ |
| AlwaysRestricted | stationary | 233.36 | 157.81 | 123.80 | 103.41 | 3.9 % | ✗ |
| AlwaysRestricted | nonstationary | 232.76 | 154.14 | 127.36 | 110.68 | 2.6 % | ✗ |
| MyopicEU | stationary | 45.85 | 34.04 | 28.62 | 25.40 | 0.2 % | ✓ |
| MyopicEU | nonstationary | 52.78 | 34.56 | 26.92 | 22.31 | 0.3 % | ✓ |
| SARSOP_Misspec | stationary | 61.49 | 39.96 | 32.58 | 27.28 | 0.4 % | ✓ |
| SARSOP_Misspec | nonstationary | 55.37 | 35.79 | 28.71 | 24.40 | 0.4 % | ✓ |
| SDP_S_Misspec | stationary | 40.21 | 30.39 | 26.14 | 24.35 | 0.1 % | ✓ |
| SDP_S_Misspec | nonstationary | 48.99 | 33.15 | 27.72 | 23.39 | 0.3 % | ✓ |
| ELS_Phil_T | stationary | 44.27 | 33.86 | 28.11 | 24.46 | 0.3 % | ✓ |
| ELS_Phil_T | nonstationary | 49.00 | 35.82 | 30.99 | 26.59 | 0.3 % | ✓ |
| ELS_Int_T | stationary | 38.23 | 26.44 | 25.79 | 23.01 | 0.2 % | ✓ |
| ELS_Int_T | nonstationary | 51.06 | 37.58 | 28.59 | 24.45 | 0.3 % | ✓ |

---

## Notes

- **Convergence:** 24/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


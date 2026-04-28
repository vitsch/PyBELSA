# Benchmark 2 — Statistical Report
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
| ELS_Phil | 755.9 | 278.6 | [707.8, 803.9] | 773.2 | 508.0 |
| ELS_Pres | 612.8 | 395.1 | [561.9, 661.6] | 714.3 | 651.0 |
| ELS_Int | 698.8 | 353.2 | [645.8, 749.5] | 725.4 | 565.1 |
| SARSOP | 1281.5 | 232.0 | [1254.9, 1306.9] | 1267.7 | -17.6 |
| PBVI | 1263.4 | 232.6 | [1237.4, 1289.0] | 1231.4 | 0.4 |
| SDP_S | 1273.7 | 249.6 | [1244.1, 1303.2] | 1272.6 | -9.9 |
| SDP_NS | 1249.7 | 246.6 | [1216.5, 1282.7] | 1221.9 | 14.1 |
| MPC | 1231.4 | 268.1 | [1192.6, 1269.9] | 1257.0 | 32.4 |
| RDM | 1238.2 | 249.0 | [1209.2, 1266.5] | 1234.2 | 25.7 |
| InfoGap | 1084.2 | 161.8 | [1065.7, 1102.5] | 1095.4 | 179.6 |
| AlwaysRestricted | 928.3 | 460.8 | [883.2, 976.5] | 1070.0 | 335.6 |
| MyopicEU | 1263.8 | 299.3 | [1218.4, 1306.9] | 1276.8 | — |
| SARSOP_Misspec | 1251.5 | 242.4 | [1223.9, 1280.4] | 1261.5 | 12.4 |
| SDP_S_Misspec | 1264.0 | 218.3 | [1236.6, 1291.9] | 1261.2 | -0.2 |
| ELS_Phil_T | 1106.7 | 259.6 | [1069.1, 1143.6] | 1084.7 | 157.1 |
| ELS_Int_T | 1083.8 | 284.5 | [1052.4, 1113.2] | 1075.9 | 180.0 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 666.9 | 229.6 | [635.1, 697.5] | 650.5 | 527.9 |
| ELS_Pres | 541.9 | 335.3 | [493.9, 587.3] | 572.7 | 652.9 |
| ELS_Int | 648.4 | 255.8 | [614.4, 687.6] | 649.6 | 546.4 |
| SARSOP | 1181.6 | 224.4 | [1152.2, 1207.8] | 1179.4 | 13.2 |
| PBVI | 1181.8 | 224.1 | [1158.5, 1207.1] | 1156.8 | 13.0 |
| SDP_S | 1198.8 | 233.8 | [1171.0, 1226.6] | 1180.4 | -4.0 |
| SDP_NS | 1212.5 | 242.7 | [1186.1, 1236.8] | 1217.4 | -17.7 |
| MPC | 1173.9 | 278.9 | [1149.5, 1198.7] | 1165.1 | 20.8 |
| RDM | 1141.2 | 276.3 | [1106.6, 1175.7] | 1156.8 | 53.6 |
| InfoGap | 1087.5 | 150.3 | [1063.9, 1112.4] | 1095.8 | 107.3 |
| AlwaysRestricted | 810.9 | 547.1 | [745.1, 870.9] | 965.2 | 383.9 |
| MyopicEU | 1194.8 | 239.9 | [1165.4, 1225.1] | 1222.2 | — |
| SARSOP_Misspec | 1191.4 | 210.9 | [1168.9, 1213.8] | 1197.9 | 3.4 |
| SDP_S_Misspec | 1199.9 | 244.0 | [1161.5, 1237.8] | 1203.5 | -5.1 |
| ELS_Phil_T | 1041.9 | 271.4 | [1000.6, 1084.6] | 1015.6 | 152.9 |
| ELS_Int_T | 1030.4 | 266.9 | [988.8, 1073.7] | 1004.6 | 164.4 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.795 | [0.740, 0.850] | 11.8 | 11.0 |
| ELS_Pres | 0.830 | [0.780, 0.875] | 8.8 | 7.0 |
| ELS_Int | 0.785 | [0.730, 0.840] | 9.5 | 8.0 |
| SARSOP | 0.260 | [0.215, 0.310] | 9.4 | 4.5 |
| PBVI | 0.270 | [0.200, 0.340] | 9.1 | 6.5 |
| SDP_S | 0.360 | [0.315, 0.405] | 11.1 | 10.0 |
| SDP_NS | 0.420 | [0.360, 0.490] | 10.8 | 10.5 |
| MPC | 0.485 | [0.410, 0.560] | 8.6 | 6.0 |
| RDM | 0.390 | [0.325, 0.455] | 8.2 | 7.0 |
| InfoGap | 0.275 | [0.215, 0.340] | 5.9 | 0.0 |
| AlwaysRestricted | 0.525 | [0.465, 0.585] | 9.5 | 7.0 |
| MyopicEU | 0.415 | [0.330, 0.505] | 6.4 | 1.0 |
| SARSOP_Misspec | 0.300 | [0.255, 0.345] | 7.7 | 3.0 |
| SDP_S_Misspec | 0.345 | [0.275, 0.410] | 11.1 | 10.0 |
| ELS_Phil_T | 0.540 | [0.475, 0.610] | 9.4 | 7.0 |
| ELS_Int_T | 0.535 | [0.480, 0.590] | 8.2 | 5.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.890 | [0.855, 0.925] | 11.1 | 11.0 |
| ELS_Pres | 0.910 | [0.855, 0.955] | 9.1 | 8.0 |
| ELS_Int | 0.910 | [0.870, 0.945] | 11.6 | 11.0 |
| SARSOP | 0.430 | [0.350, 0.500] | 12.3 | 11.0 |
| PBVI | 0.420 | [0.360, 0.475] | 12.6 | 13.5 |
| SDP_S | 0.485 | [0.410, 0.555] | 11.3 | 11.0 |
| SDP_NS | 0.450 | [0.385, 0.515] | 13.2 | 16.0 |
| MPC | 0.565 | [0.505, 0.625] | 10.5 | 10.0 |
| RDM | 0.575 | [0.505, 0.645] | 9.4 | 7.0 |
| InfoGap | 0.315 | [0.230, 0.405] | 11.6 | 11.0 |
| AlwaysRestricted | 0.685 | [0.625, 0.750] | 11.2 | 10.0 |
| MyopicEU | 0.535 | [0.465, 0.605] | 11.6 | 11.0 |
| SARSOP_Misspec | 0.380 | [0.310, 0.445] | 13.1 | 13.5 |
| SDP_S_Misspec | 0.445 | [0.400, 0.490] | 11.2 | 9.0 |
| ELS_Phil_T | 0.615 | [0.565, 0.665] | 10.3 | 8.0 |
| ELS_Int_T | 0.670 | [0.595, 0.740] | 12.4 | 13.5 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 480.000 | 0.0000 | 0.0000 | ✓ | -1.950 |
| PBVI | wilcoxon_sr | 311.000 | 0.0000 | 0.0000 | ✓ | -1.888 |
| SDP_S | wilcoxon_sr | 508.000 | 0.0000 | 0.0000 | ✓ | -1.880 |
| SDP_NS | wilcoxon_sr | 611.000 | 0.0000 | 0.0000 | ✓ | -1.809 |
| MPC | wilcoxon_sr | 685.000 | 0.0000 | 0.0000 | ✓ | -1.699 |
| RDM | wilcoxon_sr | 677.000 | 0.0000 | 0.0000 | ✓ | -1.765 |
| InfoGap | wilcoxon_sr | 1352.000 | 0.0000 | 0.0000 | ✓ | -1.403 |
| AlwaysRestricted | wilcoxon_sr | 5576.000 | 0.0000 | 0.0000 | ✓ | -0.559 |
| MyopicEU | paired_t | -16.642 | 0.0000 | 0.0000 | ✓ | -1.726 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -22.607 | 0.0000 | 0.0000 | ✓ | -2.216 |
| PBVI | paired_t | -22.893 | 0.0000 | 0.0000 | ✓ | -2.218 |
| SDP_S | paired_t | -22.324 | 0.0000 | 0.0000 | ✓ | -2.246 |
| SDP_NS | paired_t | -21.504 | 0.0000 | 0.0000 | ✓ | -2.263 |
| MPC | wilcoxon_sr | 665.000 | 0.0000 | 0.0000 | ✓ | -1.964 |
| RDM | paired_t | -17.953 | 0.0000 | 0.0000 | ✓ | -1.851 |
| InfoGap | wilcoxon_sr | 428.000 | 0.0000 | 0.0000 | ✓ | -2.093 |
| AlwaysRestricted | wilcoxon_sr | 6520.000 | 0.0000 | 0.0000 | ✓ | -0.380 |
| MyopicEU | paired_t | -21.941 | 0.0000 | 0.0000 | ✓ | -2.203 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 507.6 | 248.3 | 259.2 | 434.4 | 8.440 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 494.7 | 172.2 | 322.5 | 472.2 | 9.658 | 0.0000 | ✓ |
| ELS_Pres | stationary | 382.0 | 230.8 | 151.2 | 521.7 | 4.099 | 0.0001 | ✓ |
| ELS_Pres | nonstationary | 409.4 | 132.5 | 276.9 | 539.6 | 7.257 | 0.0000 | ✓ |
| ELS_Int | stationary | 470.0 | 228.8 | 241.2 | 498.7 | 6.839 | 0.0000 | ✓ |
| ELS_Int | nonstationary | 493.4 | 155.0 | 338.4 | 520.1 | 9.201 | 0.0000 | ✓ |
| SARSOP | stationary | 771.6 | 509.8 | 261.8 | 225.7 | 16.406 | 0.0000 | ✓ |
| SARSOP | nonstationary | 735.5 | 446.1 | 289.4 | 225.2 | 18.174 | 0.0000 | ✓ |
| PBVI | stationary | 742.4 | 521.0 | 221.3 | 210.0 | 14.906 | 0.0000 | ✓ |
| PBVI | nonstationary | 731.0 | 450.8 | 280.2 | 225.0 | 17.609 | 0.0000 | ✓ |
| SDP_S | stationary | 765.2 | 508.5 | 256.6 | 208.9 | 17.377 | 0.0000 | ✓ |
| SDP_S | nonstationary | 744.7 | 454.1 | 290.6 | 241.6 | 17.005 | 0.0000 | ✓ |
| SDP_NS | stationary | 754.1 | 495.6 | 258.5 | 215.8 | 16.939 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 763.7 | 448.8 | 314.9 | 227.2 | 19.600 | 0.0000 | ✓ |
| MPC | stationary | 738.4 | 493.0 | 245.4 | 239.5 | 14.487 | 0.0000 | ✓ |
| MPC | nonstationary | 741.9 | 432.0 | 309.9 | 258.8 | 16.937 | 0.0000 | ✓ |
| RDM | stationary | 731.8 | 506.3 | 225.5 | 229.2 | 13.919 | 0.0000 | ✓ |
| RDM | nonstationary | 702.9 | 438.3 | 264.6 | 270.8 | 13.821 | 0.0000 | ✓ |
| InfoGap | stationary | 641.5 | 442.7 | 198.7 | 138.0 | 20.360 | 0.0000 | ✓ |
| InfoGap | nonstationary | 657.4 | 430.1 | 227.3 | 130.0 | 24.734 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 563.0 | 365.3 | 197.7 | 360.3 | 7.760 | 0.0000 | ✓ |
| AlwaysRestricted | nonstationary | 531.2 | 279.7 | 251.5 | 417.9 | 8.510 | 0.0000 | ✓ |
| MyopicEU | stationary | 750.9 | 513.0 | 237.9 | 243.6 | 13.810 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 745.4 | 449.4 | 296.0 | 223.7 | 18.717 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 731.1 | 520.3 | 210.8 | 216.0 | 13.799 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 755.9 | 435.5 | 320.5 | 216.8 | 20.905 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 740.9 | 523.1 | 217.8 | 241.5 | 12.751 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 751.6 | 448.3 | 303.3 | 200.4 | 21.407 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 670.6 | 436.1 | 234.4 | 266.3 | 12.449 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 661.2 | 380.7 | 280.5 | 256.9 | 15.439 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 651.8 | 432.0 | 219.8 | 257.8 | 12.060 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 673.3 | 357.0 | 316.3 | 288.6 | 15.498 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | -24.01 | 347.75 | [-71.32, 20.29] |
| nonstationary | 13.72 | 328.15 | [-21.72, 46.27] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2138 | 0.0808 | [0.2048, 0.2228] |
| nonstationary | 0.2215 | 0.0814 | [0.2112, 0.2322] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 32.94 | 25.21 | 22.16 | 19.70 | 0.3 % | ✓ |
| ELS_Phil | nonstationary | 32.52 | 23.68 | 18.96 | 16.23 | 0.4 % | ✓ |
| ELS_Pres | stationary | 60.06 | 40.99 | 32.85 | 27.94 | 0.8 % | ✓ |
| ELS_Pres | nonstationary | 38.42 | 25.90 | 24.46 | 23.71 | 0.1 % | ✓ |
| ELS_Int | stationary | 43.39 | 33.32 | 30.11 | 24.97 | 0.7 % | ✓ |
| ELS_Int | nonstationary | 32.17 | 23.25 | 20.49 | 18.09 | 0.4 % | ✓ |
| SARSOP | stationary | 35.82 | 23.50 | 19.04 | 16.41 | 0.2 % | ✓ |
| SARSOP | nonstationary | 28.96 | 21.11 | 17.75 | 15.87 | 0.2 % | ✓ |
| PBVI | stationary | 29.86 | 24.78 | 19.45 | 16.45 | 0.2 % | ✓ |
| PBVI | nonstationary | 26.32 | 21.50 | 18.17 | 15.85 | 0.2 % | ✓ |
| SDP_S | stationary | 39.30 | 25.64 | 20.40 | 17.65 | 0.2 % | ✓ |
| SDP_S | nonstationary | 33.39 | 24.12 | 19.79 | 16.53 | 0.3 % | ✓ |
| SDP_NS | stationary | 36.89 | 24.56 | 20.73 | 17.44 | 0.3 % | ✓ |
| SDP_NS | nonstationary | 35.84 | 24.83 | 20.11 | 17.16 | 0.2 % | ✓ |
| MPC | stationary | 37.60 | 26.70 | 21.74 | 18.95 | 0.2 % | ✓ |
| MPC | nonstationary | 38.52 | 27.05 | 24.22 | 19.72 | 0.4 % | ✓ |
| RDM | stationary | 40.88 | 25.71 | 20.72 | 17.61 | 0.3 % | ✓ |
| RDM | nonstationary | 34.51 | 27.90 | 22.01 | 19.54 | 0.2 % | ✓ |
| InfoGap | stationary | 22.23 | 15.56 | 13.42 | 11.44 | 0.2 % | ✓ |
| InfoGap | nonstationary | 20.49 | 15.21 | 12.63 | 10.63 | 0.2 % | ✓ |
| AlwaysRestricted | stationary | 64.76 | 46.57 | 38.06 | 32.59 | 0.6 % | ✓ |
| AlwaysRestricted | nonstationary | 84.98 | 56.29 | 45.24 | 38.68 | 0.8 % | ✓ |
| MyopicEU | stationary | 39.05 | 28.10 | 23.99 | 21.16 | 0.2 % | ✓ |
| MyopicEU | nonstationary | 32.03 | 25.21 | 20.23 | 16.97 | 0.3 % | ✓ |
| SARSOP_Misspec | stationary | 33.86 | 23.09 | 18.80 | 17.14 | 0.1 % | ✓ |
| SARSOP_Misspec | nonstationary | 26.97 | 20.57 | 16.90 | 14.91 | 0.2 % | ✓ |
| SDP_S_Misspec | stationary | 33.75 | 22.24 | 17.70 | 15.43 | 0.2 % | ✓ |
| SDP_S_Misspec | nonstationary | 38.19 | 25.28 | 19.64 | 17.25 | 0.2 % | ✓ |
| ELS_Phil_T | stationary | 37.34 | 26.34 | 21.13 | 18.36 | 0.2 % | ✓ |
| ELS_Phil_T | nonstationary | 38.07 | 27.00 | 22.83 | 19.19 | 0.3 % | ✓ |
| ELS_Int_T | stationary | 36.96 | 27.68 | 23.13 | 20.12 | 0.3 % | ✓ |
| ELS_Int_T | nonstationary | 39.83 | 26.70 | 21.84 | 18.87 | 0.3 % | ✓ |

---

## Notes

- **Convergence:** 32/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


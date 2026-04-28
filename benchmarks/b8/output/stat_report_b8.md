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
| ELS_Phil | 595.0 | 347.0 | [540.5, 643.7] | 695.2 | 317.2 |
| ELS_Pres | 89.6 | 1124.4 | [-70.6, 234.9] | 438.6 | 822.5 |
| ELS_Int | 262.3 | 613.3 | [179.3, 341.9] | 417.4 | 649.9 |
| SARSOP | 797.8 | 244.3 | [752.6, 844.8] | 808.1 | 114.3 |
| PBVI | 817.4 | 255.4 | [778.7, 857.4] | 828.9 | 94.7 |
| SDP_S | 913.4 | 159.2 | [892.1, 931.9] | 925.2 | -1.2 |
| SDP_NS | 928.3 | 173.8 | [910.0, 946.8] | 924.0 | -16.1 |
| MPC | 913.0 | 183.7 | [892.6, 933.8] | 906.4 | -0.8 |
| RDM | 922.3 | 191.7 | [899.0, 946.9] | 908.1 | -10.1 |
| InfoGap | 907.4 | 219.3 | [887.9, 926.6] | 881.6 | 4.8 |
| AlwaysRestricted | 329.8 | 541.9 | [267.5, 390.5] | 453.7 | 582.4 |
| MyopicEU | 912.2 | 199.0 | [883.3, 946.3] | 908.4 | — |
| SARSOP_Misspec | 841.6 | 230.9 | [808.9, 875.6] | 849.4 | 70.6 |
| SDP_S_Misspec | 921.9 | 175.9 | [903.5, 939.9] | 915.8 | -9.7 |
| ELS_Phil_T | 875.3 | 223.2 | [848.7, 900.6] | 866.1 | 36.9 |
| ELS_Int_T | 848.8 | 231.1 | [818.6, 881.5] | 853.5 | 63.4 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 503.3 | 316.8 | [448.0, 556.4] | 539.5 | 422.5 |
| ELS_Pres | 92.2 | 924.7 | [-47.8, 223.6] | 344.8 | 833.6 |
| ELS_Int | 163.7 | 550.0 | [86.3, 236.8] | 257.1 | 762.1 |
| SARSOP | 834.4 | 241.8 | [805.4, 862.9] | 834.4 | 91.4 |
| PBVI | 833.7 | 237.7 | [805.8, 860.6] | 804.7 | 92.1 |
| SDP_S | 930.6 | 168.0 | [909.2, 951.8] | 928.2 | -4.8 |
| SDP_NS | 929.4 | 178.5 | [904.7, 952.7] | 927.6 | -3.6 |
| MPC | 926.9 | 185.1 | [903.5, 946.4] | 909.8 | -1.1 |
| RDM | 961.5 | 221.9 | [935.2, 991.1] | 912.8 | -35.7 |
| InfoGap | 895.8 | 194.0 | [875.5, 916.5] | 871.8 | 30.0 |
| AlwaysRestricted | 180.7 | 693.1 | [85.1, 271.5] | 383.1 | 745.1 |
| MyopicEU | 925.8 | 189.7 | [909.8, 941.7] | 909.6 | — |
| SARSOP_Misspec | 845.6 | 237.3 | [820.9, 869.9] | 841.1 | 80.1 |
| SDP_S_Misspec | 930.0 | 177.4 | [904.5, 955.6] | 929.0 | -4.2 |
| ELS_Phil_T | 921.3 | 214.0 | [894.3, 952.2] | 912.2 | 4.5 |
| ELS_Int_T | 859.4 | 243.2 | [825.0, 893.5] | 880.1 | 66.4 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.650 | [0.595, 0.710] | 12.4 | 11.5 |
| ELS_Pres | 0.840 | [0.790, 0.885] | 8.4 | 7.0 |
| ELS_Int | 0.800 | [0.730, 0.860] | 9.9 | 8.0 |
| SARSOP | 0.615 | [0.560, 0.675] | 11.6 | 10.0 |
| PBVI | 0.665 | [0.615, 0.715] | 10.2 | 9.0 |
| SDP_S | 0.580 | [0.530, 0.635] | 10.2 | 8.0 |
| SDP_NS | 0.625 | [0.560, 0.685] | 9.4 | 8.0 |
| MPC | 0.610 | [0.545, 0.675] | 10.4 | 9.0 |
| RDM | 0.585 | [0.530, 0.635] | 10.6 | 10.0 |
| InfoGap | 0.560 | [0.490, 0.625] | 8.1 | 5.0 |
| AlwaysRestricted | 0.715 | [0.645, 0.780] | 10.0 | 8.0 |
| MyopicEU | 0.550 | [0.470, 0.625] | 8.2 | 5.0 |
| SARSOP_Misspec | 0.650 | [0.595, 0.705] | 10.2 | 10.0 |
| SDP_S_Misspec | 0.710 | [0.650, 0.765] | 10.3 | 9.0 |
| ELS_Phil_T | 0.615 | [0.550, 0.675] | 10.5 | 8.0 |
| ELS_Int_T | 0.690 | [0.640, 0.740] | 9.0 | 7.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.810 | [0.755, 0.865] | 12.4 | 12.0 |
| ELS_Pres | 0.915 | [0.880, 0.950] | 10.3 | 9.0 |
| ELS_Int | 0.925 | [0.890, 0.955] | 11.7 | 11.0 |
| SARSOP | 0.800 | [0.750, 0.845] | 11.4 | 10.5 |
| PBVI | 0.770 | [0.720, 0.815] | 11.4 | 10.5 |
| SDP_S | 0.775 | [0.730, 0.820] | 11.0 | 10.0 |
| SDP_NS | 0.720 | [0.655, 0.785] | 12.1 | 14.0 |
| MPC | 0.740 | [0.675, 0.795] | 12.4 | 12.5 |
| RDM | 0.750 | [0.700, 0.800] | 10.4 | 9.0 |
| InfoGap | 0.685 | [0.625, 0.740] | 12.2 | 11.0 |
| AlwaysRestricted | 0.830 | [0.775, 0.880] | 11.4 | 11.0 |
| MyopicEU | 0.625 | [0.560, 0.685] | 11.6 | 13.0 |
| SARSOP_Misspec | 0.785 | [0.720, 0.845] | 12.1 | 14.0 |
| SDP_S_Misspec | 0.725 | [0.670, 0.775] | 11.3 | 12.0 |
| ELS_Phil_T | 0.770 | [0.705, 0.830] | 11.7 | 11.0 |
| ELS_Int_T | 0.785 | [0.730, 0.845] | 13.1 | 14.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 2087.000 | 0.0000 | 0.0000 | ✓ | -1.147 |
| PBVI | wilcoxon_sr | 1803.000 | 0.0000 | 0.0000 | ✓ | -1.182 |
| SDP_S | wilcoxon_sr | 593.000 | 0.0000 | 0.0000 | ✓ | -1.453 |
| SDP_NS | wilcoxon_sr | 634.000 | 0.0000 | 0.0000 | ✓ | -1.478 |
| MPC | wilcoxon_sr | 765.000 | 0.0000 | 0.0000 | ✓ | -1.437 |
| RDM | wilcoxon_sr | 714.000 | 0.0000 | 0.0000 | ✓ | -1.453 |
| InfoGap | wilcoxon_sr | 900.000 | 0.0000 | 0.0000 | ✓ | -1.401 |
| AlwaysRestricted | wilcoxon_sr | 9207.000 | 0.3037 | 0.3037 | – | -0.117 |
| MyopicEU | wilcoxon_sr | 525.000 | 0.0000 | 0.0000 | ✓ | -1.425 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 832.000 | 0.0000 | 0.0000 | ✓ | -1.579 |
| PBVI | wilcoxon_sr | 806.000 | 0.0000 | 0.0000 | ✓ | -1.581 |
| SDP_S | wilcoxon_sr | 168.000 | 0.0000 | 0.0000 | ✓ | -1.886 |
| SDP_NS | wilcoxon_sr | 215.000 | 0.0000 | 0.0000 | ✓ | -1.873 |
| MPC | wilcoxon_sr | 247.000 | 0.0000 | 0.0000 | ✓ | -1.860 |
| RDM | wilcoxon_sr | 288.000 | 0.0000 | 0.0000 | ✓ | -1.903 |
| InfoGap | wilcoxon_sr | 460.000 | 0.0000 | 0.0000 | ✓ | -1.775 |
| AlwaysRestricted | wilcoxon_sr | 9271.000 | 0.3419 | 0.3419 | – | -0.027 |
| MyopicEU | wilcoxon_sr | 312.000 | 0.0000 | 0.0000 | ✓ | -1.853 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 389.0 | 206.0 | 183.0 | 314.2 | 8.240 | 0.0000 | ✓ |
| ELS_Phil | nonstationary | 388.6 | 114.6 | 274.0 | 370.4 | 10.460 | 0.0000 | ✓ |
| ELS_Pres | stationary | 48.8 | 40.9 | 7.9 | 813.6 | 0.137 | 0.8912 | – |
| ELS_Pres | nonstationary | 255.6 | -163.4 | 419.0 | 978.9 | 6.053 | 0.0000 | ✓ |
| ELS_Int | stationary | 190.3 | 72.0 | 118.3 | 652.1 | 2.566 | 0.0110 | ✓ |
| ELS_Int | nonstationary | 173.2 | -9.6 | 182.8 | 701.3 | 3.686 | 0.0003 | ✓ |
| SARSOP | stationary | 472.9 | 324.9 | 148.0 | 240.7 | 8.695 | 0.0000 | ✓ |
| SARSOP | nonstationary | 498.6 | 335.8 | 162.7 | 223.2 | 10.313 | 0.0000 | ✓ |
| PBVI | stationary | 480.9 | 336.5 | 144.3 | 252.9 | 8.071 | 0.0000 | ✓ |
| PBVI | nonstationary | 505.8 | 327.8 | 178.0 | 260.7 | 9.656 | 0.0000 | ✓ |
| SDP_S | stationary | 544.8 | 368.6 | 176.2 | 154.6 | 16.119 | 0.0000 | ✓ |
| SDP_S | nonstationary | 566.2 | 364.4 | 201.8 | 167.1 | 17.082 | 0.0000 | ✓ |
| SDP_NS | stationary | 554.8 | 373.5 | 181.2 | 159.7 | 16.044 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 559.0 | 370.4 | 188.5 | 177.6 | 15.014 | 0.0000 | ✓ |
| MPC | stationary | 535.5 | 377.5 | 157.9 | 194.2 | 11.499 | 0.0000 | ✓ |
| MPC | nonstationary | 534.6 | 392.3 | 142.4 | 190.4 | 10.572 | 0.0000 | ✓ |
| RDM | stationary | 554.0 | 368.3 | 185.7 | 178.5 | 14.707 | 0.0000 | ✓ |
| RDM | nonstationary | 561.9 | 399.6 | 162.2 | 224.6 | 10.217 | 0.0000 | ✓ |
| InfoGap | stationary | 537.7 | 369.7 | 168.0 | 206.2 | 11.523 | 0.0000 | ✓ |
| InfoGap | nonstationary | 530.1 | 365.7 | 164.4 | 194.2 | 11.976 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 224.3 | 105.5 | 118.8 | 496.7 | 3.381 | 0.0009 | ✓ |
| AlwaysRestricted | nonstationary | 186.0 | -5.3 | 191.3 | 573.6 | 4.715 | 0.0000 | ✓ |
| MyopicEU | stationary | 550.6 | 361.6 | 189.1 | 198.3 | 13.483 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 542.0 | 383.8 | 158.2 | 185.7 | 12.047 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 505.1 | 336.5 | 168.6 | 256.9 | 9.280 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 498.9 | 346.7 | 152.2 | 225.2 | 9.560 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 555.4 | 366.5 | 189.0 | 168.5 | 15.862 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 565.5 | 364.5 | 201.0 | 154.2 | 18.437 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 522.9 | 352.4 | 170.5 | 218.6 | 11.027 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 564.0 | 357.3 | 206.7 | 236.9 | 12.339 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 511.9 | 336.8 | 175.1 | 217.8 | 11.368 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 511.5 | 347.9 | 163.6 | 245.7 | 9.418 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | 14.91 | 223.78 | [-10.60, 40.48] |
| nonstationary | -1.17 | 247.04 | [-31.86, 29.10] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2555 | 0.1003 | [0.2403, 0.2688] |
| nonstationary | 0.2522 | 0.0898 | [0.2390, 0.2655] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 40.94 | 28.85 | 23.32 | 24.54 | 0.2 % | ✓ |
| ELS_Phil | nonstationary | 44.46 | 30.94 | 24.79 | 22.40 | 0.5 % | ✓ |
| ELS_Pres | stationary | 184.26 | 108.41 | 87.79 | 79.51 | 9.2 % | ✗ |
| ELS_Pres | nonstationary | 88.29 | 83.42 | 69.15 | 65.38 | 4.1 % | ✗ |
| ELS_Int | stationary | 70.98 | 51.89 | 47.89 | 43.37 | 1.7 % | ✗ |
| ELS_Int | nonstationary | 69.75 | 50.77 | 41.19 | 38.89 | 1.4 % | ✗ |
| SARSOP | stationary | 32.69 | 25.71 | 20.08 | 17.28 | 0.4 % | ✓ |
| SARSOP | nonstationary | 37.76 | 24.28 | 18.89 | 17.10 | 0.2 % | ✓ |
| PBVI | stationary | 34.88 | 25.35 | 20.61 | 18.06 | 0.3 % | ✓ |
| PBVI | nonstationary | 33.06 | 23.88 | 19.63 | 16.81 | 0.3 % | ✓ |
| SDP_S | stationary | 22.62 | 15.38 | 12.33 | 11.25 | 0.1 % | ✓ |
| SDP_S | nonstationary | 27.43 | 18.43 | 14.67 | 11.88 | 0.3 % | ✓ |
| SDP_NS | stationary | 31.52 | 19.30 | 14.46 | 12.29 | 0.2 % | ✓ |
| SDP_NS | nonstationary | 26.78 | 18.20 | 14.98 | 12.62 | 0.3 % | ✓ |
| MPC | stationary | 27.19 | 18.45 | 13.80 | 12.99 | 0.1 % | ✓ |
| MPC | nonstationary | 24.06 | 17.23 | 15.12 | 13.09 | 0.2 % | ✓ |
| RDM | stationary | 26.39 | 19.84 | 15.64 | 13.56 | 0.2 % | ✓ |
| RDM | nonstationary | 32.76 | 22.95 | 17.99 | 15.69 | 0.2 % | ✓ |
| InfoGap | stationary | 29.07 | 21.52 | 17.99 | 15.51 | 0.3 % | ✓ |
| InfoGap | nonstationary | 28.77 | 20.29 | 16.18 | 13.71 | 0.3 % | ✓ |
| AlwaysRestricted | stationary | 80.39 | 57.82 | 45.67 | 38.32 | 2.2 % | ✗ |
| AlwaysRestricted | nonstationary | 117.20 | 72.66 | 57.37 | 49.01 | 4.6 % | ✗ |
| MyopicEU | stationary | 27.18 | 21.85 | 16.86 | 14.07 | 0.3 % | ✓ |
| MyopicEU | nonstationary | 29.41 | 19.23 | 15.87 | 13.42 | 0.3 % | ✓ |
| SARSOP_Misspec | stationary | 34.45 | 21.89 | 17.90 | 16.33 | 0.2 % | ✓ |
| SARSOP_Misspec | nonstationary | 34.08 | 21.67 | 19.38 | 16.78 | 0.3 % | ✓ |
| SDP_S_Misspec | stationary | 25.02 | 17.66 | 13.81 | 12.44 | 0.1 % | ✓ |
| SDP_S_Misspec | nonstationary | 20.97 | 14.61 | 13.22 | 12.54 | 0.1 % | ✓ |
| ELS_Phil_T | stationary | 23.53 | 20.03 | 17.12 | 15.78 | 0.2 % | ✓ |
| ELS_Phil_T | nonstationary | 27.46 | 20.63 | 16.62 | 15.13 | 0.2 % | ✓ |
| ELS_Int_T | stationary | 30.28 | 21.04 | 19.13 | 16.34 | 0.3 % | ✓ |
| ELS_Int_T | nonstationary | 28.11 | 22.85 | 18.47 | 17.20 | 0.1 % | ✓ |

---

## Notes

- **Convergence:** 26/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


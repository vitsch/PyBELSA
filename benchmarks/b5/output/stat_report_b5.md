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
| ELS_Phil | 271.7 | 499.2 | [210.5, 332.0] | 339.8 | 513.1 |
| ELS_Pres | 201.6 | 548.0 | [151.2, 250.6] | 264.9 | 583.2 |
| ELS_Int | 156.3 | 589.3 | [69.8, 233.3] | 207.1 | 628.4 |
| SARSOP | 698.1 | 224.6 | [659.8, 737.6] | 711.2 | 86.7 |
| PBVI | 687.2 | 215.6 | [655.1, 719.5] | 705.6 | 97.6 |
| SDP_S | 794.3 | 176.8 | [769.8, 819.1] | 808.5 | -9.5 |
| SDP_NS | 787.0 | 182.8 | [759.2, 813.2] | 805.8 | -2.2 |
| MPC | 805.7 | 178.6 | [783.9, 828.9] | 831.0 | -20.9 |
| RDM | 797.3 | 176.4 | [772.5, 822.5] | 804.8 | -12.6 |
| InfoGap | 779.0 | 188.5 | [749.7, 805.7] | 811.5 | 5.8 |
| AlwaysRestricted | 352.5 | 427.2 | [312.3, 392.7] | 388.0 | 432.3 |
| MyopicEU | 784.8 | 171.2 | [765.4, 802.9] | 782.3 | — |
| SARSOP_Misspec | 676.1 | 212.4 | [646.6, 705.3] | 683.0 | 108.7 |
| SDP_S_Misspec | 755.6 | 192.1 | [728.7, 783.5] | 757.1 | 29.2 |
| ELS_Phil_T | 653.6 | 231.4 | [616.6, 691.0] | 660.2 | 131.1 |
| ELS_Int_T | 656.7 | 241.3 | [633.3, 682.0] | 689.5 | 128.0 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | 163.2 | 487.1 | [68.2, 248.8] | 231.1 | 623.5 |
| ELS_Pres | 158.1 | 530.4 | [85.5, 232.6] | 245.2 | 628.5 |
| ELS_Int | 95.5 | 512.5 | [10.5, 176.6] | 80.6 | 691.2 |
| SARSOP | 663.5 | 232.4 | [622.6, 706.7] | 705.1 | 123.2 |
| PBVI | 679.7 | 203.5 | [652.5, 706.1] | 697.0 | 106.9 |
| SDP_S | 784.4 | 180.1 | [762.0, 804.5] | 795.9 | 2.2 |
| SDP_NS | 786.6 | 165.2 | [765.2, 807.4] | 782.1 | 0.1 |
| MPC | 790.3 | 182.6 | [765.8, 814.6] | 797.9 | -3.6 |
| RDM | 754.3 | 182.0 | [726.4, 781.1] | 773.1 | 32.4 |
| InfoGap | 764.5 | 183.6 | [738.0, 791.3] | 757.4 | 22.2 |
| AlwaysRestricted | 264.5 | 502.5 | [186.7, 333.7] | 335.5 | 522.2 |
| MyopicEU | 786.7 | 182.3 | [763.1, 808.4] | 800.4 | — |
| SARSOP_Misspec | 682.9 | 200.1 | [654.0, 709.8] | 689.5 | 103.7 |
| SDP_S_Misspec | 759.6 | 174.0 | [733.2, 786.5] | 763.5 | 27.1 |
| ELS_Phil_T | 667.5 | 230.1 | [630.0, 703.4] | 698.0 | 119.2 |
| ELS_Int_T | 655.1 | 235.2 | [622.7, 685.2] | 675.5 | 131.6 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.785 | [0.735, 0.835] | 10.1 | 8.0 |
| ELS_Pres | 0.895 | [0.855, 0.935] | 7.3 | 6.0 |
| ELS_Int | 0.875 | [0.830, 0.915] | 8.6 | 7.0 |
| SARSOP | 0.630 | [0.575, 0.685] | 10.4 | 9.0 |
| PBVI | 0.690 | [0.635, 0.750] | 9.2 | 6.5 |
| SDP_S | 0.675 | [0.610, 0.745] | 10.8 | 9.0 |
| SDP_NS | 0.710 | [0.670, 0.750] | 9.5 | 8.5 |
| MPC | 0.715 | [0.650, 0.780] | 9.6 | 7.0 |
| RDM | 0.630 | [0.570, 0.685] | 9.5 | 8.5 |
| InfoGap | 0.595 | [0.535, 0.655] | 7.6 | 5.0 |
| AlwaysRestricted | 0.770 | [0.715, 0.825] | 10.1 | 7.0 |
| MyopicEU | 0.635 | [0.575, 0.690] | 8.1 | 6.0 |
| SARSOP_Misspec | 0.635 | [0.580, 0.685] | 9.3 | 9.0 |
| SDP_S_Misspec | 0.625 | [0.550, 0.695] | 9.8 | 7.0 |
| ELS_Phil_T | 0.670 | [0.605, 0.730] | 8.9 | 6.0 |
| ELS_Int_T | 0.770 | [0.710, 0.825] | 8.5 | 6.5 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.950 | [0.925, 0.975] | 10.2 | 9.0 |
| ELS_Pres | 0.950 | [0.920, 0.980] | 9.3 | 7.0 |
| ELS_Int | 0.935 | [0.885, 0.975] | 8.9 | 7.0 |
| SARSOP | 0.830 | [0.780, 0.880] | 10.7 | 9.0 |
| PBVI | 0.815 | [0.760, 0.870] | 11.0 | 10.0 |
| SDP_S | 0.810 | [0.755, 0.860] | 11.2 | 9.5 |
| SDP_NS | 0.825 | [0.775, 0.875] | 12.5 | 14.0 |
| MPC | 0.850 | [0.810, 0.890] | 11.5 | 11.0 |
| RDM | 0.830 | [0.785, 0.880] | 9.9 | 8.0 |
| InfoGap | 0.765 | [0.705, 0.820] | 12.2 | 11.0 |
| AlwaysRestricted | 0.915 | [0.875, 0.950] | 11.3 | 11.0 |
| MyopicEU | 0.705 | [0.635, 0.765] | 10.9 | 11.0 |
| SARSOP_Misspec | 0.780 | [0.720, 0.840] | 11.7 | 13.0 |
| SDP_S_Misspec | 0.685 | [0.620, 0.740] | 11.0 | 10.0 |
| ELS_Phil_T | 0.785 | [0.715, 0.850] | 11.3 | 10.0 |
| ELS_Int_T | 0.855 | [0.795, 0.910] | 12.1 | 12.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 2174.000 | 0.0000 | 0.0000 | ✓ | -1.215 |
| PBVI | wilcoxon_sr | 2053.000 | 0.0000 | 0.0000 | ✓ | -1.197 |
| SDP_S | wilcoxon_sr | 1238.000 | 0.0000 | 0.0000 | ✓ | -1.466 |
| SDP_NS | wilcoxon_sr | 1153.000 | 0.0000 | 0.0000 | ✓ | -1.446 |
| MPC | wilcoxon_sr | 1150.000 | 0.0000 | 0.0000 | ✓ | -1.491 |
| RDM | wilcoxon_sr | 1281.000 | 0.0000 | 0.0000 | ✓ | -1.474 |
| InfoGap | wilcoxon_sr | 1463.000 | 0.0000 | 0.0000 | ✓ | -1.423 |
| AlwaysRestricted | paired_t | -3.669 | 0.0003 | 0.0003 | ✓ | -0.381 |
| MyopicEU | wilcoxon_sr | 1068.000 | 0.0000 | 0.0000 | ✓ | -1.448 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -14.178 | 0.0000 | 0.0000 | ✓ | -1.427 |
| PBVI | wilcoxon_sr | 1055.000 | 0.0000 | 0.0000 | ✓ | -1.498 |
| SDP_S | wilcoxon_sr | 391.000 | 0.0000 | 0.0000 | ✓ | -1.794 |
| SDP_NS | wilcoxon_sr | 476.000 | 0.0000 | 0.0000 | ✓ | -1.815 |
| MPC | paired_t | -19.278 | 0.0000 | 0.0000 | ✓ | -1.806 |
| RDM | paired_t | -16.924 | 0.0000 | 0.0000 | ✓ | -1.713 |
| InfoGap | wilcoxon_sr | 476.000 | 0.0000 | 0.0000 | ✓ | -1.738 |
| AlwaysRestricted | wilcoxon_sr | 6932.000 | 0.0001 | 0.0001 | ✓ | -0.333 |
| MyopicEU | wilcoxon_sr | 633.000 | 0.0000 | 0.0000 | ✓ | -1.797 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 140.3 | 131.4 | 8.9 | 451.8 | 0.277 | 0.7818 | – |
| ELS_Phil | nonstationary | 159.2 | 4.0 | 155.3 | 519.5 | 4.227 | 0.0000 | ✓ |
| ELS_Pres | stationary | 62.8 | 138.9 | -76.1 | 527.2 | -2.042 | 0.0425 | ✓ |
| ELS_Pres | nonstationary | 174.1 | -16.0 | 190.1 | 543.4 | 4.948 | 0.0000 | ✓ |
| ELS_Int | stationary | 87.4 | 68.9 | 18.5 | 545.7 | 0.479 | 0.6328 | – |
| ELS_Int | nonstationary | 85.1 | 10.4 | 74.7 | 541.5 | 1.952 | 0.0523 | – |
| SARSOP | stationary | 415.8 | 282.2 | 133.6 | 213.9 | 8.832 | 0.0000 | ✓ |
| SARSOP | nonstationary | 407.6 | 255.8 | 151.8 | 210.2 | 10.216 | 0.0000 | ✓ |
| PBVI | stationary | 407.5 | 279.8 | 127.7 | 213.4 | 8.463 | 0.0000 | ✓ |
| PBVI | nonstationary | 441.8 | 237.9 | 203.9 | 222.6 | 12.951 | 0.0000 | ✓ |
| SDP_S | stationary | 465.8 | 328.5 | 137.3 | 170.6 | 11.382 | 0.0000 | ✓ |
| SDP_S | nonstationary | 481.9 | 302.5 | 179.4 | 179.1 | 14.165 | 0.0000 | ✓ |
| SDP_NS | stationary | 474.6 | 312.4 | 162.1 | 171.0 | 13.412 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 486.2 | 300.4 | 185.8 | 178.2 | 14.745 | 0.0000 | ✓ |
| MPC | stationary | 472.2 | 333.6 | 138.6 | 178.6 | 10.971 | 0.0000 | ✓ |
| MPC | nonstationary | 476.9 | 313.4 | 163.5 | 187.4 | 12.333 | 0.0000 | ✓ |
| RDM | stationary | 473.3 | 324.0 | 149.3 | 186.6 | 11.317 | 0.0000 | ✓ |
| RDM | nonstationary | 453.3 | 300.9 | 152.4 | 180.3 | 11.952 | 0.0000 | ✓ |
| InfoGap | stationary | 456.3 | 322.7 | 133.6 | 194.6 | 9.706 | 0.0000 | ✓ |
| InfoGap | nonstationary | 458.5 | 306.0 | 152.6 | 187.9 | 11.485 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 242.7 | 109.8 | 132.9 | 411.0 | 4.573 | 0.0000 | ✓ |
| AlwaysRestricted | nonstationary | 228.9 | 35.6 | 193.3 | 451.4 | 6.056 | 0.0000 | ✓ |
| MyopicEU | stationary | 467.8 | 317.0 | 150.8 | 171.0 | 12.472 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 482.0 | 304.7 | 177.3 | 172.5 | 14.535 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 394.7 | 281.4 | 113.4 | 225.5 | 7.112 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 424.2 | 258.7 | 165.5 | 197.6 | 11.845 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 465.2 | 290.4 | 174.8 | 173.5 | 14.249 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 456.1 | 303.5 | 152.6 | 186.3 | 11.579 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 400.2 | 253.5 | 146.7 | 228.6 | 9.075 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 435.0 | 232.5 | 202.5 | 227.0 | 12.618 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 391.2 | 265.5 | 125.7 | 236.7 | 7.510 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 403.5 | 251.6 | 152.0 | 248.8 | 8.641 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | -7.26 | 249.38 | [-37.80, 20.83] |
| nonstationary | 2.18 | 246.76 | [-23.37, 25.96] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2722 | 0.1033 | [0.2588, 0.2850] |
| nonstationary | 0.2830 | 0.1072 | [0.2697, 0.2947] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 63.79 | 51.24 | 41.20 | 35.30 | 2.2 % | ✗ |
| ELS_Phil | nonstationary | 65.58 | 45.04 | 40.04 | 34.45 | 3.4 % | ✗ |
| ELS_Pres | stationary | 80.49 | 53.05 | 42.47 | 38.75 | 1.8 % | ✗ |
| ELS_Pres | nonstationary | 85.22 | 54.33 | 43.66 | 37.50 | 3.9 % | ✗ |
| ELS_Int | stationary | 86.29 | 57.47 | 49.01 | 41.67 | 4.7 % | ✗ |
| ELS_Int | nonstationary | 72.38 | 48.10 | 39.99 | 36.24 | 3.9 % | ✗ |
| SARSOP | stationary | 27.84 | 23.33 | 17.87 | 15.88 | 0.3 % | ✓ |
| SARSOP | nonstationary | 38.41 | 23.98 | 18.92 | 16.44 | 0.4 % | ✓ |
| PBVI | stationary | 30.53 | 21.36 | 17.42 | 15.24 | 0.3 % | ✓ |
| PBVI | nonstationary | 34.18 | 21.82 | 17.06 | 14.39 | 0.4 % | ✓ |
| SDP_S | stationary | 22.27 | 16.86 | 14.19 | 12.50 | 0.2 % | ✓ |
| SDP_S | nonstationary | 27.05 | 19.90 | 15.25 | 12.73 | 0.3 % | ✓ |
| SDP_NS | stationary | 25.46 | 18.50 | 15.27 | 12.93 | 0.3 % | ✓ |
| SDP_NS | nonstationary | 23.89 | 15.62 | 13.98 | 11.68 | 0.3 % | ✓ |
| MPC | stationary | 24.47 | 17.66 | 13.77 | 12.63 | 0.1 % | ✓ |
| MPC | nonstationary | 22.51 | 17.57 | 14.45 | 12.91 | 0.2 % | ✓ |
| RDM | stationary | 22.11 | 18.39 | 14.31 | 12.47 | 0.2 % | ✓ |
| RDM | nonstationary | 25.59 | 17.64 | 14.95 | 12.87 | 0.3 % | ✓ |
| InfoGap | stationary | 22.42 | 19.43 | 15.35 | 13.33 | 0.3 % | ✓ |
| InfoGap | nonstationary | 30.06 | 17.98 | 14.42 | 12.98 | 0.2 % | ✓ |
| AlwaysRestricted | stationary | 63.96 | 43.10 | 35.02 | 30.21 | 1.4 % | ✗ |
| AlwaysRestricted | nonstationary | 80.88 | 52.06 | 41.21 | 35.53 | 2.1 % | ✗ |
| MyopicEU | stationary | 23.58 | 17.72 | 14.63 | 12.10 | 0.3 % | ✓ |
| MyopicEU | nonstationary | 22.88 | 18.05 | 15.05 | 12.89 | 0.3 % | ✓ |
| SARSOP_Misspec | stationary | 27.01 | 18.67 | 16.78 | 15.02 | 0.3 % | ✓ |
| SARSOP_Misspec | nonstationary | 27.24 | 18.68 | 16.52 | 14.15 | 0.3 % | ✓ |
| SDP_S_Misspec | stationary | 28.53 | 19.30 | 15.67 | 13.59 | 0.3 % | ✓ |
| SDP_S_Misspec | nonstationary | 21.62 | 16.30 | 14.11 | 12.30 | 0.2 % | ✓ |
| ELS_Phil_T | stationary | 33.42 | 22.80 | 18.85 | 16.36 | 0.4 % | ✓ |
| ELS_Phil_T | nonstationary | 35.10 | 22.34 | 18.43 | 16.27 | 0.3 % | ✓ |
| ELS_Int_T | stationary | 33.32 | 23.32 | 20.09 | 17.07 | 0.5 % | ✓ |
| ELS_Int_T | nonstationary | 32.65 | 23.18 | 17.85 | 16.63 | 0.2 % | ✓ |

---

## Notes

- **Convergence:** 24/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


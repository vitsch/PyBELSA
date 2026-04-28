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
| ELS_Phil | 96.4 | 701.1 | [-7.6, 203.6] | 225.1 | 728.7 |
| ELS_Pres | 87.0 | 694.4 | [15.0, 162.5] | 188.1 | 738.1 |
| ELS_Int | -17.9 | 785.3 | [-114.2, 71.2] | 136.4 | 842.9 |
| SARSOP | 695.2 | 307.2 | [645.2, 747.1] | 750.1 | 129.8 |
| PBVI | 700.5 | 280.3 | [659.5, 740.0] | 734.6 | 124.6 |
| SDP_S | 837.0 | 200.2 | [813.4, 859.4] | 858.2 | -11.9 |
| SDP_NS | 832.1 | 202.6 | [799.7, 858.3] | 860.7 | -7.0 |
| MPC | 851.7 | 202.0 | [826.5, 877.8] | 876.0 | -26.7 |
| RDM | 846.7 | 195.6 | [820.0, 873.5] | 866.3 | -21.7 |
| InfoGap | 819.4 | 211.4 | [789.9, 847.1] | 844.8 | 5.6 |
| AlwaysRestricted | 334.6 | 498.5 | [286.3, 387.6] | 388.8 | 490.5 |
| MyopicEU | 825.0 | 193.9 | [802.1, 846.4] | 843.1 | — |
| SARSOP_Misspec | 717.1 | 285.0 | [681.5, 753.9] | 746.2 | 107.9 |
| SDP_S_Misspec | 788.5 | 211.2 | [753.9, 822.4] | 788.0 | 36.5 |
| ELS_Phil_T | 652.6 | 314.1 | [600.2, 703.2] | 686.8 | 172.5 |
| ELS_Int_T | 639.7 | 349.7 | [594.0, 683.9] | 702.1 | 185.3 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | -63.4 | 688.5 | [-202.2, 55.0] | 57.7 | 866.1 |
| ELS_Pres | 65.4 | 674.7 | [-21.8, 158.0] | 171.8 | 737.2 |
| ELS_Int | -51.8 | 671.0 | [-169.1, 56.3] | -12.8 | 854.5 |
| SARSOP | 671.3 | 314.1 | [625.1, 716.7] | 701.3 | 131.4 |
| PBVI | 693.7 | 265.2 | [658.1, 729.7] | 736.2 | 108.9 |
| SDP_S | 825.6 | 208.2 | [796.3, 852.5] | 843.4 | -23.0 |
| SDP_NS | 819.6 | 189.3 | [799.9, 839.6] | 817.2 | -16.9 |
| MPC | 821.3 | 218.2 | [784.5, 858.7] | 841.4 | -18.7 |
| RDM | 810.2 | 192.3 | [785.7, 834.2] | 830.9 | -7.5 |
| InfoGap | 796.1 | 216.2 | [765.2, 824.2] | 801.2 | 6.5 |
| AlwaysRestricted | 241.6 | 571.4 | [158.6, 323.2] | 341.5 | 561.0 |
| MyopicEU | 802.7 | 210.7 | [778.9, 825.5] | 810.2 | — |
| SARSOP_Misspec | 703.1 | 254.8 | [672.3, 733.6] | 726.1 | 99.6 |
| SDP_S_Misspec | 789.2 | 194.8 | [758.5, 819.1] | 804.0 | 13.5 |
| ELS_Phil_T | 657.4 | 290.7 | [615.3, 700.1] | 699.4 | 145.2 |
| ELS_Int_T | 649.8 | 314.8 | [608.4, 691.5] | 684.3 | 152.9 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.845 | [0.790, 0.900] | 10.1 | 9.0 |
| ELS_Pres | 0.920 | [0.875, 0.955] | 7.3 | 6.0 |
| ELS_Int | 0.870 | [0.825, 0.910] | 8.4 | 7.0 |
| SARSOP | 0.695 | [0.635, 0.755] | 9.9 | 9.0 |
| PBVI | 0.755 | [0.705, 0.805] | 9.4 | 7.0 |
| SDP_S | 0.740 | [0.675, 0.800] | 10.3 | 8.0 |
| SDP_NS | 0.745 | [0.690, 0.795] | 9.4 | 8.0 |
| MPC | 0.740 | [0.675, 0.800] | 9.5 | 8.0 |
| RDM | 0.700 | [0.650, 0.750] | 9.2 | 8.0 |
| InfoGap | 0.645 | [0.590, 0.705] | 8.7 | 6.0 |
| AlwaysRestricted | 0.760 | [0.705, 0.810] | 9.1 | 7.0 |
| MyopicEU | 0.660 | [0.610, 0.710] | 8.0 | 5.0 |
| SARSOP_Misspec | 0.670 | [0.620, 0.715] | 8.6 | 7.0 |
| SDP_S_Misspec | 0.690 | [0.625, 0.755] | 9.6 | 7.0 |
| ELS_Phil_T | 0.775 | [0.715, 0.835] | 9.1 | 7.0 |
| ELS_Int_T | 0.805 | [0.760, 0.845] | 8.4 | 6.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.950 | [0.930, 0.970] | 9.6 | 9.0 |
| ELS_Pres | 0.950 | [0.920, 0.980] | 9.0 | 7.5 |
| ELS_Int | 0.950 | [0.915, 0.985] | 9.7 | 8.0 |
| SARSOP | 0.860 | [0.810, 0.910] | 10.5 | 9.5 |
| PBVI | 0.825 | [0.770, 0.880] | 10.4 | 9.0 |
| SDP_S | 0.870 | [0.815, 0.920] | 10.9 | 10.0 |
| SDP_NS | 0.840 | [0.795, 0.880] | 11.8 | 11.0 |
| MPC | 0.845 | [0.805, 0.875] | 11.3 | 10.0 |
| RDM | 0.835 | [0.800, 0.870] | 9.2 | 7.0 |
| InfoGap | 0.800 | [0.745, 0.855] | 11.3 | 10.0 |
| AlwaysRestricted | 0.905 | [0.865, 0.945] | 10.9 | 10.0 |
| MyopicEU | 0.790 | [0.730, 0.840] | 10.6 | 10.0 |
| SARSOP_Misspec | 0.835 | [0.775, 0.890] | 10.9 | 11.0 |
| SDP_S_Misspec | 0.745 | [0.685, 0.805] | 10.8 | 11.0 |
| ELS_Phil_T | 0.845 | [0.785, 0.900] | 10.2 | 9.0 |
| ELS_Int_T | 0.855 | [0.800, 0.905] | 11.6 | 12.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 2156.000 | 0.0000 | 0.0000 | ✓ | -1.196 |
| PBVI | wilcoxon_sr | 1892.000 | 0.0000 | 0.0000 | ✓ | -1.218 |
| SDP_S | wilcoxon_sr | 816.000 | 0.0000 | 0.0000 | ✓ | -1.492 |
| SDP_NS | wilcoxon_sr | 875.000 | 0.0000 | 0.0000 | ✓ | -1.482 |
| MPC | wilcoxon_sr | 733.000 | 0.0000 | 0.0000 | ✓ | -1.517 |
| RDM | wilcoxon_sr | 884.000 | 0.0000 | 0.0000 | ✓ | -1.511 |
| InfoGap | wilcoxon_sr | 1093.000 | 0.0000 | 0.0000 | ✓ | -1.456 |
| AlwaysRestricted | wilcoxon_sr | 6575.000 | 0.0000 | 0.0000 | ✓ | -0.536 |
| MyopicEU | wilcoxon_sr | 757.000 | 0.0000 | 0.0000 | ✓ | -1.474 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | paired_t | -13.442 | 0.0000 | 0.0000 | ✓ | -1.380 |
| PBVI | paired_t | -14.969 | 0.0000 | 0.0000 | ✓ | -1.461 |
| SDP_S | wilcoxon_sr | 324.000 | 0.0000 | 0.0000 | ✓ | -1.766 |
| SDP_NS | wilcoxon_sr | 454.000 | 0.0000 | 0.0000 | ✓ | -1.768 |
| MPC | wilcoxon_sr | 274.000 | 0.0000 | 0.0000 | ✓ | -1.750 |
| RDM | wilcoxon_sr | 540.000 | 0.0000 | 0.0000 | ✓ | -1.747 |
| InfoGap | wilcoxon_sr | 426.000 | 0.0000 | 0.0000 | ✓ | -1.701 |
| AlwaysRestricted | paired_t | -4.749 | 0.0000 | 0.0000 | ✓ | -0.471 |
| MyopicEU | wilcoxon_sr | 669.000 | 0.0000 | 0.0000 | ✓ | -1.718 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | 78.3 | 18.1 | 60.2 | 671.8 | 1.267 | 0.2066 | – |
| ELS_Phil | nonstationary | 50.2 | -113.6 | 163.8 | 826.0 | 2.804 | 0.0056 | ✓ |
| ELS_Pres | stationary | -19.6 | 106.5 | -126.1 | 714.9 | -2.495 | 0.0134 | ✓ |
| ELS_Pres | nonstationary | 153.3 | -87.8 | 241.1 | 713.8 | 4.776 | 0.0000 | ✓ |
| ELS_Int | stationary | -30.4 | 12.5 | -42.9 | 813.9 | -0.745 | 0.4570 | – |
| ELS_Int | nonstationary | 33.2 | -85.0 | 118.2 | 773.1 | 2.162 | 0.0318 | ✓ |
| SARSOP | stationary | 412.7 | 282.5 | 130.2 | 300.4 | 6.129 | 0.0000 | ✓ |
| SARSOP | nonstationary | 422.8 | 248.5 | 174.2 | 290.6 | 8.480 | 0.0000 | ✓ |
| PBVI | stationary | 412.4 | 288.1 | 124.3 | 279.6 | 6.286 | 0.0000 | ✓ |
| PBVI | nonstationary | 450.1 | 243.7 | 206.4 | 290.3 | 10.054 | 0.0000 | ✓ |
| SDP_S | stationary | 494.9 | 342.1 | 152.8 | 212.8 | 10.156 | 0.0000 | ✓ |
| SDP_S | nonstationary | 516.8 | 308.8 | 208.0 | 216.1 | 13.613 | 0.0000 | ✓ |
| SDP_NS | stationary | 506.2 | 325.8 | 180.4 | 206.8 | 12.335 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 509.0 | 310.6 | 198.4 | 200.6 | 13.989 | 0.0000 | ✓ |
| MPC | stationary | 510.1 | 341.6 | 168.5 | 190.0 | 12.543 | 0.0000 | ✓ |
| MPC | nonstationary | 498.9 | 322.4 | 176.5 | 223.6 | 11.161 | 0.0000 | ✓ |
| RDM | stationary | 502.3 | 344.4 | 157.9 | 201.5 | 11.083 | 0.0000 | ✓ |
| RDM | nonstationary | 492.7 | 317.5 | 175.2 | 204.3 | 12.130 | 0.0000 | ✓ |
| InfoGap | stationary | 483.4 | 336.0 | 147.4 | 222.0 | 9.387 | 0.0000 | ✓ |
| InfoGap | nonstationary | 485.0 | 311.1 | 173.9 | 219.0 | 11.228 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 235.2 | 99.3 | 135.9 | 481.3 | 3.993 | 0.0001 | ✓ |
| AlwaysRestricted | nonstationary | 213.6 | 28.1 | 185.5 | 525.5 | 4.994 | 0.0000 | ✓ |
| MyopicEU | stationary | 501.6 | 323.5 | 178.1 | 213.3 | 11.810 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 495.1 | 307.6 | 187.5 | 212.2 | 12.495 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 422.8 | 294.3 | 128.5 | 277.9 | 6.540 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 448.9 | 254.2 | 194.7 | 257.5 | 10.691 | 0.0000 | ✓ |
| SDP_S_Misspec | stationary | 491.2 | 297.4 | 193.8 | 191.9 | 14.287 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 482.2 | 307.0 | 175.3 | 208.0 | 11.915 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 385.1 | 267.5 | 117.6 | 335.8 | 4.953 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 442.5 | 214.9 | 227.6 | 302.1 | 10.656 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 389.4 | 250.4 | 139.0 | 312.3 | 6.292 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 420.1 | 229.7 | 190.4 | 304.0 | 8.857 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | -4.91 | 284.62 | [-42.47, 29.41] |
| nonstationary | -6.09 | 290.76 | [-41.02, 29.49] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.4125 | 0.1277 | [0.3973, 0.4270] |
| nonstationary | 0.4225 | 0.1386 | [0.4022, 0.4425] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 85.80 | 71.59 | 57.98 | 49.57 | 8.7 % | ✗ |
| ELS_Phil | nonstationary | 81.41 | 63.32 | 56.90 | 48.68 | 13.0 % | ✗ |
| ELS_Pres | stationary | 116.16 | 72.21 | 55.92 | 49.10 | 7.8 % | ✗ |
| ELS_Pres | nonstationary | 99.68 | 63.63 | 54.11 | 47.71 | 9.8 % | ✗ |
| ELS_Int | stationary | 106.32 | 76.76 | 65.40 | 55.53 | 55.1 % | ✗ |
| ELS_Int | nonstationary | 94.45 | 62.56 | 51.83 | 47.45 | 8.5 % | ✗ |
| SARSOP | stationary | 45.29 | 33.35 | 25.38 | 21.72 | 0.5 % | ✓ |
| SARSOP | nonstationary | 40.75 | 32.16 | 26.36 | 22.21 | 0.6 % | ✓ |
| PBVI | stationary | 34.86 | 28.20 | 21.99 | 19.82 | 0.3 % | ✓ |
| PBVI | nonstationary | 33.85 | 23.79 | 20.12 | 18.75 | 0.2 % | ✓ |
| SDP_S | stationary | 31.17 | 21.27 | 17.08 | 14.16 | 0.3 % | ✓ |
| SDP_S | nonstationary | 26.02 | 21.81 | 17.60 | 14.72 | 0.3 % | ✓ |
| SDP_NS | stationary | 32.37 | 20.88 | 16.36 | 14.32 | 0.2 % | ✓ |
| SDP_NS | nonstationary | 29.89 | 19.28 | 15.76 | 13.38 | 0.3 % | ✓ |
| MPC | stationary | 24.87 | 20.05 | 16.38 | 14.28 | 0.2 % | ✓ |
| MPC | nonstationary | 22.33 | 20.47 | 16.80 | 15.43 | 0.2 % | ✓ |
| RDM | stationary | 26.11 | 18.60 | 16.22 | 13.83 | 0.3 % | ✓ |
| RDM | nonstationary | 31.58 | 20.75 | 15.75 | 13.60 | 0.3 % | ✓ |
| InfoGap | stationary | 24.16 | 19.73 | 16.51 | 14.95 | 0.2 % | ✓ |
| InfoGap | nonstationary | 30.69 | 21.42 | 17.06 | 15.29 | 0.2 % | ✓ |
| AlwaysRestricted | stationary | 76.61 | 50.25 | 41.08 | 35.25 | 1.7 % | ✗ |
| AlwaysRestricted | nonstationary | 92.22 | 59.45 | 47.45 | 40.40 | 2.9 % | ✗ |
| MyopicEU | stationary | 26.63 | 20.20 | 15.82 | 13.71 | 0.3 % | ✓ |
| MyopicEU | nonstationary | 27.48 | 19.71 | 16.76 | 14.90 | 0.2 % | ✓ |
| SARSOP_Misspec | stationary | 41.61 | 28.98 | 23.24 | 20.15 | 0.4 % | ✓ |
| SARSOP_Misspec | nonstationary | 33.41 | 25.42 | 21.55 | 18.02 | 0.5 % | ✓ |
| SDP_S_Misspec | stationary | 32.94 | 21.96 | 17.32 | 14.93 | 0.3 % | ✓ |
| SDP_S_Misspec | nonstationary | 27.75 | 18.66 | 15.62 | 13.77 | 0.2 % | ✓ |
| ELS_Phil_T | stationary | 47.52 | 33.62 | 26.60 | 22.21 | 0.7 % | ✓ |
| ELS_Phil_T | nonstationary | 42.17 | 28.27 | 24.28 | 20.56 | 0.6 % | ✓ |
| ELS_Int_T | stationary | 52.63 | 36.24 | 30.16 | 24.73 | 0.8 % | ✓ |
| ELS_Int_T | nonstationary | 47.24 | 29.25 | 25.28 | 22.26 | 0.5 % | ✓ |

---

## Notes

- **Convergence:** 24/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


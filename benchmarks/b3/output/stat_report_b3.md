# Benchmark 3 — Statistical Report
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
| ELS_Phil | -140.4 | 731.6 | [-239.4, -42.3] | -25.0 | 802.7 |
| ELS_Pres | -166.2 | 932.5 | [-312.2, -42.0] | -19.2 | 828.6 |
| ELS_Int | -134.1 | 833.2 | [-252.8, -22.2] | 6.2 | 796.4 |
| SARSOP | 528.2 | 310.4 | [494.5, 565.7] | 518.4 | 134.1 |
| PBVI | 572.3 | 343.3 | [523.9, 621.4] | 557.8 | 90.1 |
| SDP_S | 663.8 | 270.9 | [624.9, 701.2] | 614.6 | -1.4 |
| SDP_NS | 689.3 | 291.5 | [652.3, 723.2] | 666.9 | -27.0 |
| MPC | 651.9 | 270.0 | [614.1, 696.1] | 637.9 | 10.5 |
| RDM | 673.3 | 271.0 | [645.8, 701.2] | 639.0 | -10.9 |
| InfoGap | 703.1 | 281.9 | [670.6, 736.4] | 674.7 | -40.7 |
| AlwaysRestricted | 280.9 | 429.8 | [231.5, 329.0] | 235.1 | 381.5 |
| MyopicEU | 662.3 | 268.6 | [627.5, 700.9] | 647.0 | — |
| SARSOP_Misspec | 571.9 | 332.9 | [519.7, 619.4] | 561.3 | 90.5 |
| SDP_S_Misspec | 695.8 | 288.0 | [660.6, 733.1] | 666.2 | -33.5 |
| ELS_Phil_T | 594.1 | 312.2 | [569.5, 620.8] | 563.5 | 68.2 |
| ELS_Int_T | 606.3 | 307.0 | [577.4, 637.6] | 589.4 | 56.0 |

### Condition: nonstationary

| Method | Mean | SD | 95 % CI | Median | Regret (mean) |
|--------|------|-----|---------|--------|---------------|
| ELS_Phil | -82.3 | 809.6 | [-218.4, 47.3] | 33.5 | 805.7 |
| ELS_Pres | -240.9 | 926.4 | [-389.3, -101.5] | -21.4 | 964.2 |
| ELS_Int | -222.8 | 799.2 | [-316.3, -123.3] | -201.2 | 946.2 |
| SARSOP | 556.4 | 342.3 | [525.3, 591.7] | 528.2 | 167.0 |
| PBVI | 565.6 | 353.4 | [522.1, 608.7] | 523.0 | 157.8 |
| SDP_S | 714.1 | 293.7 | [677.0, 750.6] | 714.9 | 9.3 |
| SDP_NS | 703.5 | 291.1 | [671.0, 734.7] | 668.5 | 19.9 |
| MPC | 687.7 | 260.0 | [666.2, 712.3] | 650.7 | 35.7 |
| RDM | 720.0 | 280.9 | [686.8, 752.2] | 683.9 | 3.4 |
| InfoGap | 700.1 | 298.2 | [666.7, 732.1] | 660.0 | 23.2 |
| AlwaysRestricted | 279.9 | 390.8 | [225.2, 330.5] | 238.0 | 443.5 |
| MyopicEU | 723.4 | 283.8 | [691.4, 754.4] | 700.9 | — |
| SARSOP_Misspec | 539.4 | 350.1 | [493.6, 583.7] | 566.3 | 184.0 |
| SDP_S_Misspec | 694.1 | 287.8 | [644.1, 742.4] | 692.5 | 29.3 |
| ELS_Phil_T | 618.9 | 345.9 | [567.8, 674.5] | 587.5 | 104.5 |
| ELS_Int_T | 612.1 | 321.0 | [569.5, 656.0] | 582.5 | 111.2 |

## Table 2 — P_fail and MTTF

P_fail = fraction of episodes reaching θ₅. MTTF = mean time to first failure (steps); NaN-excluded.

### Condition: stationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.875 | [0.830, 0.915] | 10.4 | 9.0 |
| ELS_Pres | 0.870 | [0.825, 0.915] | 8.2 | 7.0 |
| ELS_Int | 0.875 | [0.830, 0.920] | 8.9 | 8.0 |
| SARSOP | 0.730 | [0.665, 0.785] | 9.8 | 7.0 |
| PBVI | 0.710 | [0.650, 0.765] | 8.6 | 7.0 |
| SDP_S | 0.545 | [0.475, 0.610] | 9.3 | 7.0 |
| SDP_NS | 0.595 | [0.525, 0.660] | 8.3 | 7.0 |
| MPC | 0.620 | [0.560, 0.680] | 9.8 | 7.0 |
| RDM | 0.545 | [0.495, 0.590] | 8.1 | 5.0 |
| InfoGap | 0.620 | [0.555, 0.685] | 8.5 | 5.5 |
| AlwaysRestricted | 0.530 | [0.475, 0.585] | 8.7 | 5.0 |
| MyopicEU | 0.540 | [0.470, 0.605] | 6.9 | 2.5 |
| SARSOP_Misspec | 0.730 | [0.680, 0.780] | 9.0 | 7.0 |
| SDP_S_Misspec | 0.575 | [0.510, 0.635] | 9.1 | 6.0 |
| ELS_Phil_T | 0.690 | [0.625, 0.750] | 8.8 | 6.0 |
| ELS_Int_T | 0.780 | [0.735, 0.830] | 9.3 | 6.0 |

### Condition: nonstationary

| Method | P_fail | P_fail 95 % CI | MTTF (mean) | MTTF (median) |
|--------|--------|----------------|-------------|---------------|
| ELS_Phil | 0.920 | [0.880, 0.955] | 9.9 | 8.0 |
| ELS_Pres | 0.950 | [0.915, 0.980] | 9.7 | 8.0 |
| ELS_Int | 0.925 | [0.885, 0.960] | 10.3 | 10.0 |
| SARSOP | 0.860 | [0.805, 0.915] | 9.5 | 9.0 |
| PBVI | 0.830 | [0.785, 0.870] | 10.3 | 8.0 |
| SDP_S | 0.745 | [0.685, 0.805] | 11.6 | 10.0 |
| SDP_NS | 0.660 | [0.595, 0.725] | 11.5 | 11.0 |
| MPC | 0.745 | [0.695, 0.790] | 12.0 | 13.0 |
| RDM | 0.735 | [0.695, 0.775] | 9.5 | 7.0 |
| InfoGap | 0.770 | [0.710, 0.830] | 11.6 | 11.0 |
| AlwaysRestricted | 0.690 | [0.635, 0.745] | 10.5 | 8.5 |
| MyopicEU | 0.690 | [0.635, 0.745] | 10.9 | 6.0 |
| SARSOP_Misspec | 0.840 | [0.775, 0.900] | 11.3 | 10.0 |
| SDP_S_Misspec | 0.690 | [0.630, 0.750] | 10.4 | 9.0 |
| ELS_Phil_T | 0.860 | [0.805, 0.910] | 9.8 | 8.0 |
| ELS_Int_T | 0.835 | [0.785, 0.885] | 12.0 | 13.0 |

## Table 3 — Pairwise Tests: ELS_Int vs Baselines (U_cum)

H₀: E[U_cum(ELS_Int)] = E[U_cum(baseline)].  
Test: paired t (SW p ≥ 0.05) or Wilcoxon signed-rank (SW p < 0.05).  
Holm–Bonferroni correction applied within each condition (9 comparisons).  
Cohen's d: positive = ELS_Int > baseline.

### Condition: stationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 2616.000 | 0.0000 | 0.0000 | ✓ | -1.053 |
| PBVI | wilcoxon_sr | 2519.000 | 0.0000 | 0.0000 | ✓ | -1.109 |
| SDP_S | wilcoxon_sr | 1739.000 | 0.0000 | 0.0000 | ✓ | -1.288 |
| SDP_NS | wilcoxon_sr | 1310.000 | 0.0000 | 0.0000 | ✓ | -1.319 |
| MPC | wilcoxon_sr | 1971.000 | 0.0000 | 0.0000 | ✓ | -1.269 |
| RDM | wilcoxon_sr | 1664.000 | 0.0000 | 0.0000 | ✓ | -1.303 |
| InfoGap | wilcoxon_sr | 1400.000 | 0.0000 | 0.0000 | ✓ | -1.346 |
| AlwaysRestricted | wilcoxon_sr | 5372.000 | 0.0000 | 0.0000 | ✓ | -0.626 |
| MyopicEU | wilcoxon_sr | 1627.000 | 0.0000 | 0.0000 | ✓ | -1.287 |

### Condition: nonstationary

| Baseline | Test | Statistic | p (raw) | p (adj) | Reject H₀ | Cohen's d |
|----------|------|-----------|---------|---------|-----------|-----------|
| SARSOP | wilcoxon_sr | 2075.000 | 0.0000 | 0.0000 | ✓ | -1.268 |
| PBVI | wilcoxon_sr | 2006.000 | 0.0000 | 0.0000 | ✓ | -1.276 |
| SDP_S | wilcoxon_sr | 985.000 | 0.0000 | 0.0000 | ✓ | -1.556 |
| SDP_NS | wilcoxon_sr | 875.000 | 0.0000 | 0.0000 | ✓ | -1.540 |
| MPC | paired_t | -14.908 | 0.0000 | 0.0000 | ✓ | -1.532 |
| RDM | wilcoxon_sr | 1097.000 | 0.0000 | 0.0000 | ✓ | -1.574 |
| InfoGap | wilcoxon_sr | 1037.000 | 0.0000 | 0.0000 | ✓ | -1.530 |
| AlwaysRestricted | paired_t | -7.922 | 0.0000 | 0.0000 | ✓ | -0.799 |
| MyopicEU | wilcoxon_sr | 838.000 | 0.0000 | 0.0000 | ✓ | -1.578 |

## Table 4 — Non-Stationarity Analysis (ΔU = U_cum_A − U_cum_B)

H₀: E[ΔU] = 0 (no regime effect). Paired t-test per method × condition.  
U_cum_A = discounted reward steps 0–29; U_cum_B = steps 30–59 (same γ^t).  
Positive ΔU ⟹ performance degrades after the climate shift at t = 30.

| Method | Condition | U_cum_A | U_cum_B | ΔU (mean) | ΔU (SD) | t | p | Reject |
|--------|-----------|---------|---------|-----------|---------|---|---|--------|
| ELS_Phil | stationary | -12.2 | -128.2 | 116.0 | 808.7 | 2.028 | 0.0439 | ✓ |
| ELS_Phil | nonstationary | 85.7 | -168.0 | 253.6 | 925.8 | 3.874 | 0.0001 | ✓ |
| ELS_Pres | stationary | -53.2 | -113.0 | 59.8 | 976.3 | 0.866 | 0.3873 | – |
| ELS_Pres | nonstationary | -24.7 | -216.2 | 191.5 | 923.4 | 2.933 | 0.0038 | ✓ |
| ELS_Int | stationary | 65.3 | -199.4 | 264.7 | 846.4 | 4.424 | 0.0000 | ✓ |
| ELS_Int | nonstationary | -26.7 | -196.1 | 169.4 | 946.5 | 2.531 | 0.0121 | ✓ |
| SARSOP | stationary | 318.1 | 210.1 | 108.0 | 298.6 | 5.117 | 0.0000 | ✓ |
| SARSOP | nonstationary | 315.3 | 241.1 | 74.2 | 337.9 | 3.105 | 0.0022 | ✓ |
| PBVI | stationary | 348.5 | 223.8 | 124.7 | 319.7 | 5.516 | 0.0000 | ✓ |
| PBVI | nonstationary | 341.7 | 224.0 | 117.7 | 331.1 | 5.027 | 0.0000 | ✓ |
| SDP_S | stationary | 406.4 | 257.3 | 149.1 | 242.8 | 8.685 | 0.0000 | ✓ |
| SDP_S | nonstationary | 443.3 | 270.8 | 172.5 | 271.3 | 8.990 | 0.0000 | ✓ |
| SDP_NS | stationary | 427.2 | 262.2 | 165.0 | 251.9 | 9.265 | 0.0000 | ✓ |
| SDP_NS | nonstationary | 434.0 | 269.5 | 164.5 | 276.4 | 8.418 | 0.0000 | ✓ |
| MPC | stationary | 394.9 | 257.0 | 137.8 | 253.3 | 7.696 | 0.0000 | ✓ |
| MPC | nonstationary | 419.2 | 268.5 | 150.7 | 239.2 | 8.910 | 0.0000 | ✓ |
| RDM | stationary | 414.0 | 259.3 | 154.7 | 258.6 | 8.462 | 0.0000 | ✓ |
| RDM | nonstationary | 443.9 | 276.1 | 167.8 | 306.4 | 7.746 | 0.0000 | ✓ |
| InfoGap | stationary | 418.5 | 284.6 | 133.9 | 275.2 | 6.879 | 0.0000 | ✓ |
| InfoGap | nonstationary | 433.3 | 266.8 | 166.5 | 283.6 | 8.305 | 0.0000 | ✓ |
| AlwaysRestricted | stationary | 186.3 | 94.6 | 91.7 | 337.1 | 3.848 | 0.0002 | ✓ |
| AlwaysRestricted | nonstationary | 154.9 | 125.0 | 29.9 | 349.5 | 1.211 | 0.2274 | – |
| MyopicEU | stationary | 407.7 | 254.7 | 153.0 | 256.0 | 8.454 | 0.0000 | ✓ |
| MyopicEU | nonstationary | 436.0 | 287.3 | 148.7 | 275.7 | 7.627 | 0.0000 | ✓ |
| SARSOP_Misspec | stationary | 350.4 | 221.5 | 128.9 | 310.7 | 5.868 | 0.0000 | ✓ |
| SARSOP_Misspec | nonstationary | 314.3 | 225.1 | 89.2 | 335.7 | 3.760 | 0.0002 | ✓ |
| SDP_S_Misspec | stationary | 435.2 | 260.7 | 174.5 | 267.7 | 9.218 | 0.0000 | ✓ |
| SDP_S_Misspec | nonstationary | 416.5 | 277.5 | 139.0 | 254.5 | 7.722 | 0.0000 | ✓ |
| ELS_Phil_T | stationary | 353.7 | 240.4 | 113.3 | 282.5 | 5.675 | 0.0000 | ✓ |
| ELS_Phil_T | nonstationary | 382.5 | 236.3 | 146.2 | 344.8 | 5.996 | 0.0000 | ✓ |
| ELS_Int_T | stationary | 391.1 | 215.2 | 175.9 | 322.9 | 7.704 | 0.0000 | ✓ |
| ELS_Int_T | nonstationary | 367.5 | 244.6 | 122.9 | 319.5 | 5.440 | 0.0000 | ✓ |

## Table 5 — Economic Value of Information (EVOI)

EVOI = E[U_cum(SDP_NS)] − E[U_cum(SDP_S)]. Positive EVOI = online regime detection adds value.

| Condition | EVOI (mean) | EVOI (SD) | 95 % CI |
|-----------|------------|-----------|---------|
| stationary | 25.55 | 397.69 | [-28.06, 77.36] |
| nonstationary | -10.58 | 414.61 | [-53.59, 33.12] |

## Table 6 — ELS_Int Philosophical Activation (f_phil)

f_phil = fraction of steps where the philosophical selector (SR4) was chosen.  
Expected ≈ 5 % once entropy collapses (α_t → α_max = 0.95).

| Condition | f_phil (mean) | SD | 95 % CI |
|-----------|--------------|-----|---------|
| stationary | 0.2837 | 0.0908 | [0.2743, 0.2935] |
| nonstationary | 0.2933 | 0.0983 | [0.2835, 0.3040] |

## Table 7 — Convergence Diagnostic (U_cum SE vs N_MC)

SE stabilised if |SE(200) − SE(150)| / SE(200) < 1 %.

| Method | Cond | SE(50) | SE(100) | SE(150) | SE(200) | Δ SE % | Converged |
|--------|------|--------|---------|---------|---------|--------|-----------|
| ELS_Phil | stationary | 90.72 | 69.18 | 59.37 | 51.73 | 5.4 % | ✗ |
| ELS_Phil | nonstationary | 115.23 | 80.71 | 67.05 | 57.25 | 11.9 % | ✗ |
| ELS_Pres | stationary | 111.68 | 79.32 | 66.90 | 65.94 | 0.6 % | ✓ |
| ELS_Pres | nonstationary | 139.33 | 98.84 | 80.10 | 65.51 | 6.1 % | ✗ |
| ELS_Int | stationary | 117.75 | 78.10 | 68.58 | 58.91 | 7.2 % | ✗ |
| ELS_Int | nonstationary | 107.26 | 72.59 | 61.41 | 56.51 | 2.2 % | ✗ |
| SARSOP | stationary | 41.25 | 33.77 | 25.94 | 21.95 | 0.8 % | ✓ |
| SARSOP | nonstationary | 51.70 | 34.00 | 28.01 | 24.21 | 0.7 % | ✓ |
| PBVI | stationary | 52.02 | 35.79 | 29.76 | 24.28 | 1.0 % | ✓ |
| PBVI | nonstationary | 55.15 | 37.40 | 29.06 | 24.99 | 0.7 % | ✓ |
| SDP_S | stationary | 42.96 | 28.44 | 23.05 | 19.16 | 0.6 % | ✓ |
| SDP_S | nonstationary | 42.50 | 29.83 | 24.56 | 20.77 | 0.5 % | ✓ |
| SDP_NS | stationary | 41.19 | 29.72 | 24.45 | 20.61 | 0.6 % | ✓ |
| SDP_NS | nonstationary | 42.73 | 28.08 | 24.51 | 20.58 | 0.6 % | ✓ |
| MPC | stationary | 32.33 | 25.46 | 21.00 | 19.09 | 0.3 % | ✓ |
| MPC | nonstationary | 36.17 | 25.67 | 21.63 | 18.38 | 0.5 % | ✓ |
| RDM | stationary | 37.65 | 29.98 | 23.30 | 19.17 | 0.6 % | ✓ |
| RDM | nonstationary | 38.04 | 27.53 | 21.97 | 19.86 | 0.3 % | ✓ |
| InfoGap | stationary | 40.29 | 27.89 | 22.40 | 19.93 | 0.4 % | ✓ |
| InfoGap | nonstationary | 45.12 | 32.44 | 24.40 | 21.09 | 0.5 % | ✓ |
| AlwaysRestricted | stationary | 59.67 | 40.42 | 34.95 | 30.39 | 1.6 % | ✗ |
| AlwaysRestricted | nonstationary | 52.82 | 37.55 | 30.48 | 27.64 | 1.0 % | ✗ |
| MyopicEU | stationary | 40.25 | 26.73 | 22.02 | 18.99 | 0.5 % | ✓ |
| MyopicEU | nonstationary | 39.84 | 26.18 | 22.65 | 20.07 | 0.4 % | ✓ |
| SARSOP_Misspec | stationary | 44.01 | 32.47 | 27.83 | 23.54 | 0.7 % | ✓ |
| SARSOP_Misspec | nonstationary | 46.87 | 33.98 | 29.46 | 24.76 | 0.9 % | ✓ |
| SDP_S_Misspec | stationary | 38.72 | 27.00 | 22.94 | 20.36 | 0.4 % | ✓ |
| SDP_S_Misspec | nonstationary | 45.35 | 29.77 | 24.11 | 20.35 | 0.5 % | ✓ |
| ELS_Phil_T | stationary | 38.99 | 31.09 | 25.73 | 22.08 | 0.6 % | ✓ |
| ELS_Phil_T | nonstationary | 39.71 | 29.16 | 25.29 | 24.46 | 0.1 % | ✓ |
| ELS_Int_T | stationary | 43.67 | 29.26 | 24.52 | 21.71 | 0.5 % | ✓ |
| ELS_Int_T | nonstationary | 37.83 | 33.42 | 27.04 | 22.70 | 0.7 % | ✓ |

---

## Notes

- **Convergence:** 25/32 method–condition pairs converged (SE change < 1 % from N=150 to N=200).
- **SDP_S / SDP_NS:** MC benchmark uses vectorised depth-2 lookahead (`_SDPSVec`, `_SDPNSVec` in `run_benchmark.py`). Smoke-test values (depth-3) differ; see `summary_step_4.md`.
- **ELS static belief:** ELS methods use static Bayesian updates (no Markovian predict step). The U_cum gap vs SARSOP/PBVI is expected and reflects the epistemic-humility design principle.
- **MTTF caveat:** MTTF is conditional on at least one failure episode; all NaN episodes (no failure) are excluded from the mean/median.


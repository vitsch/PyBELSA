# Adaptive w Trade-off Analysis — Benchmark 6 (Karst Aquifer)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b6.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 37.1 | 748.6 | 0.860 |
| ELS_Phil_T | nonstationary | 0.00 | 58.0 | 672.0 | 0.945 |
| ELS_Int_T | stationary | 0.00 | 71.5 | 741.0 | 0.900 |
| ELS_Int_T | nonstationary | 0.00 | -64.0 | 703.5 | 0.975 |
| ELS_Phil_T | stationary | 0.25 | 625.4 | 316.5 | 0.750 |
| ELS_Phil_T | nonstationary | 0.25 | 565.5 | 342.6 | 0.835 |
| ELS_Int_T | stationary | 0.25 | 657.7 | 316.0 | 0.790 |
| ELS_Int_T | nonstationary | 0.25 | 561.7 | 339.1 | 0.880 |
| ELS_Phil_T | stationary | 0.50 | 686.1 | 304.8 | 0.705 |
| ELS_Phil_T | nonstationary | 0.50 | 652.8 | 285.9 | 0.850 |
| ELS_Int_T | stationary | 0.50 | 633.0 | 350.9 | 0.805 |
| ELS_Int_T | nonstationary | 0.50 | 572.3 | 322.3 | 0.860 |
| ELS_Phil_T | stationary | 0.75 | 650.9 | 312.0 | 0.720 |
| ELS_Phil_T | nonstationary | 0.75 | 615.9 | 325.6 | 0.850 |
| ELS_Int_T | stationary | 0.75 | 646.7 | 327.2 | 0.755 |
| ELS_Int_T | nonstationary | 0.75 | 600.0 | 330.2 | 0.855 |
| ELS_Phil_T | stationary | 1.00 | 672.1 | 307.6 | 0.800 |
| ELS_Phil_T | nonstationary | 1.00 | 602.5 | 336.9 | 0.880 |
| ELS_Int_T | stationary | 1.00 | 636.8 | 328.2 | 0.710 |
| ELS_Int_T | nonstationary | 1.00 | 607.5 | 313.0 | 0.835 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 594.1 | 323.0 | 0.895 | 0.578 | 0.648 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 610.1 | 292.6 | 0.920 | 0.726 | 0.882 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 577.2 | 353.1 | 0.840 | 0.799 | 0.937 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 655.2 | 311.4 | 0.810 | 0.568 | 0.622 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 641.8 | 282.5 | 0.785 | 0.720 | 0.848 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 665.5 | 268.8 | 0.820 | 0.773 | 0.909 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 602.2 | 342.8 | 0.830 | 0.567 | 0.634 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 584.5 | 297.4 | 0.840 | 0.724 | 0.879 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 579.3 | 332.7 | 0.830 | 0.774 | 0.944 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 654.8 | 291.2 | 0.780 | 0.561 | 0.621 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 616.5 | 335.8 | 0.795 | 0.715 | 0.849 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 661.2 | 312.9 | 0.740 | 0.781 | 0.904 |

## 3. Reference Values (run_benchmark_b6.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

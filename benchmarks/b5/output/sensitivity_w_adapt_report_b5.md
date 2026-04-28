# Adaptive w Trade-off Analysis — Benchmark 5 (North China Plain GRACE)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b5.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 234.6 | 482.1 | 0.865 |
| ELS_Phil_T | nonstationary | 0.00 | 200.8 | 462.4 | 0.925 |
| ELS_Int_T | stationary | 0.00 | 254.0 | 513.5 | 0.870 |
| ELS_Int_T | nonstationary | 0.00 | 138.7 | 465.4 | 0.965 |
| ELS_Phil_T | stationary | 0.25 | 642.2 | 246.2 | 0.685 |
| ELS_Phil_T | nonstationary | 0.25 | 617.5 | 237.9 | 0.790 |
| ELS_Int_T | stationary | 0.25 | 637.2 | 240.9 | 0.750 |
| ELS_Int_T | nonstationary | 0.25 | 614.9 | 234.6 | 0.870 |
| ELS_Phil_T | stationary | 0.50 | 696.0 | 213.2 | 0.640 |
| ELS_Phil_T | nonstationary | 0.50 | 675.2 | 225.4 | 0.785 |
| ELS_Int_T | stationary | 0.50 | 661.0 | 231.1 | 0.765 |
| ELS_Int_T | nonstationary | 0.50 | 593.0 | 235.7 | 0.845 |
| ELS_Phil_T | stationary | 0.75 | 648.3 | 230.6 | 0.645 |
| ELS_Phil_T | nonstationary | 0.75 | 631.5 | 237.2 | 0.770 |
| ELS_Int_T | stationary | 0.75 | 672.7 | 230.1 | 0.695 |
| ELS_Int_T | nonstationary | 0.75 | 652.9 | 232.9 | 0.855 |
| ELS_Phil_T | stationary | 1.00 | 670.6 | 213.9 | 0.725 |
| ELS_Phil_T | nonstationary | 1.00 | 645.7 | 230.3 | 0.870 |
| ELS_Int_T | stationary | 1.00 | 646.8 | 252.0 | 0.695 |
| ELS_Int_T | nonstationary | 1.00 | 636.5 | 229.1 | 0.830 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 595.9 | 232.8 | 0.875 | 0.642 | 0.763 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 632.7 | 222.3 | 0.870 | 0.806 | 0.961 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 650.9 | 233.0 | 0.850 | 0.855 | 0.986 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 662.3 | 237.9 | 0.780 | 0.619 | 0.713 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 643.2 | 233.2 | 0.750 | 0.802 | 0.931 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 635.4 | 241.4 | 0.790 | 0.850 | 0.974 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 631.4 | 237.2 | 0.820 | 0.620 | 0.735 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 628.2 | 228.4 | 0.775 | 0.808 | 0.963 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 637.0 | 241.7 | 0.805 | 0.834 | 0.981 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 672.7 | 222.1 | 0.735 | 0.611 | 0.713 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 669.0 | 245.7 | 0.740 | 0.786 | 0.929 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 663.5 | 223.0 | 0.660 | 0.837 | 0.956 |

## 3. Reference Values (run_benchmark_b5.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

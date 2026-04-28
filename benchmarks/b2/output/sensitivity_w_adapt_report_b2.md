# Adaptive w Trade-off Analysis — Benchmark 2 (MAR Arizona/Spain)
**Date:** 2026-04-24  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b2.py)  

## 1. Fixed-w Reference (sensitivity_w_results_b2.csv)

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 752.7 | 271.8 | 0.805 |
| ELS_Phil_T | nonstationary | 0.00 | 682.6 | 255.8 | 0.850 |
| ELS_Int_T | stationary | 0.00 | 750.5 | 298.6 | 0.800 |
| ELS_Int_T | nonstationary | 0.00 | 628.6 | 295.4 | 0.920 |
| ELS_Phil_T | stationary | 0.25 | 1070.3 | 272.2 | 0.520 |
| ELS_Phil_T | nonstationary | 0.25 | 1028.3 | 258.7 | 0.625 |
| ELS_Int_T | stationary | 0.25 | 1064.6 | 287.7 | 0.595 |
| ELS_Int_T | nonstationary | 0.25 | 962.8 | 252.2 | 0.685 |
| ELS_Phil_T | stationary | 0.50 | 1117.4 | 282.6 | 0.495 |
| ELS_Phil_T | nonstationary | 0.50 | 1059.1 | 281.2 | 0.600 |
| ELS_Int_T | stationary | 0.50 | 1070.8 | 296.8 | 0.575 |
| ELS_Int_T | nonstationary | 0.50 | 987.8 | 275.7 | 0.635 |
| ELS_Phil_T | stationary | 0.75 | 1101.0 | 271.0 | 0.505 |
| ELS_Phil_T | nonstationary | 0.75 | 1027.6 | 251.8 | 0.655 |
| ELS_Int_T | stationary | 0.75 | 1068.4 | 271.5 | 0.535 |
| ELS_Int_T | nonstationary | 0.75 | 946.7 | 262.6 | 0.690 |
| ELS_Phil_T | stationary | 1.00 | 1077.8 | 227.7 | 0.550 |
| ELS_Phil_T | nonstationary | 1.00 | 1022.4 | 237.5 | 0.635 |
| ELS_Int_T | stationary | 1.00 | 1080.6 | 267.8 | 0.555 |
| ELS_Int_T | nonstationary | 1.00 | 1032.2 | 279.6 | 0.645 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 987.1 | 268.8 | 0.695 | 0.719 | 0.874 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 990.8 | 249.4 | 0.660 | 0.861 | 0.986 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 1000.9 | 285.9 | 0.655 | 0.904 | 0.997 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 1045.3 | 296.0 | 0.605 | 0.694 | 0.826 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 1049.7 | 275.2 | 0.550 | 0.862 | 0.985 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 1056.5 | 250.4 | 0.530 | 0.891 | 0.990 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 1039.2 | 265.8 | 0.575 | 0.689 | 0.836 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 1031.5 | 266.1 | 0.620 | 0.865 | 0.991 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 1042.5 | 272.2 | 0.610 | 0.880 | 0.996 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 1089.3 | 286.6 | 0.585 | 0.677 | 0.815 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 1080.2 | 281.4 | 0.525 | 0.850 | 0.978 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 1086.5 | 271.9 | 0.530 | 0.890 | 0.995 |

## 3. Reference Values (run_benchmark_b2.py)

| Method | Stat U_cum | NS U_cum | Stat P_fail | NS P_fail |
|---|---|---|---|---|
| SARSOP | 1281.5 | 1181.6 | 0.260 | — |
| AlwaysRestricted | 928.3 | 810.9 | 0.525 | — |
| ELS_Phil (w=0) | 755.9 | 666.9 | 0.795 | — |
| ELS_Int (w=0) | 698.8 | 648.4 | 0.785 | — |
| ELS_Phil_T (w=0.5) | 1106.7 | 1041.9 | 0.540 | — |

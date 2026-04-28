# Adaptive w Trade-off Analysis — Benchmark 9 (Indus Basin / HKH Glacial Meltwater Recharge)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b9.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 442.6 | 540.0 | 0.900 |
| ELS_Phil_T | nonstationary | 0.00 | 386.5 | 541.4 | 0.935 |
| ELS_Int_T | stationary | 0.00 | 413.4 | 626.0 | 0.890 |
| ELS_Int_T | nonstationary | 0.00 | 257.7 | 677.6 | 0.950 |
| ELS_Phil_T | stationary | 0.25 | 983.6 | 300.7 | 0.790 |
| ELS_Phil_T | nonstationary | 0.25 | 1015.6 | 285.0 | 0.800 |
| ELS_Int_T | stationary | 0.25 | 969.0 | 324.1 | 0.780 |
| ELS_Int_T | nonstationary | 0.25 | 965.5 | 316.3 | 0.860 |
| ELS_Phil_T | stationary | 0.50 | 996.6 | 278.8 | 0.740 |
| ELS_Phil_T | nonstationary | 0.50 | 1059.2 | 279.3 | 0.855 |
| ELS_Int_T | stationary | 0.50 | 968.5 | 315.8 | 0.845 |
| ELS_Int_T | nonstationary | 0.50 | 955.9 | 322.7 | 0.880 |
| ELS_Phil_T | stationary | 0.75 | 1001.8 | 282.6 | 0.765 |
| ELS_Phil_T | nonstationary | 0.75 | 1019.7 | 324.7 | 0.835 |
| ELS_Int_T | stationary | 0.75 | 979.8 | 299.1 | 0.715 |
| ELS_Int_T | nonstationary | 0.75 | 1035.4 | 317.0 | 0.845 |
| ELS_Phil_T | stationary | 1.00 | 1021.8 | 270.3 | 0.775 |
| ELS_Phil_T | nonstationary | 1.00 | 1009.6 | 309.3 | 0.860 |
| ELS_Int_T | stationary | 1.00 | 970.5 | 278.6 | 0.770 |
| ELS_Int_T | nonstationary | 1.00 | 1007.6 | 287.9 | 0.835 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 992.0 | 300.5 | 0.860 | 0.681 | 0.823 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 972.8 | 313.6 | 0.900 | 0.839 | 0.984 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 978.9 | 296.9 | 0.880 | 0.858 | 0.987 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 967.9 | 317.8 | 0.785 | 0.677 | 0.806 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 975.9 | 295.7 | 0.805 | 0.822 | 0.957 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 949.4 | 307.3 | 0.835 | 0.861 | 0.987 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 989.7 | 304.4 | 0.850 | 0.666 | 0.803 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 1024.1 | 315.9 | 0.845 | 0.826 | 0.973 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 1012.6 | 327.8 | 0.820 | 0.835 | 0.980 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 1025.4 | 298.1 | 0.815 | 0.655 | 0.781 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 1004.0 | 315.4 | 0.800 | 0.809 | 0.954 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 1026.5 | 294.6 | 0.770 | 0.840 | 0.969 |

## 3. Reference Values (run_benchmark_b6.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

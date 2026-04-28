# Adaptive w Trade-off Analysis — Benchmark 1
**Date:** 2026-04-24  
**N_MC = 200  T = 60  γ = 0.97  SEED = 2024**  
**Method:** ELS_Phil_Adapt and ELS_Int_Adapt (els_adapt.py, Idea 3.1)**  

## 1. Fixed-w Reference (from sensitivity_w_results.csv)

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 989.4 | 538.0 | 0.885 |
| ELS_Phil_T | nonstationary | 0.00 | 982.2 | 449.7 | 0.920 |
| ELS_Int_T | stationary | 0.00 | 975.2 | 500.8 | 0.915 |
| ELS_Int_T | nonstationary | 0.00 | 853.0 | 556.4 | 0.970 |
| ELS_Phil_T | stationary | 0.25 | 1504.7 | 319.2 | 0.675 |
| ELS_Phil_T | nonstationary | 0.25 | 1458.8 | 292.5 | 0.865 |
| ELS_Int_T | stationary | 0.25 | 1476.3 | 303.3 | 0.750 |
| ELS_Int_T | nonstationary | 0.25 | 1432.7 | 282.4 | 0.865 |
| ELS_Phil_T | stationary | 0.50 | 1545.4 | 299.8 | 0.660 |
| ELS_Phil_T | nonstationary | 0.50 | 1457.8 | 305.3 | 0.865 |
| ELS_Int_T | stationary | 0.50 | 1515.6 | 313.9 | 0.780 |
| ELS_Int_T | nonstationary | 0.50 | 1429.7 | 328.1 | 0.880 |
| ELS_Phil_T | stationary | 0.75 | 1562.3 | 303.1 | 0.700 |
| ELS_Phil_T | nonstationary | 0.75 | 1420.2 | 318.0 | 0.860 |
| ELS_Int_T | stationary | 0.75 | 1560.8 | 299.5 | 0.660 |
| ELS_Int_T | nonstationary | 0.75 | 1379.7 | 324.4 | 0.830 |
| ELS_Phil_T | stationary | 1.00 | 1542.4 | 287.5 | 0.680 |
| ELS_Phil_T | nonstationary | 1.00 | 1453.8 | 306.2 | 0.875 |
| ELS_Int_T | stationary | 1.00 | 1536.7 | 317.4 | 0.680 |
| ELS_Int_T | nonstationary | 1.00 | 1463.4 | 329.7 | 0.835 |

## 2. Adaptive w Results (ELS_Phil_Adapt / ELS_Int_Adapt)

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 1431.8 | 327.9 | 0.875 | 0.857 | 0.992 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 1423.5 | 304.8 | 0.860 | 0.926 | 0.998 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 1451.4 | 297.0 | 0.875 | 0.938 | 1.000 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 1516.5 | 319.0 | 0.770 | 0.842 | 0.972 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 1524.6 | 295.5 | 0.685 | 0.929 | 0.995 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 1508.2 | 284.5 | 0.695 | 0.934 | 1.000 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 1440.6 | 314.4 | 0.880 | 0.798 | 0.971 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 1463.8 | 295.9 | 0.860 | 0.912 | 1.000 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 1489.7 | 326.7 | 0.825 | 0.915 | 1.000 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 1522.5 | 303.7 | 0.770 | 0.804 | 0.949 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 1515.3 | 338.5 | 0.685 | 0.909 | 0.995 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 1512.5 | 318.8 | 0.730 | 0.918 | 0.999 |

## 3. Reference Values (run_benchmark.py, N_MC=200)

| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |
|---|---|---|---|---|
| SARSOP | 1707.0 | 1561.9 | 0.405 | 0.650 |
| AlwaysRestricted | 1439.2 | 1356.2 | 0.465 | 0.660 |
| ELS_Phil (w=0) | 1054.7 | 976.5 | 0.855 | 0.960 |
| ELS_Int (w=0) | 947.6 | 838.8 | 0.885 | 0.960 |

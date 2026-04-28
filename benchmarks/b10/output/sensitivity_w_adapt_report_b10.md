# Adaptive w Trade-off Analysis — Benchmark 10 (Sahel / Lake Chad Basin Quaternary Aquifer)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b10.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 446.2 | 405.8 | 0.940 |
| ELS_Phil_T | nonstationary | 0.00 | 433.6 | 398.8 | 0.960 |
| ELS_Int_T | stationary | 0.00 | 448.9 | 462.6 | 0.920 |
| ELS_Int_T | nonstationary | 0.00 | 377.5 | 466.5 | 0.965 |
| ELS_Phil_T | stationary | 0.25 | 871.7 | 283.1 | 0.880 |
| ELS_Phil_T | nonstationary | 0.25 | 882.1 | 245.6 | 0.900 |
| ELS_Int_T | stationary | 0.25 | 875.7 | 255.5 | 0.875 |
| ELS_Int_T | nonstationary | 0.25 | 865.4 | 251.8 | 0.935 |
| ELS_Phil_T | stationary | 0.50 | 866.2 | 230.5 | 0.835 |
| ELS_Phil_T | nonstationary | 0.50 | 936.7 | 244.2 | 0.900 |
| ELS_Int_T | stationary | 0.50 | 874.8 | 281.6 | 0.910 |
| ELS_Int_T | nonstationary | 0.50 | 867.3 | 249.3 | 0.910 |
| ELS_Phil_T | stationary | 0.75 | 873.6 | 238.7 | 0.830 |
| ELS_Phil_T | nonstationary | 0.75 | 899.0 | 263.6 | 0.890 |
| ELS_Int_T | stationary | 0.75 | 880.2 | 243.1 | 0.810 |
| ELS_Int_T | nonstationary | 0.75 | 924.4 | 244.9 | 0.920 |
| ELS_Phil_T | stationary | 1.00 | 907.8 | 226.5 | 0.880 |
| ELS_Phil_T | nonstationary | 1.00 | 900.5 | 242.4 | 0.920 |
| ELS_Int_T | stationary | 1.00 | 872.6 | 242.6 | 0.835 |
| ELS_Int_T | nonstationary | 1.00 | 887.8 | 223.6 | 0.915 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 904.8 | 247.0 | 0.930 | 0.658 | 0.794 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 873.9 | 258.1 | 0.945 | 0.812 | 0.969 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 874.7 | 252.8 | 0.915 | 0.847 | 0.987 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 863.8 | 262.0 | 0.845 | 0.651 | 0.769 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 882.7 | 234.1 | 0.880 | 0.818 | 0.960 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 856.9 | 232.0 | 0.875 | 0.834 | 0.961 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 903.8 | 235.5 | 0.910 | 0.643 | 0.776 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 909.5 | 266.2 | 0.895 | 0.800 | 0.960 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 889.8 | 247.8 | 0.905 | 0.814 | 0.985 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 894.6 | 262.0 | 0.860 | 0.637 | 0.754 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 904.9 | 249.9 | 0.860 | 0.799 | 0.948 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 902.3 | 244.2 | 0.850 | 0.837 | 0.964 |

## 3. Reference Values (run_benchmark_b6.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

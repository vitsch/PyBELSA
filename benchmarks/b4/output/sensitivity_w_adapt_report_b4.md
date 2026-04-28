# Adaptive w Trade-off Analysis — Benchmark 4 (Murray-Darling Basin SDL)
**Date:** 2026-04-24  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b4.py)  

## 1. Fixed-w Reference (sensitivity_w_results_b4.csv)

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 417.3 | 450.7 | 0.820 |
| ELS_Phil_T | nonstationary | 0.00 | 366.6 | 478.9 | 0.885 |
| ELS_Int_T | stationary | 0.00 | 476.0 | 480.4 | 0.835 |
| ELS_Int_T | nonstationary | 0.00 | 312.5 | 477.1 | 0.940 |
| ELS_Phil_T | stationary | 0.25 | 970.5 | 211.7 | 0.565 |
| ELS_Phil_T | nonstationary | 0.25 | 898.7 | 210.1 | 0.730 |
| ELS_Int_T | stationary | 0.25 | 952.3 | 211.4 | 0.640 |
| ELS_Int_T | nonstationary | 0.25 | 905.3 | 217.1 | 0.785 |
| ELS_Phil_T | stationary | 0.50 | 995.5 | 203.3 | 0.550 |
| ELS_Phil_T | nonstationary | 0.50 | 968.7 | 210.8 | 0.700 |
| ELS_Int_T | stationary | 0.50 | 976.2 | 219.6 | 0.665 |
| ELS_Int_T | nonstationary | 0.50 | 893.7 | 212.5 | 0.705 |
| ELS_Phil_T | stationary | 0.75 | 964.8 | 207.4 | 0.565 |
| ELS_Phil_T | nonstationary | 0.75 | 943.7 | 208.2 | 0.700 |
| ELS_Int_T | stationary | 0.75 | 969.3 | 200.1 | 0.570 |
| ELS_Int_T | nonstationary | 0.75 | 931.4 | 207.8 | 0.800 |
| ELS_Phil_T | stationary | 1.00 | 974.8 | 189.9 | 0.605 |
| ELS_Phil_T | nonstationary | 1.00 | 953.9 | 196.5 | 0.720 |
| ELS_Int_T | stationary | 1.00 | 976.5 | 220.4 | 0.570 |
| ELS_Int_T | nonstationary | 1.00 | 951.7 | 209.1 | 0.710 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 917.2 | 205.9 | 0.770 | 0.639 | 0.755 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 929.1 | 214.1 | 0.805 | 0.793 | 0.961 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 928.2 | 199.3 | 0.735 | 0.850 | 0.979 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 964.4 | 231.3 | 0.650 | 0.619 | 0.709 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 952.4 | 204.0 | 0.650 | 0.794 | 0.931 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 965.3 | 201.0 | 0.625 | 0.840 | 0.969 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 914.6 | 209.9 | 0.710 | 0.612 | 0.717 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 911.1 | 201.3 | 0.675 | 0.800 | 0.956 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 933.2 | 189.5 | 0.665 | 0.823 | 0.983 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 970.2 | 199.7 | 0.610 | 0.603 | 0.693 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 984.8 | 207.4 | 0.580 | 0.768 | 0.906 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 977.0 | 202.1 | 0.560 | 0.821 | 0.945 |

## 3. Reference Values (run_benchmark_b4.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

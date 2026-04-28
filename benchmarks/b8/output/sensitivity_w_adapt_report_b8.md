# Adaptive w Trade-off Analysis — Benchmark 8 (Stampriet Transboundary Aquifer STAS)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b8.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 599.0 | 311.5 | 0.685 |
| ELS_Phil_T | nonstationary | 0.00 | 483.8 | 361.9 | 0.790 |
| ELS_Int_T | stationary | 0.00 | 312.7 | 609.5 | 0.810 |
| ELS_Int_T | nonstationary | 0.00 | 180.3 | 598.6 | 0.915 |
| ELS_Phil_T | stationary | 0.25 | 881.7 | 212.0 | 0.620 |
| ELS_Phil_T | nonstationary | 0.25 | 891.1 | 213.6 | 0.745 |
| ELS_Int_T | stationary | 0.25 | 848.4 | 235.9 | 0.670 |
| ELS_Int_T | nonstationary | 0.25 | 845.6 | 231.5 | 0.780 |
| ELS_Phil_T | stationary | 0.50 | 891.2 | 195.0 | 0.585 |
| ELS_Phil_T | nonstationary | 0.50 | 913.2 | 230.4 | 0.715 |
| ELS_Int_T | stationary | 0.50 | 834.6 | 204.9 | 0.680 |
| ELS_Int_T | nonstationary | 0.50 | 837.3 | 236.4 | 0.770 |
| ELS_Phil_T | stationary | 0.75 | 887.1 | 210.1 | 0.635 |
| ELS_Phil_T | nonstationary | 0.75 | 897.3 | 245.9 | 0.710 |
| ELS_Int_T | stationary | 0.75 | 863.0 | 218.3 | 0.605 |
| ELS_Int_T | nonstationary | 0.75 | 886.6 | 219.4 | 0.785 |
| ELS_Phil_T | stationary | 1.00 | 893.7 | 217.2 | 0.625 |
| ELS_Phil_T | nonstationary | 1.00 | 879.8 | 211.3 | 0.810 |
| ELS_Int_T | stationary | 1.00 | 838.6 | 199.8 | 0.655 |
| ELS_Int_T | nonstationary | 1.00 | 855.3 | 207.0 | 0.755 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 842.7 | 234.8 | 0.750 | 0.684 | 0.834 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 856.3 | 214.5 | 0.800 | 0.832 | 0.976 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 851.5 | 221.3 | 0.750 | 0.857 | 0.984 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 851.1 | 244.6 | 0.685 | 0.677 | 0.801 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 856.0 | 211.0 | 0.670 | 0.830 | 0.942 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 836.8 | 210.5 | 0.670 | 0.857 | 0.977 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 893.2 | 220.0 | 0.730 | 0.653 | 0.789 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 881.2 | 225.1 | 0.710 | 0.815 | 0.970 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 907.8 | 234.3 | 0.735 | 0.823 | 0.974 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 898.2 | 208.2 | 0.705 | 0.651 | 0.772 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 893.0 | 220.1 | 0.630 | 0.804 | 0.936 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 905.1 | 240.7 | 0.630 | 0.831 | 0.944 |

## 3. Reference Values (run_benchmark_b6.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

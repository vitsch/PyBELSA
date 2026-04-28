# Adaptive w Trade-off Analysis — Benchmark 7 (Coastal Saltwater Intrusion)
**Date:** 2026-04-25  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b7.py)  

## 1. Fixed-w Reference

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | 172.1 | 824.5 | 0.795 |
| ELS_Phil_T | nonstationary | 0.00 | 30.7 | 885.2 | 0.870 |
| ELS_Int_T | stationary | 0.00 | 253.7 | 966.8 | 0.830 |
| ELS_Int_T | nonstationary | 0.00 | -82.7 | 1093.6 | 0.850 |
| ELS_Phil_T | stationary | 0.25 | 1318.3 | 373.7 | 0.560 |
| ELS_Phil_T | nonstationary | 0.25 | 1301.7 | 353.6 | 0.595 |
| ELS_Int_T | stationary | 0.25 | 1255.0 | 336.2 | 0.605 |
| ELS_Int_T | nonstationary | 0.25 | 1215.4 | 349.8 | 0.705 |
| ELS_Phil_T | stationary | 0.50 | 1279.6 | 327.3 | 0.530 |
| ELS_Phil_T | nonstationary | 0.50 | 1302.0 | 334.9 | 0.580 |
| ELS_Int_T | stationary | 0.50 | 1256.9 | 364.8 | 0.595 |
| ELS_Int_T | nonstationary | 0.50 | 1270.0 | 378.2 | 0.600 |
| ELS_Phil_T | stationary | 0.75 | 1275.6 | 322.5 | 0.510 |
| ELS_Phil_T | nonstationary | 0.75 | 1338.3 | 330.7 | 0.685 |
| ELS_Int_T | stationary | 0.75 | 1295.1 | 362.5 | 0.565 |
| ELS_Int_T | nonstationary | 0.75 | 1290.3 | 370.2 | 0.675 |
| ELS_Phil_T | stationary | 1.00 | 1316.9 | 318.2 | 0.605 |
| ELS_Phil_T | nonstationary | 1.00 | 1258.2 | 343.3 | 0.620 |
| ELS_Int_T | stationary | 1.00 | 1257.2 | 310.1 | 0.615 |
| ELS_Int_T | nonstationary | 1.00 | 1247.5 | 341.5 | 0.630 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 1264.5 | 375.7 | 0.670 | 0.558 | 0.620 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 1261.0 | 368.0 | 0.640 | 0.678 | 0.827 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 1275.4 | 322.6 | 0.650 | 0.718 | 0.859 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 1287.2 | 340.7 | 0.595 | 0.552 | 0.596 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 1272.8 | 365.1 | 0.600 | 0.664 | 0.783 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 1247.3 | 373.1 | 0.600 | 0.703 | 0.847 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 1262.0 | 343.7 | 0.575 | 0.541 | 0.588 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 1287.8 | 367.2 | 0.635 | 0.647 | 0.768 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 1276.7 | 342.0 | 0.595 | 0.711 | 0.849 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 1334.2 | 365.9 | 0.595 | 0.541 | 0.582 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 1337.2 | 356.1 | 0.575 | 0.643 | 0.756 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 1333.3 | 338.0 | 0.565 | 0.684 | 0.814 |

## 3. Reference Values (run_benchmark_b6.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

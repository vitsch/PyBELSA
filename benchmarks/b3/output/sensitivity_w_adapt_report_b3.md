# Adaptive w Trade-off Analysis — Benchmark 3 (Gorelick Pump-and-Treat)
**Date:** 2026-04-24  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**w_adapt method:** ELS_Phil_Adapt / ELS_Int_Adapt (els_adapt_b3.py)  

## 1. Fixed-w Reference (sensitivity_w_results_b3.csv)

| Method | Condition | w | U_cum | SD | P_fail |
|---|---|---|---|---|---|
| ELS_Phil_T | stationary | 0.00 | -83.1 | 701.6 | 0.875 |
| ELS_Phil_T | nonstationary | 0.00 | -125.0 | 798.5 | 0.920 |
| ELS_Int_T | stationary | 0.00 | -9.2 | 730.9 | 0.875 |
| ELS_Int_T | nonstationary | 0.00 | -189.8 | 785.3 | 0.930 |
| ELS_Phil_T | stationary | 0.25 | 596.3 | 337.1 | 0.720 |
| ELS_Phil_T | nonstationary | 0.25 | 576.7 | 345.3 | 0.820 |
| ELS_Int_T | stationary | 0.25 | 562.7 | 345.4 | 0.695 |
| ELS_Int_T | nonstationary | 0.25 | 578.5 | 335.1 | 0.845 |
| ELS_Phil_T | stationary | 0.50 | 613.4 | 303.3 | 0.690 |
| ELS_Phil_T | nonstationary | 0.50 | 657.0 | 312.7 | 0.800 |
| ELS_Int_T | stationary | 0.50 | 614.0 | 336.2 | 0.735 |
| ELS_Int_T | nonstationary | 0.50 | 603.0 | 316.9 | 0.795 |
| ELS_Phil_T | stationary | 0.75 | 587.5 | 321.4 | 0.680 |
| ELS_Phil_T | nonstationary | 0.75 | 629.7 | 330.1 | 0.865 |
| ELS_Int_T | stationary | 0.75 | 581.9 | 307.3 | 0.680 |
| ELS_Int_T | nonstationary | 0.75 | 649.7 | 316.6 | 0.840 |
| ELS_Phil_T | stationary | 1.00 | 630.1 | 292.6 | 0.735 |
| ELS_Phil_T | nonstationary | 1.00 | 622.6 | 335.8 | 0.805 |
| ELS_Int_T | stationary | 1.00 | 595.7 | 275.6 | 0.695 |
| ELS_Int_T | nonstationary | 1.00 | 589.7 | 295.9 | 0.800 |

## 2. Adaptive w Results

| Method | Condition | η | w_init | U_cum | SD | P_fail | w_mean | w_final |
|---|---|---|---|---|---|---|---|---|
| ELS_Int_Adapt | nonstationary | 0.1 | 0.50 | 613.8 | 334.4 | 0.825 | 0.604 | 0.705 |
| ELS_Int_Adapt | nonstationary | 0.5 | 0.50 | 611.6 | 336.6 | 0.840 | 0.764 | 0.933 |
| ELS_Int_Adapt | nonstationary | 1.0 | 0.50 | 626.3 | 314.7 | 0.815 | 0.805 | 0.970 |
| ELS_Int_Adapt | stationary | 0.1 | 0.50 | 631.5 | 317.1 | 0.685 | 0.595 | 0.670 |
| ELS_Int_Adapt | stationary | 0.5 | 0.50 | 630.3 | 297.5 | 0.725 | 0.768 | 0.907 |
| ELS_Int_Adapt | stationary | 1.0 | 0.50 | 598.7 | 351.0 | 0.730 | 0.804 | 0.933 |
| ELS_Phil_Adapt | nonstationary | 0.1 | 0.50 | 605.2 | 325.9 | 0.815 | 0.584 | 0.671 |
| ELS_Phil_Adapt | nonstationary | 0.5 | 0.50 | 618.0 | 304.8 | 0.815 | 0.740 | 0.893 |
| ELS_Phil_Adapt | nonstationary | 1.0 | 0.50 | 564.1 | 309.7 | 0.800 | 0.805 | 0.965 |
| ELS_Phil_Adapt | stationary | 0.1 | 0.50 | 614.4 | 326.6 | 0.780 | 0.583 | 0.657 |
| ELS_Phil_Adapt | stationary | 0.5 | 0.50 | 638.2 | 300.9 | 0.740 | 0.737 | 0.872 |
| ELS_Phil_Adapt | stationary | 1.0 | 0.50 | 647.0 | 319.5 | 0.660 | 0.768 | 0.908 |

## 3. Reference Values (run_benchmark_b3.py)

| Method | Stat U_cum | NS U_cum |
|---|---|---|
| SARSOP | — | — |
| AlwaysRestricted | — | — |
| ELS_Phil (w=0) | — | — |

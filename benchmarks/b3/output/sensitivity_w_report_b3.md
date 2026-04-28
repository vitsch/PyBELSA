# T-Sensitivity Analysis — B3 Gorelick P&T  w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}
**Date:** 2026-04-24  
**N_MC = 200  T = 30  γ = 0.97  SEED = 2024**  
**Benchmark:** B3 Gorelick Pump-and-Treat  (stable dynamics → faster spreading at step 15)  

## Condition: stationary

### ELS_Phil_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | -83.1 | 701.6 | 0.875 | 10.1 |
| 0.25 | 596.3 | 337.1 | 0.720 | 9.9 |
| 0.50 | 613.4 | 303.3 | 0.690 | 9.6 |
| 0.75 | 587.5 | 321.4 | 0.680 | 10.9 |
| 1.00 | 630.1 | 292.6 | 0.735 | 10.5 |

### ELS_Int_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | -9.2 | 730.8 | 0.875 | 8.5 |
| 0.25 | 562.7 | 345.4 | 0.695 | 10.0 |
| 0.50 | 614.0 | 336.2 | 0.735 | 9.7 |
| 0.75 | 581.9 | 307.3 | 0.680 | 9.5 |
| 1.00 | 595.7 | 275.6 | 0.695 | 9.8 |

## Condition: nonstationary

### ELS_Phil_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | -125.0 | 798.5 | 0.920 | 10.3 |
| 0.25 | 576.7 | 345.3 | 0.820 | 10.9 |
| 0.50 | 657.0 | 312.7 | 0.800 | 10.1 |
| 0.75 | 629.7 | 330.1 | 0.865 | 10.2 |
| 1.00 | 622.6 | 335.8 | 0.805 | 10.7 |

### ELS_Int_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | -189.8 | 785.3 | 0.930 | 10.0 |
| 0.25 | 578.5 | 335.2 | 0.845 | 11.8 |
| 0.50 | 603.0 | 316.9 | 0.795 | 11.1 |
| 0.75 | 649.7 | 316.5 | 0.840 | 9.7 |
| 1.00 | 589.7 | 295.9 | 0.800 | 11.4 |

## Reference values (run_benchmark_b3.py, N_MC=200)

| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |
|--------|-----------------|---------|-------------|-----------|
| ELS_Phil (w=0) | — | — | — | — |
| ELS_Int (w=0)  | — | — | — | — |
| ELS_Phil_T (w=0.5) | — | — | — | — |
| SARSOP  | — | — | — | — |
| AlwaysRestricted | — | — | — | — |
(run run_benchmark_b3.py first to fill reference values)

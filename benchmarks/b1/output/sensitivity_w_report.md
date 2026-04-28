# T-Sensitivity Analysis — Hybrid Belief Update w ∈ {0.0, 0.25, 0.5, 0.75, 1.0}
**Date:** 2026-04-23  
**N_MC = 200  T = 60  γ = 0.97  SEED = 2024**  
**Intervention A1:** hybrid update = (1−w)·b + w·(T_stat[a]ᵀ·b), then likelihood correction  

## Condition: stationary

### ELS_Phil_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | 989.4 | 538.0 | 0.885 | 19.4 |
| 0.25 | 1504.7 | 319.2 | 0.675 | 19.7 |
| 0.50 | 1545.4 | 299.8 | 0.660 | 20.0 |
| 0.75 | 1562.3 | 303.1 | 0.700 | 20.2 |
| 1.00 | 1542.4 | 287.5 | 0.680 | 19.1 |

### ELS_Int_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | 975.2 | 500.8 | 0.915 | 17.2 |
| 0.25 | 1476.3 | 303.3 | 0.750 | 19.9 |
| 0.50 | 1515.6 | 313.9 | 0.780 | 20.2 |
| 0.75 | 1560.8 | 299.5 | 0.660 | 20.1 |
| 1.00 | 1536.6 | 317.4 | 0.680 | 20.0 |

## Condition: nonstationary

### ELS_Phil_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | 982.2 | 449.7 | 0.920 | 20.4 |
| 0.25 | 1458.8 | 292.5 | 0.865 | 25.6 |
| 0.50 | 1457.8 | 305.3 | 0.865 | 23.3 |
| 0.75 | 1420.2 | 318.0 | 0.860 | 21.3 |
| 1.00 | 1453.8 | 306.2 | 0.875 | 23.9 |

### ELS_Int_T

| w | U_cum (mean) | U_cum (SD) | P_fail | MTTF |
|---|---|---|---|---|
| 0.00 | 853.0 | 556.3 | 0.970 | 19.8 |
| 0.25 | 1432.7 | 282.4 | 0.865 | 24.0 |
| 0.50 | 1429.7 | 328.1 | 0.880 | 23.6 |
| 0.75 | 1379.7 | 324.4 | 0.830 | 20.1 |
| 1.00 | 1463.4 | 329.7 | 0.835 | 24.1 |

## Reference values (from run_benchmark.py, N_MC=200)

| Method | Stationary U_cum | NS U_cum | Stat P_fail | NS P_fail |
|--------|-----------------|---------|-------------|-----------|
| ELS_Phil (w=0) | 1054.7 | 976.5 | 0.855 | 0.960 |
| ELS_Int (w=0) | 947.6 | 838.8 | 0.885 | 0.960 |
| SARSOP | 1707.0 | 1561.9 | 0.405 | 0.650 |
| AlwaysRestricted | 1439.2 | 1356.2 | 0.465 | 0.660 |

> Note: w=0.0 in this script uses the same algorithm as the original ELS methods
> but may differ slightly due to different episode seeds (M_IDX_BASE=100).

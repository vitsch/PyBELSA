# PyBELSA Benchmark Suite: B1–B10
## Ten-Benchmark Evaluation of the BELSA Framework
### Nature Water Submission — Reproducibility Reference
**Date:** 2026-04-27  
**Evaluation protocol:** N_MC = 200 episodes per method per condition, γ = 0.97, SEED = 2024, bootstrap CI B = 2000

---

## Overview

| BM | Domain / System | Region | U_T | Type | NS | Source code |
|---|---|---|---|---|---|---|
| B1 | Synthetic 5-state aquifer (reproducibility anchor) | UK (synthetic) | 0.00 | Parametric | Yes | `P_Base/scr/` |
| B2 | Managed aquifer recharge | Arizona, US / Catalonia, ES | 0.50 | Parametric | Yes | `P_Base2/scr/` |
| B3 | Pump-and-treat remediation (Gorelick) | Illinois, US | 0.60 | Parametric | Yes | `P_Base3/scr/` |
| B4 | Surface–GW exchange under SDL | Murray–Darling Basin, AU | 0.70 | Parametric | Yes | `P_Base4/scr/` |
| B5 | GRACE-based depletion monitoring | North China Plain, CN | 0.80 | Parametric | Yes | `P_Base5/scr/` |
| B6 | Dual-porosity karst aquifer | Dinaric / Mediterranean | 0.90 | Structural | Yes | `P_Base6/scr/` |
| B7 | Coastal saltwater intrusion (tipping point) | SE England / Netherlands | 0.70 | Structural | Yes | `P_Base7/scr/` |
| B8 | Transboundary multi-actor aquifer (STAS) | Namibia / Botswana / SA | 0.80 | Structural | Yes | `P_Base8/scr/` |
| B9 | Glacier–groundwater coupling (HKH) | Indus Basin, PK/IN/AF/CN | 0.90 | Structural | Yes | `P_Base9/scr/` |
| B10 | Data-scarce pastoral aquifer (LCB) | Sahel / Lake Chad Basin | 1.00 | Structural | Yes | `P_Base10/scr/` |

**Type:** Parametric = T form known, parameters uncertain. Structural = T form itself unknown or fundamentally unidentifiable.  
**U_T:** Model-uncertainty index (ordinal composite; see Methods §4.4 in the paper).  
**NS:** Non-stationarity condition available (climate regime shift mid-horizon).

---

## Benchmark 1 — Synthetic 5-State Aquifer (Reproducibility Anchor)

### Physical Context

A fully controlled synthetic POMDP designed to isolate framework components, validate statistical methods, and serve as the reproducibility anchor for the entire benchmark suite. Simulates a 5-state piezometric head decline in a confined aquifer with two regimes: stationary dynamics and a climate-shifted regime activating at the mid-horizon.

All parameters are published (below) and deposited with code; no external data required.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Sustainable >−5 m → θ₅ Failed <−50 m) |
| Actions M | 3 |
| Horizon T | 60 steps |
| γ | 0.97 |
| CLIMATE_SWITCH_STEP | 30 |
| SIGMA_OBS | 4.0 m (piezometric head) |
| H_MEAN | [0.0, −10.0, −22.0, −40.0, −60.0] m |
| OBS_BINS | linspace(−80, 10, 21) → 20 bins |
| L_PHIL | 0.5 × L(σ=3.5 m) + 0.5 × L(σ=5.5 m) |
| U_MIN | −100.0 |
| T_misspec | T_stat + 15% depletion shift (δ=0.15 for a₁, a₂; δ=0.075 for a₃) |

### Reward Matrix R[action, state]

| Action | θ₁ Sustainable | θ₂ Moderate | θ₃ Significant | θ₄ Critical | θ₅ Failed |
|---|---|---|---|---|---|
| a₁ Unrestricted | +100 | +80 | +40 | −20 | −100 |
| a₂ Restricted 50% | +60 | +60 | +55 | +30 | −30 |
| a₃ Emergency cessation | +5 | +5 | +5 | +5 | +5 |

### Transition Matrix T_stat (Regime A, a₁ Unrestricted — representative row)

|  | θ₁ | θ₂ | θ₃ | θ₄ | θ₅ |
|---|---|---|---|---|---|
| From θ₁ | 0.70 | 0.25 | 0.05 | 0.00 | 0.00 |
| From θ₂ | 0.10 | 0.65 | 0.20 | 0.05 | 0.00 |
| From θ₃ | 0.00 | 0.10 | 0.65 | 0.20 | 0.05 |
| From θ₄ | 0.00 | 0.00 | 0.10 | 0.65 | 0.25 |
| From θ₅ | 0.00 | 0.00 | 0.00 | 0.10 | 0.90 |

Full T matrices for all 3 actions in `P_Base/scr/pomdp_env.py`.

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SARSOP | **1707.0** | 1584.9 | 0.405 | 0.580 |
| SARSOP_Misspec | 1659.8 | 1547.1 | 0.430 | 0.595 |
| ELS_Phil_T (w=0.5) | 1537.0 | 1462.8 | 0.660 | 0.760 |
| AlwaysRestricted | 962.1 | 891.3 | 0.785 | 0.840 |

**SARSOP − ELS gap (stationary): +170 units** (95% bootstrap CI [+115, +226], p<0.001).  
This is the *price of T-agnosticism* at zero model uncertainty — the maximum in the suite.

---

## Benchmark 2 — Managed Aquifer Recharge (Arizona / Catalonia)

### Physical Context

Managed Aquifer Recharge (MAR) systems in water-stressed semi-arid regions where recharge decisions are made under uncertain aquifer states and climate-projected demand. Based on the Arizona Active Management Area (ADWR annual reports) and the Sant Vicenç dels Horts system (Catalonia Water Agency, openly licensed). Both involve sequential recharge / abstraction decisions under uncertain aquifer state — a direct POMDP fit. T-uncertainty (U_T ≈ 0.5) arises from estimation on multi-decadal recharge records with SSP2-4.5 vs SSP5-8.5 divergence.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Surplus → θ₅ Exhausted) |
| Actions M | 3 (unrestricted, MAR-restricted, emergency) |
| Horizon T | 30 |
| γ | 0.97 |
| CLIMATE_SWITCH_STEP | 15 (SSP2-4.5 → SSP5-8.5 divergence) |
| SIGMA_OBS | 35 GL-equiv |
| L_PHIL | 0.5 × L(σ=27 GL) + 0.5 × L(σ=50 GL) |
| T_misspec | T_stat + 15% depletion shift |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SARSOP | **1281.5** | 1141.8 | — | — |
| ELS_Phil_T (w=0.5) | 1106.7 | 967.1 | 0.495 | 0.600 |

**SARSOP − ELS gap (stationary): +174.7 units** (p<0.001).  
Fixed-w optimal: w ≈ 0.50 (symmetric T-trust / static blend).

---

## Benchmark 3 — Pump-and-Treat Remediation (Gorelick)

### Physical Context

The Gorelick et al. (1984/1990) pump-and-treat optimisation problem — the foundational benchmark in groundwater remediation literature (500+ citations, multiple replications). POMDP extension with uncertain plume states (5 contamination levels) and noisy concentration observations. T-uncertainty (U_T ≈ 0.6) arises from estimation on limited plume-progression data; non-stationarity represents faster plume spreading under increased recharge at step 15.

**Cost-asymmetric reward structure:** Under-restriction during active plume progression (a₁ at θ₄, θ₅) is penalised far more heavily than over-restriction — this creates the B3 crossover where ELS wins despite parametric uncertainty.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Clean → θ₅ Fully contaminated) |
| Actions M | 3 (maintain, pump-and-treat, emergency P&T) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 (faster plume spreading) |
| SIGMA_OBS | 28 μg/L (trichloroethylene concentration proxy) |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_S | **663.8** | 714.1 | 0.545 | 0.745 |
| InfoGap | 703.1 | 700.1 | 0.620 | 0.770 |
| ELS_Phil_T (w=0.5) | 594.1 | 618.9 | 0.690 | 0.860 |
| SARSOP | 528.2 | 556.4 | 0.730 | 0.860 |

**SARSOP − ELS gap (stationary): −65.9 units** — ELS wins.  
B3 is the only parametric benchmark where ELS outperforms SARSOP; the cost-asymmetric reward structure penalises SARSOP's conservative alpha-vector policy under plume progression.

---

## Benchmark 4 — Murray–Darling Basin Groundwater SDL

### Physical Context

The Murray–Darling Basin (MDB) groundwater system managed under the Basin Plan (2012) Sustainable Diversion Limits (SDLs) — annually binding extraction caps to recover overallocated aquifers. CMIP6 ensemble projections (CSIRO 2022) project 5–25% recharge decline by 2050 under SSP5-8.5 (6–18% inter-GCM spread). Data: MDBA SDL Accounting Reports (mdba.gov.au). T-uncertainty (U_T ≈ 0.70) arises from CMIP6 ensemble spread in projected recharge. Observation proxy: bore-network storage units (GL-equivalent).

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Surplus >150% SDL buffer → θ₅ Critical <40% SDL buffer) |
| Actions M | 3 (a₁ Unrestricted, a₂ SDL-restricted, a₃ Emergency −30%) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 (SSP5-8.5 diverges from SSP2-4.5 median) |
| SIGMA_OBS | 35 GL-equiv |
| H_MEAN | [150, 80, 10, −70, −180] GL-equiv |
| L_PHIL | 0.5 × L(σ=27 GL) + 0.5 × L(σ=50 GL) |
| U_MIN | −500.0 |
| T_shift delta | 0.15 / 0.12 / 0.07 per action |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_S | **1057.3** | 1021.4 | 0.605 | 0.795 |
| SARSOP | 1009.1 | 966.2 | 0.485 | 0.680 |
| ELS_Phil_T (w=0.5) | 964.2 | 959.3 | 0.585 | 0.740 |
| AlwaysRestricted | 600.2 | 531.2 | 0.650 | 0.800 |

**SARSOP − ELS gap (stationary): +44.8 units** (not significant at Bonferroni α*=0.0011).  
At U_T=0.70 parametric, SARSOP advantage is within Monte Carlo noise — the crossover is approaching.

---

## Benchmark 5 — GRACE-Based Depletion Monitoring (North China Plain)

### Physical Context

The North China Plain (NCP) deep Quaternary aquifer supports ~10% of China's agricultural output but loses 8–10 Gt/year (GRACE-TELLUS RL06). GRACE satellite observations — the only province-scale state proxy — aggregate over ~300 × 300 km footprints with σ ≈ 40–50 mm WE uncertainty (leakage error, measurement noise, surface-water confounding). This GRACE noise is the defining feature of B5. Non-stationarity: SSP5-8.5 demand increase at step 15. T-uncertainty (U_T ≈ 0.80) arises from both GRACE uncertainty and CMIP6 ensemble spread in future recharge.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Surplus → θ₅ Exhausted, TWSA mm WE) |
| Actions M | 3 (maintain, restrict, emergency + conjunctive) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 |
| SIGMA_OBS | **45 mm WE** (widest Gaussian uncertainty in parametric suite) |
| H_MEAN | [100, 20, −60, −160, −280] mm WE |
| L_PHIL | 0.5 × L(σ=35 mm, GRACE gridded) + 0.5 × L(σ=60 mm, basin-scale) |
| U_MIN | −600.0 |
| T_shift delta | 0.18 / 0.14 / 0.08 per action |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_S | **794.3** | 784.4 | 0.675 | 0.810 |
| SARSOP | 698.1 | 663.5 | 0.630 | 0.830 |
| ELS_Phil_T (w=0.5) | 653.6 | 667.5 | 0.670 | 0.785 |
| AlwaysRestricted | 352.5 | 264.5 | 0.770 | 0.915 |

**SARSOP − ELS gap (stationary): +44.4 units** (not significant; p>0.05).  
Wide GRACE noise (σ=45 mm WE) makes the LL ratio signal unreliable — adaptive w harmful here (ΔP_fail = −0.100 stationary).

---

## Benchmark 6 — Dual-Porosity Karst Aquifer

### Physical Context

Dinaric Karst / Mediterranean-type karst aquifer where the dual-porosity structure — a fast conduit network and a slow porous matrix — creates **structural model uncertainty**. T is not a fixed matrix with uncertain parameters; the functional form of T is itself unknown, depending on whether the conduit or matrix regime dominates at any given time. The agent cannot observe which regime is active; observations are spring discharge anomalies with compounded conduit/matrix noise. Non-stationarity: Mediterranean/Dinaric drought onset at step 15 causes conduit desiccation.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Surplus → θ₅ Spring failure / saltwater intrusion) |
| Actions M | 3 (a₁ Maintain, a₂ Restrict, a₃ Emergency cessation + recharge) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 |
| SIGMA_OBS | 38 L/s-equiv (dual-porosity structural noise) |
| H_MEAN | [80, 20, −30, −90, −180] L/s spring discharge anomaly |
| L_PHIL | 0.5 × L(σ=25 conduit) + 0.5 × L(σ=55 matrix) |
| U_MIN | −800.0 (saltwater intrusion: irreversible, highest penalty in suite) |

### Reward Matrix R[action, state]

| Action | θ₁ Surplus | θ₂ Normal | θ₃ Reduced | θ₄ Intermittent | θ₅ Failed |
|---|---|---|---|---|---|
| a₁ Maintain | +90 | +55 | −20 | −180 | **−800** |
| a₂ Restrict | −20 | +45 | +75 | +55 | −120 |
| a₃ Emergency | −150 | −70 | +25 | +100 | +80 |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| MPC | **851.7** | 821.3 | 0.740 | 0.845 |
| SDP_S | 837.0 | 825.6 | 0.740 | 0.870 |
| InfoGap | 819.4 | 796.1 | **0.645** | 0.800 |
| SARSOP | 695.2 | 671.3 | 0.695 | 0.860 |
| ELS_Phil_T (w=0.5) | 652.6 | 657.4 | 0.705 | 0.845 |

**SARSOP − ELS gap (stationary): +42.6 units** (within MC noise; smallest ELS–SARSOP gap in suite).  
Key finding: pure static ELS (w=0) collapses to U_cum=96 — static belief update is non-viable under structural T uncertainty. InfoGap achieves lowest P_fail (0.645) in the suite — deep structural uncertainty is the setting where info-gap is most precisely applicable.

---

## Benchmark 7 — Coastal Saltwater Intrusion (Tipping Point)

### Physical Context

Coastal aquifer saltwater intrusion in the Gaza Strip and the Dutch PWNT coastal dune system. The defining feature is a **tipping-point T structure** at state θ₃ (approaching intrusion): once the saltwater interface advances past the critical zone, recovery is hysteretically harder than the intrusion (asymmetric recovery). Non-stationarity: sea-level rise at step 15 amplifies the tipping hazard preferentially at θ₃. Observation model: log-normal chloride concentration (first non-Gaussian observation model in the suite).

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Fresh <150 mg/L Cl → θ₅ Saline >3000 mg/L Cl) |
| Actions M | 3 (a₁ Continue, a₂ Reduce 30%, a₃ Reduce 60% + injection) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 |
| SIGMA_OBS | 0.50 (log-space σ, log-normal chloride model) |
| OBS_BINS | linspace(ln 30, ln 10000, 21) |
| U_MIN | −700.0 (desalination + rehabilitation cost) |

### Reward Matrix R[action, state]

| Action | θ₁ Fresh | θ₂ Marginal | θ₃ Approaching | θ₄ Compromised | θ₅ Saline |
|---|---|---|---|---|---|
| a₁ Continue | +100 | +65 | +10 | −200 | −700 |
| a₂ Reduce 30% | +45 | +55 | +60 | −50 | −300 |
| a₃ Reduce 60% + inject | −80 | −20 | +50 | +100 | +150 |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_S | 1326.9 | 1303.2 | **0.490** | 0.595 |
| **ELS_Phil_T (w=0.5)** | **1304.2** | **1339.6** | 0.555 | 0.685 |
| SARSOP | 1217.1 | 1236.7 | 0.575 | 0.735 |
| InfoGap | 1115.7 | 1110.2 | **0.425** | **0.475** |
| AlwaysRestricted | −517.7 | −648.4 | 0.615 | 0.655 |

**SARSOP − ELS gap (stationary): −87.1 units, CI [−155, −15], p<0.01** — largest ELS advantage in the suite on the stationary condition.  
Gap widens to −102.9 under nonstationary forcing. This is the first benchmark where ELS_Phil_T beats SARSOP on the stationary condition.

---

## Benchmark 8 — Transboundary Aquifer: Stampriet STAS (Multi-Actor)

### Physical Context

The Stampriet Transboundary Aquifer System (STAS), shared by Namibia, Botswana, and South Africa. The defining feature is **endogenous game-theoretic T uncertainty**: T depends not on climate or geology but on what the other two countries extract. Unlike all prior benchmarks where T uncertainty is exogenous, B8 T uncertainty is generated by the rational strategies of other agents who observe the same GRACE signal and respond strategically. Three T regimes: COOP (voluntary cooperation), NEUTRAL (Nash equilibrium, T_stat), DEFECT (governance breakdown, T_shift). Non-stationarity: drought-induced governance breakdown (defection) at step 15.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Surplus TWSA>+50 mm WE → θ₅ Depleted <−300 mm WE) |
| Actions M | 3 (a₁ Unrestricted, a₂ Cooperative 25%+diplomacy, a₃ Emergency 60%+SADC) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 |
| SIGMA_OBS | 42 mm WE (GRACE + Kalahari lateral heterogeneity) |
| U_MIN | −600.0 (depletion + transboundary conflict) |

### Reward Matrix R[action, state]

| Action | θ₁ Surplus | θ₂ Balanced | θ₃ Stressed | θ₄ Critical | θ₅ Depleted |
|---|---|---|---|---|---|
| a₁ Unrestricted | +80 | +50 | −20 | −150 | −600 |
| a₂ Cooperative | +30 | +45 | +65 | +30 | −150 |
| a₃ Emergency + SADC | −80 | −30 | +30 | +80 | +120 |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_S | 913.4 | 930.6 | 0.580 | 0.775 |
| RDM | 922.3 | **961.5** | 0.585 | 0.750 |
| **ELS_Phil_T (w=0.5)** | **875.3** | **921.3** | 0.615 | 0.770 |
| SARSOP | 797.8 | 834.4 | 0.615 | 0.800 |
| SARSOP_Misspec | 841.6 | 845.6 | 0.650 | 0.785 |

**SARSOP − ELS gap (stationary): −77.4 units, p<0.01**.  
ELS_Phil_T (875) outperforms SARSOP (798) by +77 pts stationary and +87 pts nonstationary. SARSOP's alpha vectors, precomputed under the Nash equilibrium T, cannot adapt when governance breaks down.

---

## Benchmark 9 — Glacier–Groundwater Coupling: HKH / Indus Basin

### Physical Context

Indus Basin alluvial aquifer recharged by Hindu Kush–Himalaya (HKH) glacial and snowmelt, supporting ~230 million people in Pakistan, India, Afghanistan, and China. GRACE-FO and WAPDA monitoring show progressive TWSA decline since 2003. CMIP6 HKH ensemble shows ±40% inter-model spread in future meltwater runoff — the highest inter-model uncertainty globally. The defining feature is **continuous non-stationarity**: unlike all prior benchmarks where T switches at a discrete step, B9 uses a linear time-interpolation throughout the horizon.

```
T(t) = (1 − α(t)) · T_stat + α(t) · T_shift
α(t) = t / (T − 1)    [0 at t=0 → 1 at t=T-1]
```

No CLIMATE_SWITCH_STEP — T drifts continuously from ~2020 (T_stat) to ~2100 (T_shift). This is the only benchmark in the suite with this structure.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Recharged TWSA>+50 → θ₅ Depleted TWSA<−260 mm WE) |
| Actions M | 3 (a₁ Unrestricted, a₂ Restricted 40%, a₃ Emergency + conjunctive) |
| Horizon T | 30 |
| SIGMA_OBS | 48 mm WE (GRACE-FO + HKH terrain correction; second largest in suite) |
| H_MEAN | [80, 20, −60, −180, −340] mm WE |
| L_PHIL | 0.5 × L_GRACE_mascon(σ=38) + 0.5 × L_WAPDA_bore(σ=62) |
| U_MIN | −700.0 |
| T_shift delta | 0.14 / 0.10 / 0.06 per action |

### Reward Matrix R[action, state]

| Action | θ₁ Recharged | θ₂ Adequate | θ₃ Stressed | θ₄ Critical | θ₅ Depleted |
|---|---|---|---|---|---|
| a₁ Unrestricted | +85 | +55 | −10 | −200 | −700 |
| a₂ Restricted 40% | +40 | +50 | +70 | +20 | −200 |
| a₃ Emergency + conjunctive | −70 | −20 | +40 | +100 | +150 |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_NS | **1063.2** | — | 0.745 | — |
| **ELS_Phil_T (w=0.5)** | **994.5** | **821.0** | 0.815 | 0.940 |
| SARSOP | 931.5 | 710.4 | 0.805 | 0.955 |
| SARSOP_Misspec | 967.5 | 768.5 | 0.840 | 0.965 |

**SARSOP − ELS gap (stationary): −63.0 units, p<0.01**.  
Gap widens to −110.6 under continuous nonstationary forcing. SARSOP's alpha-vectors become progressively suboptimal as T(t) drifts away from T_stat; ELS_Phil_T's T-static blend never fully commits to T_stat.

---

## Benchmark 10 — Data-Scarce Pastoral Aquifer: Sahel / Lake Chad Basin

### Physical Context

Shallow Quaternary aquifer in the Lake Chad Basin (LCB), supporting ~45 million people in Chad, Niger, Nigeria, and Cameroon. GRACE-TELLUS shows TWSA decline of −8 to −12 mm WE/year since 2002. With ≤3 bore-wells per 10,000 km² and records ≤15 years, the entire LCB monitoring network yields only ~50 usable annual state-transition observations. T cannot be reliably estimated from available data — this is **maximum model uncertainty (U_T ≈ 1.0)**. The T_misspec is generated via a Dirichlet posterior with n_total=50 observations, representing the best-achievable T estimate under data scarcity. SARSOP solved on this Dirichlet T is the only feasible POMDP baseline — the realistic practitioner comparison.

### Environment Parameters

| Parameter | Value |
|---|---|
| States N | 5 (θ₁ Normal TWSA>+60 mm → θ₅ Depleted TWSA<−380 mm WE) |
| Actions M | 3 (a₁ Unrestricted, a₂ Managed 20%+bore rehab, a₃ Emergency 50%+LCBC) |
| Horizon T | 30 |
| CLIMATE_SWITCH_STEP | 15 (sustained Sahel drought, SSP5-8.5) |
| SIGMA_OBS | **55 mm WE** (widest in suite: GRACE footprint + OSS bore sparsity + mascon contamination) |
| H_MEAN | [60, 0, −80, −200, −380] mm WE |
| L_PHIL | 0.5 × L_GRACE(σ=45) + 0.5 × L_OSS_bore(σ=70) |
| U_MIN | −500.0 |
| T_misspec | Dirichlet posterior (n_total=50, n_per_row≈3; SEED+10000) |
| T_shift delta | 0.18 / 0.13 / 0.08 per action (strongest shift in suite) |

### Reward Matrix R[action, state]

| Action | θ₁ Normal | θ₂ Moderate | θ₃ Stressed | θ₄ Crisis | θ₅ Depleted |
|---|---|---|---|---|---|
| a₁ Unrestricted | +70 | +40 | −15 | −180 | −500 |
| a₂ Managed 20% | +25 | +40 | +60 | +15 | −150 |
| a₃ Emergency 50% | −60 | −15 | +35 | +90 | +100 |

### Key Results (N_MC=200, γ=0.97)

| Method | U_cum stat | U_cum NS | P_fail stat | P_fail NS |
|---|---|---|---|---|
| SDP_NS | **934.7** | — | 0.820 | — |
| **ELS_Phil_T (w=0.5)** | **888.8** ±35 | **937.0** | 0.905 | 0.945 |
| SARSOP | 832.6 | 720.2 | 0.890 | 0.960 |
| **SARSOP_Misspec** | **761.0** ±39 | 769.0 | 0.925 | 0.975 |
| AlwaysRestricted | −204.0 | −360.0 | 0.960 | 0.975 |

**ELS_Phil_T vs SARSOP_Misspec (realistic baseline): +128 units stationary, +168 units nonstationary** (both p<0.01, non-overlapping 95% bootstrap CIs).  
This is the most policy-relevant result in the suite: in data-scarce settings, T-agnosticism is not a compromise but the superior strategy. AlwaysRestricted collapses to negative utility because the reward structure includes implementation costs — continued restriction at depleted state θ₅ yields −150 (loss from mismatched policy), whereas optimal recovery (a₃) yields +100.

---

## Cross-Benchmark Summary

### Price-of-Robustness Curve (SARSOP − ELS_Phil_T, stationary)

| BM | U_T | Type | Gap (SARSOP − ELS stat) | Significant? |
|---|---|---|---|---|
| B1 | 0.00 | Parametric | **+170** (CI [+115, +226]) | p<0.001 |
| B2 | 0.50 | Parametric | +175 | p<0.001 |
| B3 | 0.60 | Parametric | **−66** (ELS wins) | p<0.05 |
| B4 | 0.70 | Parametric | +45 | not sig. |
| B5 | 0.80 | Parametric | +44 | not sig. |
| B6 | 0.90 | Structural | +43 | not sig. |
| B7 | 0.70 | Structural | **−87** (CI [−155, −15]) | p<0.01 |
| B8 | 0.80 | Structural | **−77** | p<0.01 |
| B9 | 0.90 | Structural | **−63** | p<0.01 |
| B10* | 1.00 | Structural | **−128** (vs SARSOP_Misspec) | p<0.01 |

\* B10 uses SARSOP_Misspec as the only feasible POMDP baseline.

### Adaptive-w Operational Window

| BM | U_T | σ_obs | ΔP_fail (stat) | ΔP_fail (NS) | Verdict |
|---|---|---|---|---|---|
| B1 | 0.00 | 4.0 m | +0.010 | +0.010 | Neutral |
| B2 | 0.50 | 35 GL | +0.025 | +0.010 | Marginal benefit |
| B3 | 0.60 | 28 μg/L | +0.020 | +0.010 | Marginal benefit |
| B4 | 0.70 | 35 GL | −0.030 | **+0.025** | Marginal NS benefit |
| B5 | 0.80 | **45 mm WE** | **−0.100** | **+0.010** | **Harmful stat** |
| B6 | 0.90 | 38 L/s | ~0 | −0.035 | Saturation |
| B7 | 0.70 | log-norm | neutral | neutral | No benefit |
| B8 | 0.80 | 42 mm WE | neutral | neutral | No benefit |
| B9 | 0.90 | 48 mm WE | **+0.015** | **+0.015** | **Beneficial** |
| B10 | 1.00 | **55 mm WE** | **+0.045** | **+0.025** | **Beneficial** |

**Decision rule for ELS_Adapt activation:** Score ≥ 2 (one point each for U_T ≥ 0.90, documented tipping / regime behaviour, σ_obs < 35 mm WE equivalent) → activate ELS_Adapt. Score ≤ 1 → use ELS_Phil_T (w=0.5 fixed).

---

## Evaluation Protocol

| Element | Specification |
|---|---|
| Episodes | N_MC = 200 per method per condition (stationary + nonstationary) |
| Discount | γ = 0.97 |
| Random seed | SEED = 2024 (collision-free episode seeding) |
| Pairwise test | Wilcoxon signed-rank, two-sided, α=0.05, Bonferroni k=45 → α*=0.0011 |
| Confidence intervals | Percentile bootstrap, B=2000 resamples, `numpy.random.default_rng(42)` |
| Common evaluation utility | U_eval(a, θ) = R(a, θ) (raw reward, no framework augmentation) |
| Convergence criterion | Rolling-window SE ratio SE(N)/SE(25) < 0.10 at N=200 (satisfied for all BMs) |

---

## Data and Code

All benchmark environments are self-contained Python modules (`pomdp_env_bN.py`) with no external POMDP library dependency. Numerical results are stored in per-benchmark `raw_results_bN.npz` files. Publication figures are in `P_Base/image/` (final versions: `fig1_`–`fig4_`).

Data sources per benchmark are listed in Supplementary Section SI-E of the paper.

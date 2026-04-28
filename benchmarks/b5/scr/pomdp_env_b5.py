# =============================================================================
# pomdp_env_b5.py  —  North China Plain GRACE-Based Groundwater POMDP
# Project  : ELS_NEW / P_Base5  (Benchmark 5 — North China Plain)
# Plan ref : P_Base/docs/NW_benchmarks.md §Benchmark 5
# Date     : 2026-04-25
# Usage    : import pomdp_env_b5 as env
# Data src : GRACE-TELLUS TWS anomaly data (NASA PO.DAAC, RL06)
#            Feng et al. (2013) GRACE: loss of GW in NCP, Geophys Res Lett
#            Cao et al. (2016) NCP GW depletion, J Hydrol
#            Zheng et al. (2010) Responses of streamflow to climate change NCP
#            Gleeson et al. (2012) Groundwater sustainability strategies, NatGeosci
# =============================================================================
"""
POMDP environment for the North China Plain (NCP) GRACE-based groundwater benchmark.
Benchmark 5 in the ELS NW benchmark suite.

Physical context
----------------
The North China Plain (Hai River Basin) supports ~10% of China's agricultural
output with only ~3% of national water resources.  Groundwater accounts for
~70% of irrigation supply; GRACE-TELLUS data (2002–2023) shows depletion of
−8 to −10 Gt/year in the deep Quaternary aquifer.  Provincial quota systems,
crop switching programmes (wheat→maize), and managed aquifer recharge via South-
to-North Water Transfer Project diversions constitute the primary interventions.

GRACE observations provide the state proxy: terrestrial water storage anomaly
(TWSA) aggregated over ~300 × 300 km footprint with σ ≈ 40–50 mm WE uncertainty
(leakage + measurement noise).  This large observation noise is the defining
feature of B5 and the primary driver of U_T ≈ 0.7–0.9 — the highest in the suite.

Differences from Benchmark 4 (P_Base4):
  * Domain         : NCP provincial quota + crop management decisions
  * State space    : 5 aquifer depletion stages (surplus → exhausted)
  * Action space   : 3 interventions (maintain, restrict quotas, emergency)
  * Observations   : GRACE TWSA (noisy satellite, σ=45 mm WE — widest in suite)
  * Non-stationarity: SSP5-8.5 warming increases irrigation demand at t=15
  * Dynamics       : BIDIRECTIONAL — emergency restriction + recharge achieves recovery
  * Horizon        : T=30 (30-year provincial water plan)
  * Primary metric : U_cum in $bn/year net agricultural benefit equivalent
  * T-uncertainty  : HIGHEST (U_T ≈ 0.7–0.9) — GRACE noise + sparse wells + unknown
    pumping behaviour make T the least reliable in the benchmark suite

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, SSP5-8.5 warming increases evapotranspiration by
~5–8%, driving larger irrigation withdrawals.  This increases net depletion
rate: T_stat → T_shift represents the additional +0.18/0.14/0.08 depletion
shift per action, calibrated to CMIP6 NCP temperature projections.

State space (TWSA relative to sustainable storage level)
---------
θ₁ : Surplus        (TWSA > +100 mm WE above sustainable) — full extraction OK
θ₂ : Sustainable    (−20 to +100 mm WE)                   — manageable depletion
θ₃ : Stressed       (−100 to −20 mm WE)                   — active quota needed
θ₄ : Critical       (−200 to −100 mm WE)                  — emergency management
θ₅ : Exhausted      (TWSA < −200 mm WE)                   — irreversible damage

TWSA = Terrestrial Water Storage Anomaly (mm WE, GRACE RL06)

Action space
------------
a₁ : Maintain       (current quota, no policy change)         — max economic return
a₂ : Restrict       (seasonal quota reduction + crop switch)   — moderate cost
a₃ : Emergency      (deep restriction + recharge enhancement)  — highest cost

Reward function
---------------
Net economic benefit ($bn/year, normalised to $k/year-equiv):
  Positive: agricultural revenue from irrigation + food security value
  Negative: groundwater depletion penalty (ecosystem, future supply) + restriction cost

Calibration to NCP agricultural economics (Zheng et al. 2010; Cao et al. 2016):
  Full extraction (θ₁,a₁): max agricultural benefit ≈ +$80k-equiv/unit
  No-action during exhaustion (θ₅,a₁): ecosystem penalty ≈ −$500k-equiv/unit
  Emergency restriction (θ₅,a₃): avoids −$500k at ~$120k cost → net +$60k-equiv
  Unnecessary emergency (θ₁,a₃): ~−$120k/unit economic loss

Aliases for shared-code compatibility
--------------------------------------
T_stat  = T_B5_STAT  (long-term average dynamics — "stationary" regime)
T_shift = T_B5_SHIFT (SSP5-8.5 increased demand — "nonstationary" after step 15)
T_misspec = undercalibrated depletion model (+22% underestimate)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year provincial water plan
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # SSP5-8.5 diverges from long-term average

N = 5   # aquifer depletion stages
M = 3   # intervention actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (TWSA > +100 mm WE) — full extraction available",
    "θ₂ Sustainable (−20 to +100 mm WE) — manageable depletion",
    "θ₃ Stressed (−100 to −20 mm WE) — active quota needed",
    "θ₄ Critical (−200 to −100 mm WE) — emergency management",
    "θ₅ Exhausted (TWSA < −200 mm WE) — irreversible damage risk",
]
FAILURE_STATE = 4   # θ₅ — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Maintain (current quota, no policy change)",
    "a₂ Restrict (seasonal quota reduction + crop switching)",
    "a₃ Emergency (deep restriction + recharge enhancement)",
]
ACTION_COST = np.array([0.0, 35.0, 120.0])   # $k-equiv/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $k-equiv/year net agricultural benefit (normalised)
#
# Calibration (NCP agricultural economics, GRACE depletion cost):
#   a₁ Maintain: max agricultural revenue but depletion penalty in θ₃–θ₅
#   a₂ Restrict: quota reduction cost offset by depletion prevention in θ₃–θ₄
#   a₃ Emergency: recharge enhancement cost but avoids irreversible damage in θ₄–θ₅
#
# Note: R[a₁, θ₅] = -500 — most severe penalty in suite (irreversible depletion)
#       R[a₃, θ₅] = +60  — emergency avoids −500 at ~$120k cost
#       R[a₁, θ₁] = +80  — max agricultural benefit in surplus
#       R[a₃, θ₁] = -120 — unnecessary emergency restriction in surplus
# ---------------------------------------------------------------------------
R = np.array([
    [  80.0,  50.0,  -30.0, -200.0, -500.0],   # a₁ Maintain
    [ -30.0,  40.0,   70.0,   50.0, -100.0],   # a₂ Restrict
    [-120.0, -60.0,   20.0,   90.0,   60.0],   # a₃ Emergency
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices (long-term average NCP dynamics)  T_B5_STAT[action, s, s']
#
# Key properties:
#  - BIDIRECTIONAL: emergency restriction + recharge achieves recovery from any stage
#  - a₁ (maintain): continued pumping; θ₅ near-absorbing but not fully absorbing
#  - a₂ (restrict): slow recovery in θ₃; containment in θ₄
#  - a₃ (emergency): South-to-North diversion + quota cut; meaningful recovery in θ₄–θ₅
#  - Calibrated to published NCP depletion rates (Feng 2013; Cao 2016)
#    (−8 to −10 Gt/year observed; ~0.5–1 m/year deep aquifer decline)
# ---------------------------------------------------------------------------
_T_B5_STAT_0 = np.array([        # a₁ Maintain (current quota)
    [0.55, 0.30, 0.12, 0.03, 0.00],   # θ₁: mostly surplus, slow depletion
    [0.05, 0.50, 0.35, 0.09, 0.01],   # θ₂: moderate depletion with current quotas
    [0.01, 0.05, 0.45, 0.38, 0.11],   # θ₃: significant depletion without restriction
    [0.00, 0.01, 0.08, 0.50, 0.41],   # θ₄: heavy depletion — critical breach likely
    [0.00, 0.00, 0.02, 0.10, 0.88],   # θ₅: near-absorbing exhausted state
], dtype=float)

_T_B5_STAT_1 = np.array([        # a₂ Restrict (quota + crop switching)
    [0.70, 0.22, 0.07, 0.01, 0.00],   # θ₁: surplus maintained
    [0.12, 0.58, 0.25, 0.05, 0.00],   # θ₂: stable, slow recovery
    [0.04, 0.18, 0.55, 0.20, 0.03],   # θ₃: partial containment + recovery
    [0.01, 0.04, 0.20, 0.60, 0.15],   # θ₄: slow recovery under restriction
    [0.00, 0.01, 0.05, 0.22, 0.72],   # θ₅: limited recovery — deep restriction needed
], dtype=float)

_T_B5_STAT_2 = np.array([        # a₃ Emergency (deep restriction + recharge)
    [0.78, 0.18, 0.03, 0.01, 0.00],   # θ₁: surplus well maintained
    [0.30, 0.52, 0.15, 0.03, 0.00],   # θ₂: strong recovery to surplus
    [0.10, 0.35, 0.42, 0.12, 0.01],   # θ₃: good recovery with recharge
    [0.03, 0.13, 0.38, 0.40, 0.06],   # θ₄: meaningful recovery achievable
    [0.00, 0.02, 0.15, 0.40, 0.43],   # θ₅: recovery with S-N diversion + quota cut
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B5_STAT_0), ("STAT_1", _T_B5_STAT_1),
                   ("STAT_2", _T_B5_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B5_{_tag} rows not sum to 1: {_rs}"

T_B5_STAT = np.stack([_T_B5_STAT_0, _T_B5_STAT_1, _T_B5_STAT_2], axis=0)  # (3,5,5)


def _apply_demand_increase(T_base: np.ndarray, delta: float = 0.18) -> np.ndarray:
    """
    Apply SSP5-8.5 irrigation demand increase to a single 5×5 transition matrix.

    For each non-final state s (0..3): subtract delta from diagonal (self-loop),
    add delta to next-worse state (s+1). Final row (θ₅) left unchanged.
    Clips negatives and renormalises.

    Physical interpretation: SSP5-8.5 warming (+2–4°C by 2050 in NCP) increases
    evapotranspiration, driving larger groundwater withdrawals even under same quota,
    pushing states toward deeper depletion stages.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_shift: SSP5-8.5 increased demand after CLIMATE_SWITCH_STEP=15
# a₁ delta=0.18: largest increase — no policy response to warming
# a₂ delta=0.14: quota helps but warming partially offsets restriction benefit
# a₃ delta=0.08: emergency + recharge partially compensates warming demand
T_B5_SHIFT = np.stack([
    _apply_demand_increase(_T_B5_STAT_0, delta=0.18),
    _apply_demand_increase(_T_B5_STAT_1, delta=0.14),
    _apply_demand_increase(_T_B5_STAT_2, delta=0.08),
], axis=0)

# T-misspecification: practitioner uses model that underestimates depletion rate
# (+22% demand increase misestimate — uses historical depletion calibrated
# to pre-2010 data that underestimates accelerating depletion)
T_misspec = np.stack([
    _apply_demand_increase(_T_B5_STAT_0, delta=0.22),
    _apply_demand_increase(_T_B5_STAT_1, delta=0.20),
    _apply_demand_increase(_T_B5_STAT_2, delta=0.10),
], axis=0)

# Aliases for shared-code compatibility
T_stat  = T_B5_STAT
T_shift = T_B5_SHIFT

# ---------------------------------------------------------------------------
# Observation model
# GRACE TWSA proxy (mm WE, relative to sustainable storage level)
# H_MEAN: mean TWSA per state (θ₁ highest storage → θ₅ lowest)
# SIGMA_OBS: GRACE leakage + measurement noise (σ = 45 mm WE)
#            Wider than B4 (35) — GRACE footprint aggregation dominates
# ---------------------------------------------------------------------------
H_MEAN    = np.array([100.0, 20.0, -60.0, -160.0, -280.0])  # mm WE TWSA proxy
SIGMA_OBS = 45.0                                               # GRACE uncertainty
OBS_BINS  = np.linspace(-380.0, 200.0, 21)                    # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                                 # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])       # (20,)

# Likelihood L[θ, o] = P(obs bin o | depletion state θ) — shape (N, N_OBS)
_L = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=SIGMA_OBS)
    _cdf_lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=SIGMA_OBS)
    _L[_s]  = _cdf_hi - _cdf_lo

_L[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
_L[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
_L /= _L.sum(axis=1, keepdims=True)
LIKELIHOOD = _L   # (5, 20)

# ---------------------------------------------------------------------------
# ELS likelihood and prior variants
# L_PRES: single GRACE RL06 product (σ=45 — primary data source)
# L_PHIL: model-averaged (GRACE gridded σ=35 + basin-scale model σ=60)
#         Widest model spread in suite — reflects GRACE aggregation uncertainty
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_M1 = np.zeros((N, N_OBS), dtype=float)
_L_M2 = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi_m1 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=35.0)
    _cdf_lo_m1 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=35.0)
    _cdf_hi_m2 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=60.0)
    _cdf_lo_m2 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=60.0)
    _L_M1[_s]  = _cdf_hi_m1 - _cdf_lo_m1
    _L_M2[_s]  = _cdf_hi_m2 - _cdf_lo_m2

for _mat in (_L_M1, _L_M2):
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_M1 + 0.5 * _L_M2   # (5, 20)

H_MAX_NATS = float(np.log(N))

# PRIOR_PHIL: uniform — no prior assumption about NCP state at planning start
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward stressed/critical states
# (NCP is already heavily depleted; planning typically starts under active stress)
PRIOR_PRES = np.array([0.05, 0.15, 0.30, 0.35, 0.15], dtype=float)
PRIOR_PRES = PRIOR_PRES / PRIOR_PRES.sum()

# ---------------------------------------------------------------------------
# Environment API
# ---------------------------------------------------------------------------

def reset(rng: np.random.Generator) -> tuple[int, np.ndarray]:
    """Begin new episode; initial state drawn uniformly."""
    initial_state = int(rng.integers(0, N))
    b0 = np.full(N, 1.0 / N, dtype=float)
    return initial_state, b0


def step(
    state: int,
    action: int,
    t: int,
    rng: np.random.Generator,
) -> tuple[int, int, float]:
    """
    Advance one step using T_B5_STAT (t < CLIMATE_SWITCH_STEP) or
    T_B5_SHIFT (t >= CLIMATE_SWITCH_STEP — SSP5-8.5 demand increase).
    """
    T_use      = T_B5_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B5_STAT
    next_state = int(rng.choice(N, p=T_use[action, state]))
    obs_idx    = int(rng.choice(N_OBS, p=LIKELIHOOD[next_state]))
    reward     = float(R[action, next_state])
    return next_state, obs_idx, reward


def update_belief(b: np.ndarray, obs_idx: int) -> np.ndarray:
    """Static Bayesian belief update (ELS default)."""
    b_new = LIKELIHOOD[:, obs_idx] * b
    total = b_new.sum()
    return b_new / total if total > 1e-300 else b.copy()


def markov_update_belief(
    b: np.ndarray, obs_idx: int, action: int, t: int
) -> np.ndarray:
    """Full Markovian belief update (predict + correct)."""
    T_use  = T_B5_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B5_STAT
    b_pred = T_use[action].T @ b
    b_new  = LIKELIHOOD[:, obs_idx] * b_pred
    total  = b_new.sum()
    if total < 1e-300:
        return b_pred / b_pred.sum()
    return b_new / total


def expected_reward(b: np.ndarray, action: int) -> float:
    """Single-period expected reward under belief b."""
    return float(b @ R[action])


def entropy(b: np.ndarray) -> float:
    """Shannon entropy H(b) in nats."""
    mask = b > 0
    return float(-np.sum(b[mask] * np.log(b[mask])))


def entropy_norm(b: np.ndarray) -> float:
    """Normalised Shannon entropy H_norm = H(b) / log(N) ∈ [0, 1]."""
    return entropy(b) / np.log(N)

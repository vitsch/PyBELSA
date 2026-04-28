# =============================================================================
# pomdp_env_b4.py  —  Murray-Darling Basin Groundwater SDL POMDP Environment
# Project  : ELS_NEW / P_Base4  (Benchmark 4 — Murray-Darling Basin)
# Plan ref : P_Base/docs/NW_benchmarks.md §Benchmark 4
# Date     : 2026-04-24
# Usage    : import pomdp_env_b4 as env
# Data src : MDBA SDL Accounting data + CMIP6 ensemble projections (MDB region)
#            MDBA (2019) Basin Plan Evaluation; CSIRO (2022) CMIP6 downscaled MDB
#            Doble et al. (2017) Groundwater SDLs, Water Resour. Res.
#            Leblanc et al. (2012) GRACE MDB groundwater decline estimates
# =============================================================================
"""
POMDP environment for the Murray-Darling Basin Groundwater SDL benchmark.
Benchmark 4 in the ELS NW benchmark suite.

Physical context
----------------
The Murray-Darling Basin (MDB) groundwater system is managed under the Basin
Plan (2012) Sustainable Diversion Limits (SDLs) — legally binding annual caps on
groundwater extraction designed to recover overallocated aquifers and maintain
environmental flows.  The decision-maker chooses annual extraction allocation
levels to balance agricultural economic benefit against long-run aquifer health.

Under CMIP6 ensemble projections (SSP2-4.5 and SSP5-8.5), MDB groundwater recharge
declines by 5–25% by 2050, creating significant uncertainty in the T matrix.
The SDL adaptive management mechanism (Basin Plan s.6.13) provides an existing
rule-based baseline for comparison.

Differences from Benchmark 3 (P_Base3):
  * Domain         : MDB groundwater SDL management (annual allocation decisions)
  * State space    : 5 aquifer storage stages relative to SDL buffer (surplus → critical)
  * Action space   : 3 allocation levels (unrestricted, SDL-capped, emergency reduction)
  * Observations   : Noisy groundwater level readings (monitoring bore + satellite proxy)
  * Non-stationarity: Drier SSP5-8.5 conditions increase depletion rate at t=15
  * Dynamics       : BIDIRECTIONAL — emergency reduction achieves recovery from any stage
  * Horizon        : T=30 (30-year annual SDL management programme)
  * Primary metric : U_cum in GL/year net sustainable yield equivalent
  * T-uncertainty  : HIGHER (U_T ≈ 0.6–0.8) — CMIP6 ensemble spread (6–18% recharge
    variation across GCMs) makes T less reliable than B3 plume transport model

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, CMIP6 SSP5-8.5 trajectories diverge sharply from
SSP2-4.5 median, reducing groundwater recharge by an additional 8–12% and
increasing irrigation demand.  T_stat → T_shift represents this recharge
decline, calibrated to CSIRO CMIP6 downscaled projections for the MDB.

State space
-----------
θ₁ : Surplus          (storage > 150 % SDL buffer) — full allocation available
θ₂ : Adequate         (100–150 % SDL buffer)        — normal SDL operations
θ₃ : Near-SDL         (70–100 % SDL buffer)         — caution, trend monitoring
θ₄ : Below-SDL        (40–70 % SDL buffer)          — active SDL management
θ₅ : Critical         (< 40 % SDL buffer)           — emergency SDL restriction

SDL = Sustainable Diversion Limit (Basin Plan 2012 extraction cap per SDL unit)

Action space
------------
a₁ : Unrestricted     (full extraction at licence entitlement)  — max economic return
a₂ : SDL-restricted   (extraction capped at SDL entitlement)    — compliance mode
a₃ : Emergency        (30 % below SDL entitlement)              — maximum recovery

Reward function
---------------
Net sustainable yield equivalent (GL/year, normalised to $k/year-equiv):
  Positive: agricultural benefit from water use + compliance bonus
  Negative: ecosystem/regulatory penalty for below-SDL conditions + economic cost
            of unnecessary restrictions

Calibration to MDBA SDL accounting:
  Full allocation (θ₁,a₁): ~$100k/GL equivalent economic benefit
  Below-SDL penalty (θ₅,a₁): ~$400k/GL equivalent regulatory + ecosystem penalty
  Emergency restriction (θ₁,a₃): ~$100k/GL unnecessary economic cost

Aliases for shared-code compatibility
--------------------------------------
T_stat  = T_B4_STAT  (SSP2-4.5 median — "stationary" regime)
T_shift = T_B4_SHIFT (SSP5-8.5 drier — "nonstationary" regime after step 15)
T_misspec = undercalibrated CMIP6 (+20% recharge decline — T-misspecification)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year annual SDL programme
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # step at which SSP5-8.5 diverges from SSP2-4.5

N = 5   # number of aquifer storage stages
M = 3   # number of allocation actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (> 150 % SDL buffer) — full allocation",
    "θ₂ Adequate (100–150 % SDL buffer) — normal operations",
    "θ₃ Near-SDL (70–100 % SDL buffer) — caution",
    "θ₄ Below-SDL (40–70 % SDL buffer) — active management",
    "θ₅ Critical (< 40 % SDL buffer) — emergency restriction",
]
FAILURE_STATE = 4   # θ₅ index — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Unrestricted (full licence entitlement)",
    "a₂ SDL-restricted (SDL cap active)",
    "a₃ Emergency reduction (30 % below SDL entitlement)",
]
ACTION_COST = np.array([0.0, 30.0, 100.0])   # $k/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: GL/year net sustainable yield equivalent ($k/year-equiv normalised)
#
# Calibration (MDBA SDL accounting):
#   a₁ Unrestricted: max economic return in θ₁-θ₂; regulatory penalty dominates θ₄-θ₅
#   a₂ SDL-restricted: moderate economic return; compliance benefit in θ₃-θ₄
#   a₃ Emergency: significant economic cost but avoids largest penalties; best in θ₄-θ₅
#
# Note: R[a₁, θ₅] = -400 — unrestricted use during critical = massive ecosystem penalty
#       R[a₃, θ₅] = +80  — emergency reduction during critical avoids $400 penalty
#       R[a₁, θ₁] = +100 — full allocation in surplus = maximum economic benefit
#       R[a₃, θ₁] = -100 — unnecessary emergency restriction in surplus = economic cost
# ---------------------------------------------------------------------------
R = np.array([
    [ 100.0,  60.0,  -10.0, -150.0, -400.0],   # a₁ Unrestricted
    [  -20.0,  50.0,   80.0,   60.0, -80.0],   # a₂ SDL-restricted
    [-100.0,  -40.0,   20.0,  100.0,  80.0],   # a₃ Emergency reduction
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices (SSP2-4.5 median — stable recharge regime)  T_B4_STAT[action, s, s']
#
# Key properties:
#  - BIDIRECTIONAL: recovery achievable from all states with emergency reduction
#  - a₁ (unrestricted): natural + anthropogenic depletion; θ₅ near-absorbing
#  - a₂ (SDL-restricted): containment within SDL buffer; slow recovery in θ₃-θ₄
#  - a₃ (emergency): significant recovery in all states; θ₅ not fully absorbing
#  - Calibrated to MDB alluvial aquifer dynamics (Doble et al. 2017)
#    (30-year SDL management horizon; CMIP6 SSP2-4.5 median recharge)
# ---------------------------------------------------------------------------
_T_B4_STAT_0 = np.array([        # a₁ Unrestricted (SSP2-4.5 median)
    [0.65, 0.25, 0.08, 0.02, 0.00],   # θ₁: mostly surplus, some depletion
    [0.10, 0.55, 0.28, 0.07, 0.00],   # θ₂: moderate depletion with unrestricted use
    [0.02, 0.10, 0.48, 0.32, 0.08],   # θ₃: significant depletion without restriction
    [0.00, 0.02, 0.10, 0.52, 0.36],   # θ₄: heavy depletion — SDL breach likely
    [0.00, 0.00, 0.03, 0.12, 0.85],   # θ₅: near-absorbing critical state
], dtype=float)

_T_B4_STAT_1 = np.array([        # a₂ SDL-restricted (SDL cap active)
    [0.75, 0.20, 0.04, 0.01, 0.00],   # θ₁: surplus well maintained
    [0.15, 0.60, 0.20, 0.05, 0.00],   # θ₂: stable with slow recovery
    [0.05, 0.20, 0.55, 0.18, 0.02],   # θ₃: moderate containment + recovery
    [0.01, 0.05, 0.22, 0.57, 0.15],   # θ₄: slow recovery, partial containment
    [0.00, 0.01, 0.06, 0.25, 0.68],   # θ₅: limited recovery at SDL cap
], dtype=float)

_T_B4_STAT_2 = np.array([        # a₃ Emergency reduction (30 % below SDL)
    [0.80, 0.17, 0.02, 0.01, 0.00],   # θ₁: surplus well maintained
    [0.35, 0.50, 0.13, 0.02, 0.00],   # θ₂: strong recovery to surplus
    [0.12, 0.38, 0.40, 0.09, 0.01],   # θ₃: good recovery efficiency
    [0.03, 0.15, 0.40, 0.37, 0.05],   # θ₄: meaningful recovery achievable
    [0.01, 0.04, 0.20, 0.38, 0.37],   # θ₅: significant recovery — 30% reduction
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B4_STAT_0), ("STAT_1", _T_B4_STAT_1),
                   ("STAT_2", _T_B4_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B4_{_tag} rows not sum to 1: {_rs}"

T_B4_STAT = np.stack([_T_B4_STAT_0, _T_B4_STAT_1, _T_B4_STAT_2], axis=0)  # (3,5,5)


def _apply_recharge_decline(T_base: np.ndarray, delta: float = 0.15) -> np.ndarray:
    """
    Apply SSP5-8.5 recharge decline to a single 5×5 transition matrix.

    For each non-final state s (0..3): subtract delta from diagonal (self-loop),
    add delta to next-worse state (s+1). Final row (θ₅) left unchanged.
    Clips negatives and renormalises.

    Physical interpretation: drier SSP5-8.5 conditions reduce groundwater recharge,
    increasing the probability of transitioning to a lower (more depleted) storage
    state and reducing the effectiveness of each allocation strategy.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_shift: SSP5-8.5 recharge decline after CLIMATE_SWITCH_STEP=15
# a₁ delta=0.15: large depletion increase without restriction
# a₂ delta=0.12: SDL cap less effective under drier conditions
# a₃ delta=0.07: emergency reduction partially compensates recharge loss
T_B4_SHIFT = np.stack([
    _apply_recharge_decline(_T_B4_STAT_0, delta=0.15),
    _apply_recharge_decline(_T_B4_STAT_1, delta=0.12),
    _apply_recharge_decline(_T_B4_STAT_2, delta=0.07),
], axis=0)

# T-misspecification ablation: practitioner uses undercalibrated CMIP6 model
# (+20% recharge decline — underestimates SSP5-8.5 drying trend)
T_misspec = np.stack([
    _apply_recharge_decline(_T_B4_STAT_0, delta=0.20),
    _apply_recharge_decline(_T_B4_STAT_1, delta=0.18),
    _apply_recharge_decline(_T_B4_STAT_2, delta=0.09),
], axis=0)

# Aliases for shared-code compatibility
T_stat  = T_B4_STAT
T_shift = T_B4_SHIFT

# ---------------------------------------------------------------------------
# Observation model
# Groundwater level proxy (GL-equiv relative to SDL baseline)
# H_MEAN: mean storage proxy per state (θ₁ highest storage → θ₅ lowest)
# SIGMA_OBS: monitoring bore + CMIP6-scale uncertainty (σ = 35 GL-equiv)
#            Wider than B3 (28) — CMIP6 ensemble model spread adds noise
# ---------------------------------------------------------------------------
H_MEAN    = np.array([150.0, 80.0, 10.0, -70.0, -180.0])   # GL-equiv storage proxy
SIGMA_OBS = 35.0                                              # observation noise
OBS_BINS  = np.linspace(-280.0, 250.0, 21)                   # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                                # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])      # (20,)

# Likelihood L[θ, o] = P(obs bin o | aquifer state θ)  — shape (N, N_OBS)
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
# L_PRES: single model (monitoring bore: σ=35)
# L_PHIL: model-averaged (careful survey bore: σ=27 + satellite/regional: σ=50)
#         Wider model spread than B3 (22+40) — reflects CMIP6 ensemble uncertainty
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_M1 = np.zeros((N, N_OBS), dtype=float)
_L_M2 = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi_m1 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=27.0)
    _cdf_lo_m1 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=27.0)
    _cdf_hi_m2 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=50.0)
    _cdf_lo_m2 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=50.0)
    _L_M1[_s]  = _cdf_hi_m1 - _cdf_lo_m1
    _L_M2[_s]  = _cdf_hi_m2 - _cdf_lo_m2

for _mat in (_L_M1, _L_M2):
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_M1 + 0.5 * _L_M2   # (5, 20)

H_MAX_NATS = float(np.log(N))

# PRIOR_PHIL: uniform — no prior assumption about MDB aquifer state at planning start
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward depleted states
# (SDL is typically invoked when storage is below adequate; planning starts in stress)
PRIOR_PRES = np.array([0.05, 0.20, 0.35, 0.30, 0.10], dtype=float)
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
    Advance one step using T_B4_STAT (t < CLIMATE_SWITCH_STEP) or
    T_B4_SHIFT (t >= CLIMATE_SWITCH_STEP — SSP5-8.5 drying).
    """
    T_use      = T_B4_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B4_STAT
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
    T_use = T_B4_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B4_STAT
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

# =============================================================================
# pomdp_env_b3.py  —  Pump-and-Treat Remediation POMDP Environment
# Project  : ELS_NEW / P_Base3  (Benchmark 3 — Gorelick Pump-and-Treat)
# Plan ref : P_Base/docs/experiment_plan.md §6.3
# Date     : 2026-04-24
# Usage    : import pomdp_env_b3 as env
# Data src : Calibrated synthetic based on published parameters from:
#            Gorelick et al. (1984) Water Resources Research 20(4):415–427
#            Gorelick et al. (1990) Groundwater 28(6):821–827
#            Reed et al. (2003) Adv. Water Resources 26:723–743
# =============================================================================
"""
POMDP environment for the Gorelick Pump-and-Treat Remediation benchmark.
Benchmark 3 in the ELS NW benchmark suite.

Physical context
----------------
A trichloroethylene (TCE) contamination plume has established in an alluvial
aquifer following an industrial solvent spill (Gorelick 1984 Stanford case).
The decision-maker chooses the annual pump-and-treat intensity to minimise
total remediation cost while achieving regulatory compliance.

Differences from Benchmark 2 (P_Base2):
  * Domain         : Plume remediation — annual pump-and-treat intensity decisions
  * State space    : 5 plume contamination stages (clean → severe regulatory exceedance)
  * Action space   : 3 treatment levels (monitor only, partial P&T, full P&T)
  * Observations   : Noisy monitoring well concentrations (lab + sampling uncertainty)
  * Non-stationarity: Plume spreading rate increases at t=15 (seasonal recharge change)
  * Dynamics       : BIDIRECTIONAL — full treatment can achieve cleanup from any stage
  * Horizon        : T=30 (30-year annual remediation programme)
  * Primary metric : U_cum in $k/year-equivalent; P_comply = P(clean by end)
  * T-uncertainty  : HIGH (U_T ≈ 0.5–0.7) — plume transport models are structurally
    uncertain (heterogeneous subsurface, kriging uncertainty, sorption parameters)

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, increased seasonal recharge (wetter winters under
climate change) drives faster contaminant transport, increasing the plume spreading
rate. T_stat → T_shift represents this step-change in plume dynamics.

State space
-----------
θ₁ : Clean               (concentration < 10 % MCL)      — target/compliance state
θ₂ : Near-compliance     (10–50 % MCL)                   — monitoring required
θ₃ : Moderate exceedance (50–200 % MCL)                  — active remediation needed
θ₄ : Significant exceedance (200–500 % MCL)             — intensive treatment
θ₅ : Severe exceedance   (> 500 % MCL)                   — emergency response

MCL = Maximum Contaminant Level (EPA regulatory threshold)

Action space
------------
a₁ : Monitor only        (no active pump-and-treat)        — lowest cost
a₂ : Partial P&T         (50 % pump-and-treat capacity)    — moderate cost
a₃ : Full P&T            (maximum capacity, 6-well system) — highest cost, most effective

Reward function
---------------
Net economic benefit = compliance value − remediation cost − regulatory fine
Units: $k/year equivalent (normalised; positive = net benefit)

Calibration to Gorelick et al. (1984/1990) cost structure:
  Full P&T operational cost:  ~$120–150k/year
  Partial P&T operational:    ~$30–50k/year
  Regulatory fine (θ₄–θ₅):  $200–600k/year
  Compliance benefit (θ₁):   ~$50k/year (avoided monitoring + site value)

Aliases for shared-code compatibility
--------------------------------------
T_stat  = T_B3_STAT  (stable plume dynamics — "stationary" regime)
T_shift = T_B3_SHIFT (faster spreading — "nonstationary" regime after step 15)
T_misspec = T_B3_STAT perturbed +15% spreading (T-misspecification ablation)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year annual remediation programme
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # step at which faster plume spread begins

N = 5   # number of plume contamination stages
M = 3   # number of treatment actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Clean (< 10 % MCL) — regulatory compliance",
    "θ₂ Near-compliance (10–50 % MCL)",
    "θ₃ Moderate exceedance (50–200 % MCL)",
    "θ₄ Significant exceedance (200–500 % MCL)",
    "θ₅ Severe exceedance (> 500 % MCL) — emergency",
]
FAILURE_STATE = 4   # θ₅ index — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions and treatment costs
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Monitor only (no pump-and-treat)",
    "a₂ Partial pump-and-treat (50 % capacity)",
    "a₃ Full pump-and-treat (6-well maximum)",
]
ACTION_COST = np.array([0.0, 40.0, 130.0])   # $k/year treatment cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $k/year net benefit (positive = net benefit; negative = net cost)
#
# Calibration (Gorelick 1984 / Reed 2003 cost structures):
#   a₁ Monitor: no treatment cost, but regulatory fine dominates at θ₄-θ₅
#   a₂ Partial: moderate cost offset by fine avoidance at θ₃-θ₄
#   a₃ Full:    high treatment cost but avoids largest fines; best in θ₄-θ₅
#
# Note: R[a₃, θ₅] = +150 — emergency treatment avoids $600k fine at $130k cost
#       R[a₁, θ₅] = -600 — no treatment + maximum regulatory fine
#       R[a₁, θ₁] = +50  — clean site, minimal monitoring cost only
# ---------------------------------------------------------------------------
R = np.array([
    [ 50.0,  20.0,  -60.0, -250.0, -600.0],   # a₁ Monitor only
    [-30.0,  10.0,   50.0,  100.0,  -40.0],   # a₂ Partial P&T
    [-120.0, -70.0,  10.0,   80.0,  150.0],   # a₃ Full P&T
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices (stable plume dynamics)  T_B3_STAT[action, s, s']
#
# Key properties:
#  - BIDIRECTIONAL: cleanup achievable from all states with sufficient treatment
#  - a₁ (monitor): plume spreads naturally; θ₅ mostly stable (slow attenuation)
#  - a₂ (partial): containment in most states; slow recovery in θ₂-θ₃
#  - a₃ (full):    significant cleanup in all states; θ₅ not fully absorbing
#  - Calibrated to Gorelick (1984) alluvial aquifer plume dynamics
#    (TCE transport, 6-well P&T system, 30-year remediation horizon)
# ---------------------------------------------------------------------------
_T_B3_STAT_0 = np.array([        # a₁ Monitor only (stable conditions)
    [0.75, 0.20, 0.05, 0.00, 0.00],   # θ₁: mostly clean, slow natural spreading
    [0.05, 0.55, 0.30, 0.10, 0.00],   # θ₂: moderate spreading, limited attenuation
    [0.00, 0.05, 0.45, 0.40, 0.10],   # θ₃: significant spreading without treatment
    [0.00, 0.00, 0.05, 0.55, 0.40],   # θ₄: high contamination spreads fast
    [0.00, 0.00, 0.02, 0.08, 0.90],   # θ₅: mostly stable, minor natural attenuation
], dtype=float)

_T_B3_STAT_1 = np.array([        # a₂ Partial pump-and-treat (50 % capacity)
    [0.85, 0.12, 0.03, 0.00, 0.00],   # θ₁: maintained clean
    [0.20, 0.60, 0.16, 0.04, 0.00],   # θ₂: some recovery, containment
    [0.05, 0.25, 0.52, 0.16, 0.02],   # θ₃: partial containment + recovery
    [0.00, 0.05, 0.22, 0.58, 0.15],   # θ₄: slow recovery, partial containment
    [0.00, 0.00, 0.05, 0.22, 0.73],   # θ₅: limited recovery with 50 % capacity
], dtype=float)

_T_B3_STAT_2 = np.array([        # a₃ Full pump-and-treat (6-well maximum)
    [0.90, 0.09, 0.01, 0.00, 0.00],   # θ₁: very well maintained
    [0.45, 0.45, 0.09, 0.01, 0.00],   # θ₂: strong recovery to clean
    [0.15, 0.38, 0.38, 0.08, 0.01],   # θ₃: good cleanup efficiency
    [0.03, 0.15, 0.40, 0.37, 0.05],   # θ₄: significant cleanup possible
    [0.00, 0.02, 0.18, 0.35, 0.45],   # θ₅: meaningful recovery — full system
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B3_STAT_0), ("STAT_1", _T_B3_STAT_1),
                   ("STAT_2", _T_B3_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B3_{_tag} rows not sum to 1: {_rs}"

T_B3_STAT = np.stack([_T_B3_STAT_0, _T_B3_STAT_1, _T_B3_STAT_2], axis=0)  # (3,5,5)


def _apply_plume_shift(T_base: np.ndarray, delta: float = 0.12) -> np.ndarray:
    """
    Apply increased plume spreading rate to a single 5×5 transition matrix.

    For each non-final state s (0..3): subtract delta from diagonal (self-loop),
    add delta to next-worse state (s+1). Final row (θ₅) left unchanged.
    Clips negatives and renormalises.

    Physical interpretation: increased seasonal recharge (wetter winters)
    drives faster contaminant transport, reducing the probability of staying
    in the current contamination stage and increasing forward spreading.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_shift: increased plume spreading after CLIMATE_SWITCH_STEP=15
# a₁ delta=0.12: significant increase in spreading without treatment
# a₂ delta=0.10: partial treatment less effective under faster spreading
# a₃ delta=0.06: full treatment partially compensates for faster spreading
T_B3_SHIFT = np.stack([
    _apply_plume_shift(_T_B3_STAT_0, delta=0.12),
    _apply_plume_shift(_T_B3_STAT_1, delta=0.10),
    _apply_plume_shift(_T_B3_STAT_2, delta=0.06),
], axis=0)

# T-misspecification ablation: practitioner uses undercalibrated spreading model
# (+15 % spreading error — underestimates plume transport velocity)
T_misspec = np.stack([
    _apply_plume_shift(_T_B3_STAT_0, delta=0.15),
    _apply_plume_shift(_T_B3_STAT_1, delta=0.15),
    _apply_plume_shift(_T_B3_STAT_2, delta=0.075),
], axis=0)

# Aliases for shared-code compatibility
T_stat  = T_B3_STAT
T_shift = T_B3_SHIFT

# ---------------------------------------------------------------------------
# Observation model
# Monitoring well concentration proxy (normalised relative to MCL)
# H_MEAN: mean concentration proxy per state (μg/L offset from MCL baseline)
# SIGMA_OBS: lab + sampling uncertainty (σ = 28 μg/L-equiv)
# ---------------------------------------------------------------------------
H_MEAN    = np.array([-80.0, -25.0, 30.0, 90.0, 170.0])   # concentration proxy
SIGMA_OBS = 28.0                                             # observation noise
OBS_BINS  = np.linspace(-180.0, 270.0, 21)                  # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                               # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])     # (20,)

# Likelihood L[θ, o] = P(obs bin o | plume stage θ)  — shape (N, N_OBS)
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
# L_PRES: single model (accurate monitoring: σ=28)
# L_PHIL: model-averaged (precise bore: σ=22 + field grab sample: σ=40)
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_M1 = np.zeros((N, N_OBS), dtype=float)
_L_M2 = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi_m1 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=22.0)
    _cdf_lo_m1 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=22.0)
    _cdf_hi_m2 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=40.0)
    _cdf_lo_m2 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=40.0)
    _L_M1[_s]  = _cdf_hi_m1 - _cdf_lo_m1
    _L_M2[_s]  = _cdf_hi_m2 - _cdf_lo_m2

for _mat in (_L_M1, _L_M2):
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_M1 + 0.5 * _L_M2   # (5, 20)

H_MAX_NATS = float(np.log(N))

# PRIOR_PHIL: uniform — no prior assumption about plume state at planning start
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: moderately contaminated start
# (contamination event has occurred; plume in θ₂-θ₃ range at planning start)
PRIOR_PRES = np.array([0.10, 0.35, 0.35, 0.15, 0.05], dtype=float)
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
    Advance one step using T_B3_STAT (t < CLIMATE_SWITCH_STEP) or
    T_B3_SHIFT (t >= CLIMATE_SWITCH_STEP).
    """
    T_use      = T_B3_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B3_STAT
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
    T_use = T_B3_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B3_STAT
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

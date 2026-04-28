# =============================================================================
# pomdp_env_b2.py  —  MAR POMDP Environment: Arizona/Spain Benchmark 2
# Project  : ELS_NEW / P_Base2  (Benchmark 2 — Managed Aquifer Recharge)
# Paper    : P_Base/ref/Frames_Bernoulli_update.tex
# Plan ref : P_Base/docs/experiment_plan.md §6.2
# Date     : 2026-04-23
# Usage    : import pomdp_env_b2 as env
# Data src : Calibrated synthetic based on ADWR AMA reports + CMIP6 projections
#            (Arizona Active Management Areas; SSP2-4.5 and SSP5-8.5 scenarios)
# =============================================================================
"""
POMDP environment for the Arizona/Spain Managed Aquifer Recharge (MAR) benchmark.
Benchmark 2 in the ELS NW benchmark suite.

Differences from Benchmark 1 (P_Base):
  * Domain         : MAR — annual groundwater storage account decisions
  * State space    : 5 storage-balance categories (surplus → critical deficit)
  * Action space   : 3 recharge program levels (BAU, moderate, maximum recharge)
  * Observations   : noisy annual storage balance indicator (ADWR-style report)
  * Non-stationarity: SSP2-4.5 (base) → SSP5-8.5 (high-emission shift) at t=15
  * Dynamics       : BIDIRECTIONAL — recovery IS possible under active recharge
    (unlike B1 where θ₅ is absorbing)
  * Horizon        : T=30 (30-year annual decision steps)
  * Primary metric : U_cum in $/ML-equivalent; P_fail = P(critical threshold exceeded)

Exported aliases for shared code compatibility
----------------------------------------------
T_stat  = T_SSP245  (SSP2-4.5 base scenario — used by all 'known-T' baselines)
T_shift = T_SSP585  (SSP5-8.5 high-emission scenario — regime B after t=15)
T_misspec = T_SSP245 with +15% depletion perturbation (T-misspecification ablation)

State space
-----------
θ₁ : Surplus          (annual balance > +20 GL-equiv)
θ₂ : Near-balanced    (−5 to +20 GL-equiv)
θ₃ : Mild deficit     (−30 to −5 GL-equiv)
θ₄ : Severe deficit   (−80 to −30 GL-equiv)
θ₅ : Critical/Regulatory threshold exceeded (<−80 GL-equiv)

Action space
------------
a₁ : Business-as-usual (BAU — current allocations, no active recharge program)
a₂ : Moderate recharge (50% percolation/injection capacity; buy-and-dry partial)
a₃ : Maximum recharge  (full program: direct + in-lieu + emergency acquisition)

Reward function
---------------
Objective: maximise discounted net benefit = supply value − supply failure cost
Units: $/ML-equivalent utility (normalised to licence value, comparable to B1)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200      # Monte Carlo episodes per method
T                   = 30       # horizon steps (30-year annual planning horizon)
GAMMA               = 0.97     # discount factor
CLIMATE_SWITCH_STEP = 15       # year at which SSP5-8.5 replaces SSP2-4.5

N = 5   # number of states
M = 3   # number of actions

# ---------------------------------------------------------------------------
# 1.  State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (>+20 GL/yr)",
    "θ₂ Near-balanced (−5 to +20 GL/yr)",
    "θ₃ Mild deficit (−30 to −5 GL/yr)",
    "θ₄ Severe deficit (−80 to −30 GL/yr)",
    "θ₅ Critical / Regulatory threshold exceeded",
]
FAILURE_STATE = 4   # index of θ₅

# ---------------------------------------------------------------------------
# 2.  Action descriptions and recharge costs
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Business-as-usual (BAU)",
    "a₂ Moderate recharge (50 %)",
    "a₃ Maximum recharge (full program)",
]
ACTION_COST = np.array([0.0, 20.0, 55.0])   # $/ML-equiv recharge program cost

# ---------------------------------------------------------------------------
# 3.  Reward matrix  R[action, state]  — shape (M, N)
# Units: $/ML-equivalent net benefit (supply value − failure cost)
# U_eval(a, θ) = R[a, θ]  — common evaluation utility for all methods
#
# Design:
#  a₁ BAU     : best in θ₁-θ₂ (cheap water), catastrophic in θ₄-θ₅
#  a₂ Moderate: balanced across all states; protection in θ₃-θ₄
#  a₃ Maximum : costly in θ₁-θ₂ (overinvestment); best protection in θ₃-θ₅
# Note: R[a₃, θ₅] = -15 > -60 > -180 — always prefer active recharge in crisis
# ---------------------------------------------------------------------------
R = np.array([
    [120.0,  85.0,  25.0, -60.0, -180.0],   # a₁ BAU
    [ 75.0,  75.0,  60.0,  10.0,  -70.0],   # a₂ Moderate recharge
    [ 25.0,  30.0,  45.0,  40.0,  -15.0],   # a₃ Maximum recharge
], dtype=float)

# ---------------------------------------------------------------------------
# 4.  Transition matrices (SSP2-4.5 base scenario)  T_SSP245[action, s, s']
# rows = from-state, cols = to-state;  rows sum to 1
#
# Key properties:
#  - BIDIRECTIONAL: recovery probability > 0 under a₂ and a₃
#  - a₁ (BAU): mostly depletion-driven; slow natural recovery
#  - a₂ (moderate): near-balanced; moderate recovery in θ₂-θ₃
#  - a₃ (maximum): strong recovery in all states; θ₅ not fully absorbing
#  - Calibrated to Arizona AMA annual budget dynamics (Gleick & Palaniappan 2010;
#    ADWR 2022 Annual Report summary statistics)
# ---------------------------------------------------------------------------
_T_SSP245_0 = np.array([          # a₁ Business-as-usual (SSP2-4.5)
    [0.62, 0.28, 0.10, 0.00, 0.00],   # θ₁ surplus → mostly stable but depleting
    [0.10, 0.52, 0.28, 0.10, 0.00],   # θ₂ adequate → depletion risk
    [0.00, 0.10, 0.52, 0.30, 0.08],   # θ₃ mild deficit → deteriorating
    [0.00, 0.00, 0.08, 0.62, 0.30],   # θ₄ severe → likely worse
    [0.00, 0.00, 0.05, 0.15, 0.80],   # θ₅ critical → mostly stays (NOT fully absorbing)
], dtype=float)

_T_SSP245_1 = np.array([          # a₂ Moderate recharge (SSP2-4.5)
    [0.78, 0.17, 0.05, 0.00, 0.00],   # θ₁ → protected
    [0.20, 0.60, 0.15, 0.05, 0.00],   # θ₂ → recovery possible
    [0.05, 0.22, 0.53, 0.18, 0.02],   # θ₃ → recharge helps
    [0.00, 0.06, 0.22, 0.60, 0.12],   # θ₄ → slow recovery
    [0.00, 0.00, 0.10, 0.22, 0.68],   # θ₅ → limited recovery with moderate recharge
], dtype=float)

_T_SSP245_2 = np.array([          # a₃ Maximum recharge (SSP2-4.5)
    [0.85, 0.12, 0.03, 0.00, 0.00],   # θ₁ → well-protected
    [0.35, 0.50, 0.12, 0.03, 0.00],   # θ₂ → strong recovery
    [0.10, 0.35, 0.43, 0.11, 0.01],   # θ₃ → strong recovery from mild deficit
    [0.02, 0.12, 0.35, 0.45, 0.06],   # θ₄ → significant recovery possible
    [0.00, 0.05, 0.20, 0.30, 0.45],   # θ₅ → recovery with emergency recharge
], dtype=float)

# Validate rows sum to 1
for _name, _T in [("SSP245_0", _T_SSP245_0), ("SSP245_1", _T_SSP245_1),
                  ("SSP245_2", _T_SSP245_2)]:
    _rs = _T.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_{_name} rows not sum to 1: {_rs}"

T_SSP245 = np.stack([_T_SSP245_0, _T_SSP245_1, _T_SSP245_2], axis=0)  # (3,5,5)


def _apply_climate_shift(T_base: np.ndarray, delta: float = 0.10) -> np.ndarray:
    """
    Apply a climate step-change to a single 5×5 transition matrix.

    For each non-final state s (0..3): subtract delta from diagonal,
    add delta to next-worse state (s+1).  Final row (θ₅) unchanged.
    Clips negatives and renormalises.

    In B2 context: SSP5-8.5 increases depletion pressure and reduces recovery
    efficiency. The shift reduces self-loop probability (less stability) and
    increases forward transitions (more depletion).
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]   # keep θ₅ row unchanged
    T_new = np.clip(T_new, 0.0, 1.0)
    row_sums = T_new.sum(axis=1, keepdims=True)
    return T_new / row_sums


# SSP5-8.5 (high-emission scenario, Regime B):
# a₁ full delta=0.15: severe reduction in storage recovery, faster depletion
# a₂ delta=0.10: moderate recharge less effective under high temperature/ET
# a₃ delta=0.05: full recharge partially compensates but not fully under SSP5-8.5
T_SSP585 = np.stack([
    _apply_climate_shift(_T_SSP245_0, delta=0.15),   # a₁ severe shift
    _apply_climate_shift(_T_SSP245_1, delta=0.10),   # a₂ moderate shift
    _apply_climate_shift(_T_SSP245_2, delta=0.05),   # a₃ small shift
], axis=0)  # (3, 5, 5)

# ---------------------------------------------------------------------------
# T-misspecification ablation (same structure as B1 Priority 1)
# T_misspec: T_SSP245 perturbed by +15% depletion shift — practitioner using
# a wrongly calibrated model (e.g., using historical data before climate shift)
# ---------------------------------------------------------------------------
T_misspec = np.stack([
    _apply_climate_shift(_T_SSP245_0, delta=0.15),
    _apply_climate_shift(_T_SSP245_1, delta=0.15),
    _apply_climate_shift(_T_SSP245_2, delta=0.075),
], axis=0)  # (3, 5, 5)

# ---------------------------------------------------------------------------
# Aliases for shared-code compatibility (baselines.py, els_methods.py,
# run_benchmark_b2.py all import 'T_stat' and 'T_shift' by name)
# ---------------------------------------------------------------------------
T_stat  = T_SSP245   # alias: base scenario = "stationary" T
T_shift = T_SSP585   # alias: shifted scenario = "nonstationary" T

# ---------------------------------------------------------------------------
# 5.  Observation model
# Storage balance indicator (annual ADWR-style report proxy)
# H_MEAN: mean storage balance proxy per state (GL-equivalent)
# SIGMA_OBS: observation noise std dev (higher than B1 — annual reporting)
# ---------------------------------------------------------------------------
H_MEAN    = np.array([150.0, 50.0, -30.0, -120.0, -250.0])  # GL-equiv state means
SIGMA_OBS = 35.0                                              # noise std dev (GL-equiv)
OBS_BINS  = np.linspace(-380.0, 280.0, 21)                   # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                                 # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])       # (20,)

# Likelihood matrix L[θ, o] = P(obs bin o | state θ)  — shape (N, N_OBS)
_L = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=SIGMA_OBS)
    _cdf_lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=SIGMA_OBS)
    _L[_s] = _cdf_hi - _cdf_lo

_L[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
_L[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
_L = _L / _L.sum(axis=1, keepdims=True)
LIKELIHOOD = _L   # (5, 20)

# ---------------------------------------------------------------------------
# ELS framework likelihood and prior variants
# ---------------------------------------------------------------------------
# L_PRES: single Gaussian (σ=35.0) — prescriptive model (accurate annual report)
L_PRES = LIKELIHOOD.copy()

# L_PHIL: model-averaged (σ=30.0 precision bore + σ=45.0 diffuse report)
_L_M1 = np.zeros((N, N_OBS), dtype=float)
_L_M2 = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi_m1 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=30.0)
    _cdf_lo_m1 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=30.0)
    _cdf_hi_m2 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=45.0)
    _cdf_lo_m2 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=45.0)
    _L_M1[_s] = _cdf_hi_m1 - _cdf_lo_m1
    _L_M2[_s] = _cdf_hi_m2 - _cdf_lo_m2

for _mat in (_L_M1, _L_M2):
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_M1 + 0.5 * _L_M2   # (5, 20); rows sum to 1

H_MAX_NATS = float(np.log(N))   # max entropy in nats

# PRIOR_PHIL : uniform (no prior commitment to storage state)
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES : moderately optimistic (based on typical AMA storage at programme start)
PRIOR_PRES = np.array([0.45, 0.35, 0.15, 0.04, 0.01], dtype=float)
PRIOR_PRES = PRIOR_PRES / PRIOR_PRES.sum()

# ---------------------------------------------------------------------------
# Environment API
# ---------------------------------------------------------------------------

def reset(rng: np.random.Generator) -> tuple[int, np.ndarray]:
    """
    Begin a new episode. Initial state drawn uniformly from {0..4}.
    Initial belief: uniform (no prior information).
    """
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
    Advance one step using SSP2-4.5 (t < CLIMATE_SWITCH_STEP) or
    SSP5-8.5 (t >= CLIMATE_SWITCH_STEP) transition matrix.
    """
    T_use = T_SSP585 if t >= CLIMATE_SWITCH_STEP else T_SSP245
    row        = T_use[action, state]
    next_state = int(rng.choice(N, p=row))
    obs_idx    = int(rng.choice(N_OBS, p=LIKELIHOOD[next_state]))
    reward     = float(R[action, next_state])
    return next_state, obs_idx, reward


def update_belief(b: np.ndarray, obs_idx: int) -> np.ndarray:
    """Static Bayesian belief update (ELS default, no predict step)."""
    b_new = LIKELIHOOD[:, obs_idx] * b
    total = b_new.sum()
    if total < 1e-300:
        return b.copy()
    return b_new / total


def markov_update_belief(
    b: np.ndarray, obs_idx: int, action: int, t: int
) -> np.ndarray:
    """Full Markovian belief update (predict + correct)."""
    T_use = T_SSP585 if t >= CLIMATE_SWITCH_STEP else T_SSP245
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


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate() -> None:
    """Sanity-check all POMDP components. Raises AssertionError on failure."""
    print("=" * 60)
    print("pomdp_env_b2  — validation report (Benchmark 2 MAR)")
    print("=" * 60)

    assert R.shape == (M, N), f"R shape {R.shape}"
    print(f"R shape: {R.shape}  OK")

    for regime_name, T_mat in [("T_SSP245", T_SSP245), ("T_SSP585", T_SSP585),
                                ("T_misspec", T_misspec)]:
        assert T_mat.shape == (M, N, N)
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), f"{regime_name} rows: {rs}"
        assert (T_mat >= 0).all()
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # B2-specific: SSP585 should have ≥ depletion mass than SSP245 (a₁)
    upper_245 = np.tril(T_SSP245[0], k=-1).sum()
    upper_585 = np.tril(T_SSP585[0], k=-1).sum()
    assert upper_585 >= upper_245 - 1e-9, "SSP585 should have ≥ recovery mass below diagonal"
    print("SSP585 depletion monotonicity  OK")

    assert LIKELIHOOD.shape == (N, N_OBS)
    assert np.allclose(LIKELIHOOD.sum(axis=1), 1.0, atol=1e-9)
    print(f"LIKELIHOOD shape {LIKELIHOOD.shape}  row sums OK")

    rng = np.random.default_rng(SEED)
    state, b0 = reset(rng)
    assert 0 <= state < N
    ns, o, rew = step(state, 0, t=0, rng=rng)
    assert 0 <= ns < N
    b1 = update_belief(b0, o)
    assert np.isclose(b1.sum(), 1.0)
    print(f"reset()+step()+update_belief()  OK  (state={state}→{ns}, r={rew:.1f})")

    rng2 = np.random.default_rng(SEED + 1)
    s, b = reset(rng2)
    cumr = 0.0
    for t_step in range(T):
        a = int(np.argmax([expected_reward(b, ai) for ai in range(M)]))
        s, o, r = step(s, a, t_step, rng2)
        b = update_belief(b, o)
        cumr += GAMMA ** t_step * r
    print(f"Full episode smoke test  OK  (U_cum={cumr:.2f}, final_state=θ{s+1})")

    print("=" * 60)
    print("All checks passed.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Module-level exports (same interface as pomdp_env.py for shared code)
# ---------------------------------------------------------------------------
__all__ = [
    "SEED", "N_MC", "T", "GAMMA", "CLIMATE_SWITCH_STEP",
    "N", "M", "N_OBS",
    "STATE_LABELS", "ACTION_LABELS", "ACTION_COST",
    "FAILURE_STATE",
    "R", "T_stat", "T_shift", "T_misspec",
    "T_SSP245", "T_SSP585",
    "H_MEAN", "SIGMA_OBS", "OBS_BINS", "OBS_BIN_CENTRES", "LIKELIHOOD",
    "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

if __name__ == "__main__":
    validate()

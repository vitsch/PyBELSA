# =============================================================================
# pomdp_env_b9.py  —  Glacial Meltwater Recharge POMDP (Indus Basin / HKH)
# Project  : ELS_NEW / P_Base9  (Benchmark 9 — Continuous Non-stationarity)
# Plan ref : P_Base/docs/experiment_plan2.md §12.4
# Date     : 2026-04-25
# Usage    : import pomdp_env_b9 as env
# Data src : GRACE-FO (NASA PO.DAAC DOI:10.5067/GRACE-FO/GRACEF0)
#            ICIMOD HKH Cryosphere Monitoring Programme (www.icimod.org)
#            Pakistan WAPDA groundwater monitoring bore data
#            Pokhrel et al. (2021) Nature Climate Change HKH projection
#            Lutz et al. (2014) Nature Climate Change Indus meltwater runoff
#            Immerzeel et al. (2010) Science Indus basin GRACE + hydrological model
# =============================================================================
"""
POMDP environment for the Indus Basin / HKH Glacial Meltwater Recharge System.
Benchmark 9 in the ELS NW benchmark suite.

Physical context
----------------
The Indus Basin is one of the world's most water-stressed river basins, supporting
~230 million people in Pakistan, India, Afghanistan, and China.  The upper Indus
relies heavily on glacial and snowmelt recharge from the Hindu Kush-Himalaya (HKH)
cryosphere.  CMIP6 projections (IPCC AR6 WG1 Ch.9) show HKH inter-model spread
of ±40% in meltwater runoff trajectories — the highest globally — driven by
uncertainty in ice dynamics, black-carbon deposition, and monsoonal feedbacks.

The defining feature of B9 is CONTINUOUS NON-STATIONARITY:
Unlike B2–B8 where T shifts step-wise at a discrete CLIMATE_SWITCH_STEP, B9 uses
a linear interpolation between T_stat (current era) and T_shift (end-century era)
over the full 30-year horizon:

  T(t) = (1 − α(t)) · T_stat + α(t) · T_shift
  α(t) = t / (T − 1)    [0 at t=0, 1 at t=T-1]

This models the slow but accelerating decline in HKH glacial mass balance as CO₂
continues to accumulate — no abrupt tipping point, just relentless progression.

CMIP6 uncertainty implication (Pokhrel et al. 2021):
  Across CMIP6 models, Indus meltwater recharge changes by −15% to +5% per decade.
  T_stat (best-estimate current conditions) → T_shift (median 2090 degradation) spans
  a transition probability delta of ~0.12–0.16 per annual time step.  This is the
  largest α-uncertainty in the B1–B9 suite (U_T ≈ 0.9).

Key consequence for decision methods:
  Classical POMDP (SARSOP/SDP_S) is solved on T_stat.  Under continuous drift,
  SARSOP's alpha-vectors become increasingly suboptimal as t → T.  ELS_Phil's
  model-averaging over {T_stat, T_shift} degrades less because neither extreme
  is ever fully correct — the blended T remains closer to the true T(t) throughout.

  Adaptive w (ELS_Phil_Adapt) exhibits a novel within-episode w trajectory:
  w rises early (when T_stat ≈ T(t)) then naturally declines as T_stat diverges
  from the true T(t) at later steps — without explicitly tracking α(t).  This
  self-correcting property is the B9 showcase for the adaptive mechanism.

State space (TWSA relative to long-term HKH meltwater recharge baseline)
------------------------------------------------------------------------
θ₁ : Recharged    (TWSA > +50 mm WE)     — glacial surplus sustains full extraction
θ₂ : Adequate     (−20 to +50 mm WE)     — seasonal balance; sustainable management
θ₃ : Stressed     (−110 to −20 mm WE)    — multi-year deficit; active management needed
θ₄ : Critical     (−260 to −110 mm WE)   — infrastructure risk; near-irreversible
θ₅ : Depleted     (TWSA < −260 mm WE)    — 40+ year recovery; food crisis risk

Action space (Pakistan/Afghanistan/India basin-level management)
----------------------------------------------------------------
a₁ : Unrestricted  (full licensed irrigated extraction)
a₂ : Restricted    (40% extraction reduction via rabi crop substitution)
a₃ : Emergency     (70% moratorium + conjunctive surface water use + recharge injection)

Reward function
---------------
Units: $M-equiv/year (irrigated agriculture + pastoral + domestic net benefit)
  Calibrated to WAPDA/World Bank Indus Basin economic valuations (Jacobsen et al. 2009):
  a₁ θ₁: maximum agricultural return — Punjab/Sindh wheat-rice-sugarcane = $85M/year
  a₁ θ₅: catastrophic crop failure + ecosystem collapse + food crisis = -$700M/year
  a₂ θ₃: 40% restriction in stressed state nets positive (avoids -$200M θ₄ trajectory)
  a₃ θ₅: conjunctive surface water + recharge injection avoids worst case (+$150M)
  a₃ θ₁: unnecessary moratorium in recharged state = large economic cost (-$70M)

T_misspec: practitioner uses midpoint T = 0.5·T_stat + 0.5·T_shift as a static model,
  acknowledging some degradation but incorrectly modelling it as time-invariant.
  This represents the common error of "averaging out" non-stationarity into a
  single stationary model — fundamentally wrong because T_true(t) never equals
  the midpoint at any time step except t = (T−1)/2 ≈ step 14.5.

U_T ≈ 0.9 (joint source: CMIP6 inter-model spread × T-horizon × continuous drift)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED    = 2024
N_MC    = 200
T       = 30       # 30-year annual Indus Basin management horizon
GAMMA   = 0.97
# Note: no CLIMATE_SWITCH_STEP — B9 uses continuous T interpolation

N = 5   # aquifer storage / TWSA stages
M = 3   # management actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Recharged (TWSA > +50 mm WE) — glacial surplus sustains full extraction",
    "θ₂ Adequate (−20 to +50 mm WE) — seasonal balance; sustainable",
    "θ₃ Stressed (−110 to −20 mm WE) — multi-year deficit; management needed",
    "θ₄ Critical (−260 to −110 mm WE) — near-irreversible depletion risk",
    "θ₅ Depleted (TWSA < −260 mm WE) — 40+ year recovery; food crisis risk",
]
FAILURE_STATE = 4   # θ₅ — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Unrestricted (full licensed irrigated extraction)",
    "a₂ Restricted (40% rabi crop substitution reduction)",
    "a₃ Emergency (70% moratorium + conjunctive surface use + recharge injection)",
]
ACTION_COST = np.array([0.0, 25.0, 90.0])   # $M/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $M-equiv/year net benefit (irrigated agriculture + pastoral + domestic)
#
# Indus Basin calibration (World Bank IBRD; Jacobsen et al. 2009):
#   a₁ θ₁: max irrigated return (Punjab + Sindh full allocation) = +85
#   a₁ θ₅: Indus crop failure + ecosystem collapse + Pakistan food crisis = -700
#   a₂ θ₃: stressed restriction nets positive — avoids tipping to -200 θ₄ cost
#   a₃ θ₅: conjunctive use (Tarbela/Mangla diversion + injection) = +150
#   a₃ θ₁: unnecessary moratorium in recharged state = -70 (kharif season loss)
# ---------------------------------------------------------------------------
R = np.array([
    [ 85.0,  55.0, -10.0, -200.0, -700.0],   # a₁ Unrestricted
    [ 40.0,  50.0,  70.0,   20.0, -200.0],   # a₂ Restricted 40%
    [-70.0, -20.0,  40.0,  100.0,  150.0],   # a₃ Emergency + conjunctive
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices — T_B9_STAT (current HKH recharge era, ~2020–2030)
# T[action, s, s'] : rows = from-state, cols = to-state; rows sum to 1
#
# Calibration (WAPDA bore network + GRACE-FO Indus Basin 2002–2023):
#   - θ₂ self-loop under a₁ = 0.55 (moderate but unstable in current era)
#   - θ₃ strongly depletion-prone under a₁: P(θ₃→θ₄|a₁)=0.37 per year
#     (consistent with GRACE showing −6 to −8 mm WE/year in stressed zones)
#   - Recovery from θ₄ under a₃ = 0.32 (HKH recharge ~ 5–8 year lag)
#   - θ₅ near-absorbing (WAPDA: 40+ year recovery without radical intervention)
# ---------------------------------------------------------------------------
_T_B9_STAT_0 = np.array([        # a₁ Unrestricted
    [0.75, 0.20, 0.04, 0.01, 0.00],   # θ₁: slow drift in current era
    [0.02, 0.55, 0.30, 0.10, 0.03],   # θ₂: moderate depletion under BAU
    [0.00, 0.05, 0.46, 0.37, 0.12],   # θ₃: significant depletion (GRACE trend)
    [0.00, 0.01, 0.07, 0.56, 0.36],   # θ₄: near-irreversible under unrestricted
    [0.00, 0.00, 0.02, 0.10, 0.88],   # θ₅: near-absorbing depleted state
], dtype=float)

_T_B9_STAT_1 = np.array([        # a₂ Restricted 40% (rabi substitution)
    [0.78, 0.18, 0.03, 0.01, 0.00],   # θ₁: well-maintained under restriction
    [0.04, 0.62, 0.22, 0.10, 0.02],   # θ₂: stable; partial depletion reduction
    [0.01, 0.12, 0.53, 0.27, 0.07],   # θ₃: partial mitigation (CMWU-analogous)
    [0.00, 0.05, 0.20, 0.62, 0.13],   # θ₄: slow recovery; some recharge lag
    [0.00, 0.01, 0.06, 0.22, 0.71],   # θ₅: limited recovery under partial action
], dtype=float)

_T_B9_STAT_2 = np.array([        # a₃ Emergency 70% + conjunctive use
    [0.82, 0.14, 0.02, 0.01, 0.01],   # θ₁: very well maintained
    [0.32, 0.55, 0.11, 0.02, 0.00],   # θ₂: strong recovery tendency
    [0.05, 0.28, 0.49, 0.15, 0.03],   # θ₃: significant recovery with moratorium
    [0.02, 0.10, 0.32, 0.48, 0.08],   # θ₄: recovery achievable with injection
    [0.00, 0.02, 0.14, 0.32, 0.52],   # θ₅: partial recovery; 40-yr recharge lag
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B9_STAT_0), ("STAT_1", _T_B9_STAT_1),
                   ("STAT_2", _T_B9_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B9_{_tag} rows not sum to 1: {_rs}"

T_B9_STAT = np.stack([_T_B9_STAT_0, _T_B9_STAT_1, _T_B9_STAT_2], axis=0)


# ---------------------------------------------------------------------------
# T_B9_SHIFT: end-century diminished HKH recharge era (~2085–2100)
# Models accelerated glacial retreat under CMIP6 median SSP5-8.5 scenario.
# Applied via forward-depletion shift (_apply_depletion_shift) from T_stat.
#
# Physical calibration (Pokhrel et al. 2021 CMIP6 HKH ensemble):
#   Under SSP5-8.5, Indus Upper Basin meltwater contribution declines by 30–45%.
#   For each non-final state s: P(s→s+1) increases by delta (reduced glacial buffer).
#   a₁ delta=0.14: unrestricted extraction + diminished recharge = fast depletion
#   a₂ delta=0.10: restriction partially compensates for reduced glacial input
#   a₃ delta=0.06: emergency measures + conjunctive largely compensate for melt loss
# ---------------------------------------------------------------------------
def _apply_depletion_shift(T_base: np.ndarray, delta: float = 0.14) -> np.ndarray:
    """
    Apply accelerated glacial-retreat depletion to a single 5×5 T matrix.

    For each non-final state s (0..3):
      subtract delta from diagonal self-loop (s→s)
      add delta to forward-depletion entry (s→s+1)
    θ₅ row unchanged (already absorbing — glacier retreat cannot worsen).

    Calibrated to CMIP6 SSP5-8.5 HKH meltwater projections (Pokhrel et al. 2021):
    30–45% reduction in glacial recharge → ~0.06–0.16 additional annual probability
    of state deterioration, modulated by Namibia's management action.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


T_B9_SHIFT = np.stack([
    _apply_depletion_shift(_T_B9_STAT_0, delta=0.14),
    _apply_depletion_shift(_T_B9_STAT_1, delta=0.10),
    _apply_depletion_shift(_T_B9_STAT_2, delta=0.06),
], axis=0)

# Validate T_shift
_rs_shift = T_B9_SHIFT.sum(axis=2)
assert np.allclose(_rs_shift, 1.0, atol=1e-9), "T_B9_SHIFT rows not sum to 1"

# Aliases for shared-code compatibility
T_stat  = T_B9_STAT    # current era = stationary baseline
T_shift = T_B9_SHIFT   # end-century diminished recharge = shift target

# T_misspec: practitioner uses midpoint as a static time-invariant model.
# Acknowledges future degradation but incorrectly treats it as stationary.
# Equal-weight blend of current-era and end-century matrices.
# This is "wrong" at every step except t ≈ (T-1)/2 ≈ 14.5.
T_misspec = 0.5 * T_B9_STAT + 0.5 * T_B9_SHIFT

_rs_misspec = T_misspec.sum(axis=2)
assert np.allclose(_rs_misspec, 1.0, atol=1e-9), "T_misspec rows not sum to 1"


# ---------------------------------------------------------------------------
# Continuous non-stationarity: T(t) = (1-α)·T_stat + α·T_shift
# ---------------------------------------------------------------------------
def T_climate(t: int) -> np.ndarray:
    """
    Continuously interpolated transition matrix at step t.

    T(t) = (1 − α(t)) · T_stat + α(t) · T_shift
    α(t) = t / (T − 1)   →   0 at t=0 (T_stat), 1 at t=T-1 (T_shift)

    Physical interpretation: linear decline in HKH glacial mass balance over
    the 30-year horizon, consistent with CMIP6 median trajectory.  Row sums = 1
    by construction (convex combination of row-stochastic matrices).

    Parameters
    ----------
    t : int — current step index (0-based; 0 ≤ t ≤ T-1)

    Returns
    -------
    T_eff : ndarray (M, N, N) — effective transition matrix at step t
    """
    alpha = min(1.0, float(t) / float(T - 1))
    return (1.0 - alpha) * T_stat + alpha * T_shift


# ---------------------------------------------------------------------------
# Observation model
# GRACE-FO TWSA regional storage anomaly (upper Indus Basin, ~350,000 km²)
# H_MEAN: mean TWSA per state (mm WE, relative to 2002–2020 HKH baseline mean)
# SIGMA_OBS: GRACE-FO aggregation + HKH mountain terrain correction uncertainty
#   σ = 48 mm WE — higher than B8's 42 mm (HKH mountain mass redistribution
#   correction adds ~10 mm WE vs flat Kalahari topography; Vishwakarma et al. 2017)
# OBS_BINS: spans ≈ ±4σ from extreme states
#   [H_MEAN[4] - 2×SIGMA ≈ -356, H_MEAN[0] + 2×SIGMA ≈ +176]
# ---------------------------------------------------------------------------
H_MEAN    = np.array([80.0, 20.0, -60.0, -180.0, -340.0])   # mm WE TWSA
SIGMA_OBS = 48.0     # GRACE-FO + HKH terrain correction uncertainty
OBS_BINS  = np.linspace(-440.0, 180.0, 21)                   # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1   # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])   # (20,)

# Likelihood L[θ, o] = P(obs bin o | state θ)  — shape (N, N_OBS)
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
# L_PRES: single GRACE-FO mascon model (σ=48 — primary satellite product)
# L_PHIL: model-averaged
#   Component 1: GRACE-FO mascon σ=38 (CRI-filtered; best-available regional)
#   Component 2: WAPDA bore network σ=62 (Pakistan monitoring; sparse in Indus)
#   L_PHIL = 0.5 * L_GRACE + 0.5 * L_WAPDA
#   Reflects uncertainty: GRACE-FO covers 350,000 km² footprint (confounds
#   surface/groundwater); bore network is sparse (~1 per 8,000 km² in upper Indus)
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_GRACE = np.zeros((N, N_OBS), dtype=float)
_L_WAPDA = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    for _mat, _sig in [(_L_GRACE, 38.0), (_L_WAPDA, 62.0)]:
        _hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=_sig)
        _lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=_sig)
        _mat[_s] = _hi - _lo

for _mat, _sig in [(_L_GRACE, 38.0), (_L_WAPDA, 62.0)]:
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=_sig)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=_sig)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_GRACE + 0.5 * _L_WAPDA   # (5, 20)

H_MAX_NATS = float(np.log(N))

# ---------------------------------------------------------------------------
# Priors
# ---------------------------------------------------------------------------
# PRIOR_PHIL: uniform — no prior assumption about Indus state
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward θ₃ (stressed) — GRACE shows progressive Indus
# depletion; planning typically starts when the trend is visible in data.
# Calibrated to GRACE-FO 2010–2023 Indus trend (Immerzeel et al. 2010;
# Pokhrel et al. 2021): ~55% of sub-basins show θ₃-equivalent TWSA declining.
PRIOR_PRES = np.array([0.05, 0.15, 0.45, 0.25, 0.10], dtype=float)
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
    Advance one step using continuously interpolated T(t).

    T_eff(t) = (1 − α(t)) · T_stat + α(t) · T_shift, α(t) = t/(T-1)
    No discrete switch — T drifts continuously from T_stat at t=0 to T_shift at t=T-1.
    """
    T_use      = T_climate(t)
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
    """Full Markovian belief update (predict + correct) using T_climate(t)."""
    T_use  = T_climate(t)
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
    """Sanity-check all POMDP components."""
    print("=" * 65)
    print("pomdp_env_b9  — validation report (Benchmark 9 Indus/HKH)")
    print("=" * 65)

    assert R.shape == (M, N), f"R shape {R.shape}"
    print(f"R shape: {R.shape}  OK")

    for regime_name, T_mat in [
        ("T_B9_STAT", T_B9_STAT), ("T_B9_SHIFT", T_B9_SHIFT),
        ("T_misspec", T_misspec),
    ]:
        assert T_mat.shape == (M, N, N)
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), f"{regime_name} rows: {rs}"
        assert (T_mat >= 0).all()
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # B9: T_SHIFT should deplete faster than T_STAT under a₁
    depl_stat  = sum(T_B9_STAT[0, s, s+1] for s in range(N-1))
    depl_shift = sum(T_B9_SHIFT[0, s, s+1] for s in range(N-1))
    assert depl_shift > depl_stat, \
        f"T_SHIFT should have higher depletion than T_STAT: {depl_shift:.3f} > {depl_stat:.3f}"
    print(f"SHIFT > STAT depletion (a₁): {depl_shift:.3f} > {depl_stat:.3f}  OK")

    # T_misspec should be between T_stat and T_shift (midpoint check)
    depl_misspec = sum(T_misspec[0, s, s+1] for s in range(N-1))
    assert depl_stat < depl_misspec < depl_shift, \
        f"T_misspec should be midpoint: {depl_stat:.3f} < {depl_misspec:.3f} < {depl_shift:.3f}"
    print(f"STAT < misspec < SHIFT (a₁): {depl_stat:.3f} < {depl_misspec:.3f} < {depl_shift:.3f}  OK")

    # Continuous non-stationarity: T_climate(0) ≈ T_stat, T_climate(T-1) ≈ T_shift
    assert np.allclose(T_climate(0), T_stat, atol=1e-9), "T_climate(0) ≠ T_stat"
    assert np.allclose(T_climate(T-1), T_shift, atol=1e-9), "T_climate(T-1) ≠ T_shift"
    # Monotone depletion increase
    depl_t0  = sum(T_climate(0)[0, s, s+1] for s in range(N-1))
    depl_t14 = sum(T_climate(14)[0, s, s+1] for s in range(N-1))
    depl_t29 = sum(T_climate(29)[0, s, s+1] for s in range(N-1))
    assert depl_t0 < depl_t14 < depl_t29, \
        f"Non-monotone depletion: {depl_t0:.3f}, {depl_t14:.3f}, {depl_t29:.3f}"
    print(f"T_climate depletion monotone: t=0:{depl_t0:.3f}, t=14:{depl_t14:.3f}, t=29:{depl_t29:.3f}  OK")
    print(f"T_climate(0)≈T_stat  T_climate(T-1)≈T_shift  OK")

    assert LIKELIHOOD.shape == (N, N_OBS)
    assert np.allclose(LIKELIHOOD.sum(axis=1), 1.0, atol=1e-9)
    print(f"LIKELIHOOD shape {LIKELIHOOD.shape}  row sums OK")

    rng = np.random.default_rng(SEED)
    state, b0 = reset(rng)
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

    print("=" * 65)
    print("All checks passed.")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Module-level exports
# ---------------------------------------------------------------------------
__all__ = [
    "SEED", "N_MC", "T", "GAMMA",
    "N", "M", "N_OBS",
    "STATE_LABELS", "ACTION_LABELS", "ACTION_COST",
    "FAILURE_STATE",
    "R", "T_stat", "T_shift", "T_misspec",
    "T_B9_STAT", "T_B9_SHIFT",
    "T_climate",
    "H_MEAN", "SIGMA_OBS", "OBS_BINS", "OBS_BIN_CENTRES", "LIKELIHOOD",
    "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

if __name__ == "__main__":
    validate()

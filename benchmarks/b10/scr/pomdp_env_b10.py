# =============================================================================
# pomdp_env_b10.py  —  Data-Scarce Pastoral Aquifer (Sahel / Lake Chad Basin)
# Project  : ELS_NEW / P_Base10  (Benchmark 10 — Maximal T Uncertainty)
# Plan ref : P_Base/docs/experiment_plan2.md §12.5
# Date     : 2026-04-25
# Usage    : import pomdp_env_b10 as env
# Data src : GRACE-TELLUS RL06 mascon product (NASA PO.DAAC)
#            OSS (Observatoire du Sahara et du Sahel) groundwater portal
#            LCBC (Lake Chad Basin Commission) annual hydrogeological reports
#            Leblanc et al. (2011) J Hydrol Lake Chad groundwater decline
#            Goni et al. (2021) Hydrogeol J Quaternary aquifer Lake Chad
#            Buma & Lee (2020) Sci Total Environ Sahel GRACE depletion
# =============================================================================
"""
POMDP environment for the Sahel / Lake Chad Basin Shallow Quaternary Aquifer.
Benchmark 10 in the ELS NW benchmark suite — maximal T-uncertainty scenario.

Physical context
----------------
The Lake Chad Basin shallow Quaternary aquifer (≈2.4 million km²) supports
pastoral and rain-fed agricultural livelihoods for ~45 million people in Chad,
Niger, Nigeria, and Cameroon.  GRACE-TELLUS shows steady TWSA decline of
−8 to −12 mm WE/year since 2002 (Buma & Lee 2020; Leblanc et al. 2011).

Monitoring is severely limited: the OSS groundwater portal records ≤3 bore-wells
per 10,000 km² across most of the basin, and monitoring records extend ≤15 years
at most sites.  The LCBC annual reports provide only basin-scale estimates without
spatial disaggregation adequate for state-transition estimation.

The defining feature of B10 is MAXIMAL T UNCERTAINTY (U_T ≈ 1.0):
With only ~50 observed annual state transitions across the entire monitoring
network, the transition matrix T cannot be estimated reliably.  A Dirichlet
posterior with n_obs=50 observations produces T estimates that are nearly uniform
— structurally indistinguishable from random transitions.  This is the critical
practical difference between data-scarce Sahel aquifer management and the B1–B9
benchmarks: the decision problem must be solved WITHOUT a reliable T estimate.

ELS advantage at U_T ≈ 1.0
----------------------------
ELS_Phil uses ONLY the observation likelihood L_PHIL to update beliefs and select
actions via the satisficing + info-gain criterion.  L_PHIL can be estimated from
even sparse bore-network and GRACE data — it does not require temporal state
transitions.  SARSOP under estimated T (T_misspec, n=50) produces alpha-vectors
that reflect a near-uniform transition model; the resulting policy is near-random.

Key prediction (experiment_plan2.md §12.5):
  SARSOP_Misspec (T estimated from n=50 transitions)
  → U_cum below or near AlwaysRestricted baseline
  ELS_Phil (w=0, no T dependence)
  → 20–40% above AlwaysRestricted

T_misspec design (B10 novelty)
-------------------------------
T_misspec is generated via a Dirichlet posterior from T_stat with n_total=50
observed transitions distributed uniformly across M×N=15 state-action rows:
  n_per_row = max(1, n_total // (M × N)) = 3  transitions per row
  alpha[a, s, :] = n_per_row × T_stat[a, s, :] + 1/N  (uniform Dirichlet prior)
  T_misspec[a, s, :] ~ Dirichlet(alpha[a, s, :])
With only 3 "votes" per row, the posterior is near-uniform (high-entropy),
producing a T_misspec that radically underestimates self-loops and depletion
asymmetry.  Fixed seed (SEED+10000) ensures reproducibility.

Non-stationarity source (CLIMATE_SWITCH_STEP = 15)
--------------------------------------------------
At step 15, a sustained Sahel drought (consistent with CMIP6 SSP5-8.5 Lake Chad
projections; Taylor et al. 2017) reduces millet-zone infiltration by 25–40%,
shifting T_stat → T_shift (accelerated depletion).  The drought is the primary
governance trigger for LCBC emergency protocols.

State space (groundwater access level, Quaternary aquifer TWSA)
---------------------------------------------------------------
θ₁ : Surplus      (TWSA > +50 mm WE)    — all wells functional; seasonal recharge exceeds demand
θ₂ : Adequate     (−30 to +50 mm WE)   — demand-recharge balance; no shortfalls
θ₃ : Stressed     (−120 to −30 mm WE)  — dry-season deficits; some seasonal wells fail
θ₄ : Critical     (−270 to −120 mm WE) — multi-year cumulative deficit; well failures common
θ₅ : Crisis       (TWSA < −270 mm WE)  — population displacement; food insecurity; 50+ yr recovery

Action space (LCBC coordinated management options)
--------------------------------------------------
a₁ : Unrestricted  (unlimited pastoral + rain-fed agricultural extraction)
a₂ : Managed       (20% reduction + OSS bore rehabilitation programme)
a₃ : Emergency     (50% moratorium + LCBC emergency fund + desalination kits)

Reward function
---------------
Units: $M-equiv/year (pastoral economy + food security + humanitarian cost avoidance)
  Calibrated to OSS/LCBC economic valuations (Leblanc et al. 2011; LCBC 2019):
  a₁ θ₁: max pastoral economy — livestock + millet + sorghum = +$70M/year
  a₁ θ₅: population displacement + food insecurity + emergency response = −$500M/year
  a₂ θ₃: managed reduction in stressed state nets positive (avoids θ₄ cascade)
  a₃ θ₅: LCBC fund + desalination avoids −$500M cost (+$100M net)
  a₃ θ₁: unnecessary moratorium in surplus = −$60M (livestock idle, crops missed)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year annual Lake Chad Basin management horizon
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # Sustained Sahel drought onset (CMIP6 SSP5-8.5)

N = 5   # aquifer storage / TWSA stages
M = 3   # management actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (TWSA > +50 mm WE) — all wells functional; recharge exceeds demand",
    "θ₂ Adequate (−30 to +50 mm WE) — demand-recharge balance; no shortfalls",
    "θ₃ Stressed (−120 to −30 mm WE) — dry-season deficits; seasonal wells fail",
    "θ₄ Critical (−270 to −120 mm WE) — multi-year deficit; well failures common",
    "θ₅ Crisis (TWSA < −270 mm WE) — population displacement; 50+ yr recovery",
]
FAILURE_STATE = 4   # θ₅ — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Unrestricted (unlimited pastoral + agricultural extraction)",
    "a₂ Managed (20% reduction + OSS bore rehabilitation)",
    "a₃ Emergency (50% moratorium + LCBC fund + desalination kits)",
]
ACTION_COST = np.array([0.0, 10.0, 60.0])   # $M/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $M-equiv/year net benefit (pastoral + food security + humanitarian)
#
# OSS/LCBC calibration principles:
#   a₁ θ₁: max pastoral return = +70 (optimal under good conditions)
#   a₁ θ₅: population crisis = -500 = U_MIN (catastrophic; irreversible on human timescale)
#   a₂ θ₃: managed restriction in stressed state → +60 (avoids θ₄ tipping)
#   a₃ θ₅: LCBC emergency fund + desalination avoids worst case = +100
#   a₃ θ₁: unnecessary moratorium in surplus = -60 (lost pastoral production)
# ---------------------------------------------------------------------------
R = np.array([
    [ 70.0,  40.0, -15.0, -180.0, -500.0],   # a₁ Unrestricted
    [ 25.0,  40.0,  60.0,   15.0, -150.0],   # a₂ Managed 20%
    [-60.0, -15.0,  35.0,   90.0,  100.0],   # a₃ Emergency + LCBC fund
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices — T_B10_STAT (current Sahel dynamics, ~2020–2035)
# T[action, s, s'] : rows = from-state, cols = to-state; rows sum to 1
#
# Calibration (OSS portal + LCBC annual reports + Leblanc et al. 2011):
#   - θ₂ self-loop under a₁ = 0.50 (high seasonal variability in Sahel recharge)
#   - θ₃ depletion under a₁: P(θ₃→θ₄|a₁)=0.38 (multi-year recharge deficits)
#   - θ₄ near-absorbing under a₁ (P(θ₄→θ₅|a₁)=0.38 per year)
#   - Recovery from θ₄ under a₃ = 0.28 (Quaternary recharge ~8–12 year lag)
#   - θ₅ near-absorbing under all actions (50+ year recovery)
#
# Key B10 feature: θ₁ self-loop under a₁ = 0.70 (lower than B9's 0.75) —
# Sahel is more variable; even in "surplus" conditions, recharge is uncertain.
# ---------------------------------------------------------------------------
_T_B10_STAT_0 = np.array([        # a₁ Unrestricted
    [0.70, 0.22, 0.06, 0.02, 0.00],   # θ₁: slow drift in current era
    [0.02, 0.50, 0.32, 0.12, 0.04],   # θ₂: moderate-high depletion under BAU
    [0.00, 0.06, 0.45, 0.38, 0.11],   # θ₃: significant depletion (Leblanc 2011)
    [0.00, 0.01, 0.06, 0.55, 0.38],   # θ₄: near-absorbing under unrestricted
    [0.00, 0.00, 0.02, 0.12, 0.86],   # θ₅: near-absorbing crisis state
], dtype=float)

_T_B10_STAT_1 = np.array([        # a₂ Managed 20% + bore rehabilitation
    [0.75, 0.18, 0.05, 0.02, 0.00],   # θ₁: moderately maintained
    [0.03, 0.58, 0.26, 0.10, 0.03],   # θ₂: stable with bore rehabilitation
    [0.01, 0.10, 0.52, 0.30, 0.07],   # θ₃: partial mitigation
    [0.00, 0.04, 0.18, 0.62, 0.16],   # θ₄: slow recovery; 20% not enough alone
    [0.00, 0.01, 0.06, 0.24, 0.69],   # θ₅: limited recovery under partial action
], dtype=float)

_T_B10_STAT_2 = np.array([        # a₃ Emergency 50% + LCBC fund
    [0.80, 0.15, 0.03, 0.01, 0.01],   # θ₁: well maintained
    [0.28, 0.55, 0.14, 0.03, 0.00],   # θ₂: strong recovery tendency
    [0.04, 0.26, 0.50, 0.17, 0.03],   # θ₃: significant recovery with moratorium
    [0.01, 0.08, 0.28, 0.52, 0.11],   # θ₄: recovery achievable with LCBC fund
    [0.00, 0.02, 0.12, 0.34, 0.52],   # θ₅: partial recovery; 50-yr recharge lag
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B10_STAT_0), ("STAT_1", _T_B10_STAT_1),
                   ("STAT_2", _T_B10_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B10_{_tag} rows not sum to 1: {_rs}"

T_B10_STAT = np.stack([_T_B10_STAT_0, _T_B10_STAT_1, _T_B10_STAT_2], axis=0)


# ---------------------------------------------------------------------------
# T_B10_SHIFT: sustained Sahel drought (post-CLIMATE_SWITCH_STEP=15)
# Models CMIP6 SSP5-8.5 Lake Chad Basin sustained drought from ~2035.
# Reduces millet-zone infiltration by 25–40% → accelerated aquifer depletion.
# Applied via _apply_depletion_shift from T_stat.
#
# Calibration (Taylor et al. 2017; Goni et al. 2021 CMIP6 LCB projections):
#   Under SSP5-8.5, Lake Chad Basin rainfall declines 20–35% from ~2035.
#   a₁ delta=0.16: unrestricted + drought = fastest depletion in suite
#   a₂ delta=0.12: managed restriction partially compensates for drought
#   a₃ delta=0.08: emergency measures largely compensate (desalination + bore deepening)
# ---------------------------------------------------------------------------
def _apply_depletion_shift(T_base: np.ndarray, delta: float = 0.14) -> np.ndarray:
    """
    Apply drought-induced depletion acceleration to a single 5×5 T matrix.

    For each non-final state s (0..3):
      subtract delta from diagonal self-loop (s→s)
      add delta to forward-depletion entry (s→s+1)
    θ₅ row unchanged (already absorbing).

    Calibrated to CMIP6 SSP5-8.5 Lake Chad Basin: 25–40% rainfall reduction
    → ~0.08–0.16 additional annual probability of state deterioration.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


T_B10_SHIFT = np.stack([
    _apply_depletion_shift(_T_B10_STAT_0, delta=0.16),
    _apply_depletion_shift(_T_B10_STAT_1, delta=0.12),
    _apply_depletion_shift(_T_B10_STAT_2, delta=0.08),
], axis=0)

_rs_shift = T_B10_SHIFT.sum(axis=2)
assert np.allclose(_rs_shift, 1.0, atol=1e-9), "T_B10_SHIFT rows not sum to 1"

# Aliases for shared-code compatibility
T_stat  = T_B10_STAT    # current era = stationary baseline
T_shift = T_B10_SHIFT   # SSP5-8.5 drought shift

# ---------------------------------------------------------------------------
# T_misspec (B10 NOVELTY): Dirichlet-estimated T from n_total=50 observations
#
# In the Lake Chad Basin, the entire monitoring network produces ~50 usable
# annual state-transition observations across all wells and years.  With
# M×N=15 state-action rows, this gives ~3 observations per row.
#
# Dirichlet posterior:
#   For each action a, state s:
#     alpha[s, :] = n_per_row × T_stat[a, s, :] + 1/N  (uniform prior)
#     T_misspec[a, s, :] ~ Dirichlet(alpha[s, :])
#
# With n_per_row=3, concentration parameter ≈ 4 (including prior), the
# posterior is near-uniform.  A SARSOP policy solved on T_misspec receives
# near-random transition information — qualitatively wrong in self-loop
# magnitude, depletion asymmetry, and recovery probabilities.
#
# Fixed RNG (SEED+10000) ensures T_misspec is reproducible across all runs.
# ---------------------------------------------------------------------------
N_OBS_MISSPEC = 50    # total observations across full monitoring network
_N_PER_ROW    = max(1, N_OBS_MISSPEC // (M * N))   # = 3 per state-action row

_rng_misspec = np.random.default_rng(SEED + 10000)
T_misspec = np.zeros((M, N, N), dtype=float)
for _a in range(M):
    for _s in range(N):
        _alpha = _N_PER_ROW * T_B10_STAT[_a, _s, :] + 1.0 / N
        T_misspec[_a, _s, :] = _rng_misspec.dirichlet(_alpha)

_rs_misspec = T_misspec.sum(axis=2)
assert np.allclose(_rs_misspec, 1.0, atol=1e-9), "T_misspec rows not sum to 1"


# ---------------------------------------------------------------------------
# Observation model
# GRACE-TELLUS TWSA regional anomaly (Lake Chad Basin)
# H_MEAN: mean TWSA per state (mm WE, relative to 2002–2020 LCB mean)
# SIGMA_OBS = 55.0 mm WE — highest in suite
#   Sources: GRACE-TELLUS RL06 mascon (NASA PO.DAAC); OSS bore interpolation
#   SIGMA = 55 reflects:
#     - GRACE footprint 300–400 km in flat Sahel (surface water confounding)
#     - OSS bore network 1–3 wells per 10,000 km² (extreme sparsity)
#     - Seasonal variability in Sahel TWSA (~40 mm WE annual amplitude)
#     - Lake Chad open-water surface effects on mascon signal (~15 mm WE)
# ---------------------------------------------------------------------------
H_MEAN    = np.array([60.0, 0.0, -80.0, -200.0, -380.0])   # mm WE TWSA
SIGMA_OBS = 55.0      # highest in suite (GRACE Sahel + extreme sparsity)
OBS_BINS  = np.linspace(-500.0, 180.0, 21)                  # 21 edges → 20 bins
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
# L_PRES: single GRACE-TELLUS mascon model (σ=55 — primary satellite product)
# L_PHIL: model-averaged
#   Component 1: GRACE-TELLUS mascon σ=45 (CRI-filtered sub-basin product)
#   Component 2: OSS bore network σ=70 (extremely sparse; low spatial coverage)
#   L_PHIL = 0.5 × L_GRACE + 0.5 × L_OSS
#   Widest model uncertainty in suite: GRACE-TELLUS aggregates ≥150,000 km²
#   footprints; OSS bore extrapolation spans 10,000 km² per well
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_GRACE = np.zeros((N, N_OBS), dtype=float)
_L_OSS   = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    for _mat, _sig in [(_L_GRACE, 45.0), (_L_OSS, 70.0)]:
        _hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=_sig)
        _lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=_sig)
        _mat[_s] = _hi - _lo

for _mat, _sig in [(_L_GRACE, 45.0), (_L_OSS, 70.0)]:
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=_sig)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=_sig)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_GRACE + 0.5 * _L_OSS   # (5, 20)

H_MAX_NATS = float(np.log(N))

# ---------------------------------------------------------------------------
# Priors
# ---------------------------------------------------------------------------
# PRIOR_PHIL: uniform — no prior assumption about LCB state
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: strongly biased toward θ₃–θ₄ (stressed/critical).
# Calibrated to GRACE-TELLUS 2002–2023 LCB trend: ~65% of OSS monitoring
# sites show θ₃–θ₄ equivalent TWSA (Leblanc et al. 2011; Buma & Lee 2020).
# Planning starts when crisis trajectory is visible in GRACE data.
PRIOR_PRES = np.array([0.03, 0.10, 0.35, 0.35, 0.17], dtype=float)
PRIOR_PRES = PRIOR_PRES / PRIOR_PRES.sum()

# ---------------------------------------------------------------------------
# T_misspec depletion info (stored for validation)
# ---------------------------------------------------------------------------
_depl_stat   = sum(T_B10_STAT[0, s, s+1] for s in range(N-1))
_depl_misspec = sum(T_misspec[0, s, s+1] for s in range(N-1))

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
    Advance one step.
    t < CLIMATE_SWITCH_STEP : T_B10_STAT (current Sahel conditions)
    t >= CLIMATE_SWITCH_STEP: T_B10_SHIFT (sustained drought onset)
    """
    T_use      = T_B10_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B10_STAT
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
    T_use  = T_B10_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B10_STAT
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
    print("pomdp_env_b10  — validation (Benchmark 10 Sahel/LCB)")
    print("=" * 65)

    assert R.shape == (M, N), f"R shape {R.shape}"
    print(f"R shape: {R.shape}  OK")

    for regime_name, T_mat in [
        ("T_B10_STAT", T_B10_STAT), ("T_B10_SHIFT", T_B10_SHIFT),
        ("T_misspec", T_misspec),
    ]:
        assert T_mat.shape == (M, N, N)
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), f"{regime_name} rows: {rs}"
        assert (T_mat >= 0).all()
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # B10: T_SHIFT depletes faster than T_STAT under a₁
    depl_stat  = sum(T_B10_STAT[0, s, s+1]  for s in range(N-1))
    depl_shift = sum(T_B10_SHIFT[0, s, s+1] for s in range(N-1))
    assert depl_shift > depl_stat, \
        f"T_SHIFT depletion {depl_shift:.3f} should exceed T_STAT {depl_stat:.3f}"
    print(f"SHIFT > STAT depletion (a₁): {depl_shift:.3f} > {depl_stat:.3f}  OK")

    # T_misspec: report Dirichlet uncertainty (no ordering guarantee — near-uniform)
    print(f"T_misspec (Dirichlet n=50) depletion (a₁): {_depl_misspec:.3f}  "
          f"(T_stat ref: {_depl_stat:.3f})  rows OK")
    print(f"T_misspec row entropy check: "
          f"max_entropy={float(np.log(N)):.3f}  "
          f"T_misspec_mean_entropy="
          f"{float(np.mean([-np.sum(r*np.log(np.clip(r,1e-9,1))) for a in range(M) for r in T_misspec[a]])):.3f}  "
          f"T_stat_mean_entropy="
          f"{float(np.mean([-np.sum(r*np.log(np.clip(r,1e-9,1))) for a in range(M) for r in T_B10_STAT[a]])):.3f}")

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
    "SEED", "N_MC", "T", "GAMMA", "CLIMATE_SWITCH_STEP",
    "N", "M", "N_OBS",
    "STATE_LABELS", "ACTION_LABELS", "ACTION_COST",
    "FAILURE_STATE",
    "R", "T_stat", "T_shift", "T_misspec",
    "T_B10_STAT", "T_B10_SHIFT",
    "N_OBS_MISSPEC",
    "H_MEAN", "SIGMA_OBS", "OBS_BINS", "OBS_BIN_CENTRES", "LIKELIHOOD",
    "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

if __name__ == "__main__":
    validate()

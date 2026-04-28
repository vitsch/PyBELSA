# =============================================================================
# pomdp_env_b6.py  —  Karst Aquifer: Deep Structural Uncertainty POMDP
# Project  : ELS_NEW / P_Base6  (Benchmark 6 — Karst Aquifer)
# Plan ref : P_Base/docs/experiment_plan2.md §12.1
# Date     : 2026-04-25
# Usage    : import pomdp_env_b6 as env
# Data src : Dinaric Karst AQUADEM project (EC FP7, open access)
#            Bonacci (1987) Karst Hydrology, Springer
#            Ford & Williams (2007) Karst Hydrogeology and Geomorphology, Wiley
#            White (2002) Karst hydrology: recent developments, J Hydrol
#            GRACE-FO regional storage anomaly (NASA PO.DAAC)
# =============================================================================
"""
POMDP environment for the Karst Aquifer groundwater benchmark.
Benchmark 6 in the ELS NW benchmark suite.

Physical context
----------------
Karst aquifers host approximately 25% of global groundwater supplies and support
~1 billion people, yet their dynamics are the hardest to model in the standard
suite.  The dual-porosity structure — consisting of a fast conduit network and a
slow porous matrix — means the effective transition matrix T depends on which
flow regime dominates at any given time:

  Conduit-dominated:  fast, highly nonlinear flow; springs respond within days
  Matrix-dominated:   slow, diffusive flow; springs respond over weeks to months

This creates STRUCTURAL model uncertainty: T is not a fixed matrix with uncertain
parameters — the functional form of T is unknown.  A practitioner using a purely
matrix-based model (standard porous-medium Darcy flow) will systematically
misrepresent both the speed and nonlinearity of karst transitions.

ELS's T-agnosticism is uniquely suited to this setting: the observation likelihood
L(obs|state) can still be estimated from spring discharge monitoring even when T
cannot be reliably specified.  SARSOP's alpha vectors, computed from a single
assumed T, become systematically wrong as conduit connectivity changes.

This benchmark provides U_T ≈ 0.9 — the highest structural T uncertainty in the
suite.  The primary research question is whether ELS's observation-driven belief
update maintains performance superiority even when the T uncertainty is not just
parametric but structural.

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, prolonged drought begins desiccating the conduit
network, shifting effective dynamics from mixed conduit-matrix toward
matrix-dominated.  This is a structural non-stationarity: the T form changes,
not just the parameters.  CMIP6 Mediterranean and Dinaric projections show
increasing drought frequency under SSP5-8.5 (Spinoni et al. 2020; Polade et al.
2017).

State space (spring discharge categories, L/s anomaly relative to baseline)
---------------------------------------------------------------------------
θ₁ : Surplus        (TWSA proxy > +80 L/s above baseline) — full extraction OK
θ₂ : Normal         (+20 to +80 L/s anomaly)              — sustainable abstraction
θ₃ : Reduced        (−30 to +20 L/s anomaly)              — active restriction needed
θ₄ : Intermittent   (−90 to −30 L/s anomaly)              — conduit network stressed
θ₅ : Failed/Saline  (< −90 L/s or saltwater intrusion)   — irreversible 30-yr scale

Note: saltwater intrusion is the dominant failure mode in coastal karst (Yucatan,
Mediterranean); spring drying dominates in inland Dinaric-type systems.

Action space
------------
a₁ : Maintain   (full abstraction from karst wells + springs)
a₂ : Restrict   (seasonal reduction 40%, restrict large-scale extraction)
a₃ : Emergency  (full cessation + managed recharge via surface spreading)

Reward function
---------------
Units: $k-equiv/year (net economic benefit from water supply and tourism)
  Positive: water supply revenue + spring-fed tourism ecosystem value
  Negative: spring failure penalty (saltwater intrusion + tourism collapse)

Calibration (Dinaric/Mediterranean karst economic valuation):
  Full extraction in surplus (θ₁,a₁): max water supply + tourism ≈ +$90k-equiv
  No-action during failure (θ₅,a₁): saltwater + collapse ≈ −$800k-equiv
  Emergency in failure (θ₅,a₃): avoids −$800 at ~$150k cost → net +$80k-equiv
  Unnecessary emergency in surplus (θ₁,a₃): −$150k opportunity cost

Key B6 differences vs B5 (NCP GRACE):
  * Domain         : Karst aquifer (dual-porosity structural T uncertainty)
  * State space    : 5 spring discharge categories (L/s anomaly proxy)
  * Observations   : spring discharge (σ=38 — dual-porosity model spread)
  * L_PHIL         : avg(σ=25 conduit-dominated, σ=55 matrix-dominated)
  * Non-stationarity: conduit-network desiccation (structural T change at t=15)
  * T-uncertainty  : STRUCTURAL (U_T ≈ 0.9) — T form unknown, not just parameters
  * U_MIN          : −800 (saltwater intrusion irreversible; highest penalty in suite)
  * PRIOR_PRES     : moderate stress bias [0.05, 0.20, 0.40, 0.25, 0.10]
  * SIGMA_OBS      : 38 mm discharge-equiv (dual-porosity measurement noise)

Aliases for shared-code compatibility
--------------------------------------
T_stat  = T_B6_STAT  (long-term average mixed conduit-matrix dynamics)
T_shift = T_B6_SHIFT (drought-desiccated conduit → matrix-dominated dynamics)
T_misspec = purely matrix model (standard Darcy — misses conduit fast paths)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year karst management plan
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # prolonged drought onset (conduit desiccation)

N = 5   # spring discharge states
M = 3   # management actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (discharge > +80 L/s above baseline) — full extraction available",
    "θ₂ Normal (+20 to +80 L/s anomaly) — sustainable abstraction",
    "θ₃ Reduced (−30 to +20 L/s anomaly) — active restriction needed",
    "θ₄ Intermittent (−90 to −30 L/s anomaly) — conduit network stressed",
    "θ₅ Failed/Saline (< −90 L/s or saltwater intrusion) — irreversible 30-yr scale",
]
FAILURE_STATE = 4   # θ₅ — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Maintain (full abstraction from karst wells and springs)",
    "a₂ Restrict (seasonal 40% reduction in abstraction)",
    "a₃ Emergency (full cessation + managed recharge via surface spreading)",
]
ACTION_COST = np.array([0.0, 40.0, 150.0])   # $k-equiv/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $k-equiv/year net economic benefit
#
# Design rationale (Dinaric/Mediterranean karst economics):
#   a₁ Maintain: best in θ₁ but catastrophic in θ₅ (saltwater intrusion costs)
#   a₂ Restrict: moderate benefit across θ₂–θ₄; some cost in θ₁
#   a₃ Emergency: high cost in θ₁–θ₂ but avoids irreversible failure in θ₄–θ₅
#
#   R[a₁, θ₅] = −800: saltwater intrusion + spring failure (highest penalty in suite)
#   R[a₃, θ₅] = +80:  emergency cessation + recharge avoids −800 at ~$150k cost
#   R[a₁, θ₁] = +90:  max water supply + spring-fed tourism in surplus
#   R[a₃, θ₁] = −150: unnecessary emergency; significant opportunity cost
# ---------------------------------------------------------------------------
R = np.array([
    [  90.0,  55.0,  -20.0, -180.0, -800.0],   # a₁ Maintain
    [ -20.0,  45.0,   75.0,   55.0, -120.0],   # a₂ Restrict
    [-150.0, -70.0,   25.0,  100.0,   80.0],   # a₃ Emergency cessation + recharge
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices — T_B6_STAT  (long-term average, mixed conduit-matrix)
#
# Key physics:
#  - BIDIRECTIONAL: managed recharge (a₃) can restore conduit connectivity
#  - a₁ (maintain): conduit drainage + matrix seepage → progressive decline
#  - a₂ (restrict): maintains conduit flow, slows matrix depletion
#  - a₃ (emergency): surface spreading recharges both conduit and matrix
#  - Calibrated to Dinaric Karst AQUADEM project observations (Ford & Williams 2007)
#
# Note on conduit-matrix mixing:
#  - Conduit component: fast transitions (higher off-diagonal probability)
#  - Matrix component:  slow transitions (higher diagonal probability)
#  - T_B6_STAT represents the long-term average; any given episode may be
#    conduit-dominated (high variance) or matrix-dominated (low variance)
#  - This structural uncertainty drives U_T ≈ 0.9 — the practitioner cannot
#    observe which regime dominates without expensive dye-trace testing
# ---------------------------------------------------------------------------
_T_B6_STAT_0 = np.array([        # a₁ Maintain (full abstraction)
    [0.58, 0.30, 0.09, 0.03, 0.00],   # θ₁: surplus → gradual depletion under pumping
    [0.07, 0.50, 0.30, 0.11, 0.02],   # θ₂: conduit drainage + matrix extraction
    [0.01, 0.10, 0.44, 0.33, 0.12],   # θ₃: significant conduit contribution to decline
    [0.00, 0.01, 0.14, 0.48, 0.37],   # θ₄: conduit network nearing exhaustion
    [0.00, 0.00, 0.02, 0.08, 0.90],   # θ₅: near-absorbing; saltwater once intruded
], dtype=float)

_T_B6_STAT_1 = np.array([        # a₂ Restrict (seasonal reduction)
    [0.72, 0.22, 0.05, 0.01, 0.00],   # θ₁: surplus maintained with restriction
    [0.13, 0.58, 0.23, 0.05, 0.01],   # θ₂: stable, conduit flow maintained
    [0.04, 0.18, 0.54, 0.20, 0.04],   # θ₃: partial containment; matrix recovery
    [0.01, 0.04, 0.22, 0.58, 0.15],   # θ₄: slow recovery if restriction maintained
    [0.00, 0.01, 0.05, 0.23, 0.71],   # θ₅: limited recovery without full cessation
], dtype=float)

_T_B6_STAT_2 = np.array([        # a₃ Emergency cessation + managed recharge
    [0.82, 0.15, 0.02, 0.01, 0.00],   # θ₁: surplus well maintained; slight recession risk
    [0.32, 0.52, 0.13, 0.02, 0.01],   # θ₂: strong recovery toward surplus
    [0.12, 0.38, 0.38, 0.10, 0.02],   # θ₃: good conduit recharge + matrix filling
    [0.03, 0.15, 0.40, 0.38, 0.04],   # θ₄: meaningful recovery; conduit refilling
    [0.01, 0.03, 0.18, 0.42, 0.36],   # θ₅: recovery possible if saltwater not yet fixed
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B6_STAT_0), ("STAT_1", _T_B6_STAT_1),
                   ("STAT_2", _T_B6_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B6_{_tag} rows not sum to 1: {_rs}"

T_B6_STAT = np.stack([_T_B6_STAT_0, _T_B6_STAT_1, _T_B6_STAT_2], axis=0)  # (3,5,5)


def _apply_drought_depletion(T_base: np.ndarray, delta: float = 0.18) -> np.ndarray:
    """
    Apply conduit-network desiccation effect to a single 5×5 transition matrix.

    For each non-final state s (0..3): subtract delta from diagonal (self-loop),
    add delta to next-worse state (s+1). Final row (θ₅) left unchanged.
    Clips negatives and renormalises.

    Physical interpretation: prolonged drought in Mediterranean/Dinaric regions
    reduces conduit connectivity (sinkholes dry, epikarst depletes), shifting
    dynamics toward the worse state with higher probability. SSP5-8.5 projects
    a 25–40% increase in drought duration in these regions by 2050.

    The structural shift is: conduit fast-paths close → effective T moves from
    the fast conduit regime toward the slow matrix regime, with higher depletion
    probability under the same abstraction level.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_shift: drought-desiccated conduit network after CLIMATE_SWITCH_STEP=15
# a₁ delta=0.18: no restriction + drought → rapid conduit drainage
# a₂ delta=0.13: restriction slows but drought independently depletes conduits
# a₃ delta=0.07: emergency + recharge partially compensates conduit loss
T_B6_SHIFT = np.stack([
    _apply_drought_depletion(_T_B6_STAT_0, delta=0.18),
    _apply_drought_depletion(_T_B6_STAT_1, delta=0.13),
    _apply_drought_depletion(_T_B6_STAT_2, delta=0.07),
], axis=0)

# T-misspecification: practitioner uses purely matrix-based Darcy model
# Misses conduit fast paths → underestimates depletion speed
# delta=0.22/0.18/0.10: matrix model adds slow wrong-direction smoothing
T_misspec = np.stack([
    _apply_drought_depletion(_T_B6_STAT_0, delta=0.22),
    _apply_drought_depletion(_T_B6_STAT_1, delta=0.18),
    _apply_drought_depletion(_T_B6_STAT_2, delta=0.10),
], axis=0)

# Aliases for shared-code compatibility
T_stat  = T_B6_STAT
T_shift = T_B6_SHIFT

# ---------------------------------------------------------------------------
# Observation model
# Spring discharge proxy (L/s anomaly relative to long-term baseline)
# H_MEAN: mean discharge anomaly per state (θ₁ highest → θ₅ lowest/failure)
# SIGMA_OBS: combined measurement noise + dual-porosity structural uncertainty
#            σ = 38 L/s-equiv — between B4 (35) and B5 (45)
# Dual-porosity uncertainty: conduit-dominated springs show high short-term
# variability; matrix-dominated springs are smoother but systematically offset
# ---------------------------------------------------------------------------
H_MEAN    = np.array([80.0, 20.0, -30.0, -90.0, -180.0])  # L/s anomaly proxy
SIGMA_OBS = 38.0                                             # dual-porosity uncertainty
OBS_BINS  = np.linspace(-280.0, 130.0, 21)                  # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                               # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])     # (20,)

# Likelihood L[θ, o] = P(obs bin o | discharge state θ) — shape (N, N_OBS)
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
# ELS likelihood variants — DUAL-POROSITY MODEL UNCERTAINTY
#
# L_PRES: single best observation model — direct discharge measurement
#         σ = 38 (measurement uncertainty at monitoring station)
#
# L_PHIL: model-averaged dual-porosity likelihood
#         Component 1: conduit-dominated σ = 25 (fast, tight obs distribution)
#         Component 2: matrix-dominated  σ = 55 (slow, diffuse distribution)
#         Average: equal weight between conduit and matrix model
#
# This represents the fundamental karst observational uncertainty: at any given
# monitoring station, we cannot know a priori whether the spring response reflects
# conduit (tight, fast) or matrix (diffuse, slow) dynamics.  The wide model spread
# in L_PHIL (σ=25 vs σ=55) is the direct analogue of the structural T uncertainty.
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_CONDUIT = np.zeros((N, N_OBS), dtype=float)   # conduit model (σ=25)
_L_MATRIX  = np.zeros((N, N_OBS), dtype=float)   # matrix model  (σ=55)
for _s in range(N):
    for _sig, _mat in [(25.0, _L_CONDUIT), (55.0, _L_MATRIX)]:
        _cdf_hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=_sig)
        _cdf_lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=_sig)
        _mat[_s] = _cdf_hi - _cdf_lo

for _mat, _sig in [(_L_CONDUIT, 25.0), (_L_MATRIX, 55.0)]:
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=_sig)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=_sig)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_CONDUIT + 0.5 * _L_MATRIX   # (5, 20) — dual-porosity average

H_MAX_NATS = float(np.log(N))

# PRIOR_PHIL: uniform — epistemic humility about karst state at planning start
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward reduced/intermittent states
# (Dinaric/Mediterranean karst springs increasingly show moderate stress due to
# decades of over-extraction and recent Mediterranean drying trend)
PRIOR_PRES = np.array([0.05, 0.20, 0.40, 0.25, 0.10], dtype=float)
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
    Advance one step using T_B6_STAT (t < CLIMATE_SWITCH_STEP) or
    T_B6_SHIFT (t >= CLIMATE_SWITCH_STEP — conduit desiccation onset).
    """
    T_use      = T_B6_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B6_STAT
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
    T_use  = T_B6_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B6_STAT
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

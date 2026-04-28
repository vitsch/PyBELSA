# =============================================================================
# pomdp_env_b8.py  —  Transboundary Aquifer POMDP (Multi-Agent: Stampriet STAS)
# Project  : ELS_NEW / P_Base8  (Benchmark 8 — Stampriet Transboundary Aquifer)
# Plan ref : P_Base/docs/experiment_plan2.md §12.3
# Date     : 2026-04-25
# Usage    : import pomdp_env_b8 as env
# Data src : IGRAC TWAP Stampriet Transboundary Aquifer System data
#            Baba Sy (2009) Evaluation of STAS recharge — IGRAC Report
#            GRACE-TELLUS RL06 mascon product (NASA PO.DAAC)
#            Seyler et al. (2009) SADC Groundwater Atlas
#            Kirchner & Van der Merwe (2016) Stampriet monitoring data
#            IGRAC (2018) Transboundary Aquifer Assessment Programme (TWAP)
# =============================================================================
"""
POMDP environment for the Stampriet Transboundary Aquifer System (STAS).
Benchmark 8 in the ELS NW benchmark suite.

Physical context
----------------
The Stampriet Transboundary Aquifer System (STAS) is a Kalahari sandstone aquifer
spanning ~87,000 km² across Namibia (~70% of recharge area), Botswana (~20%), and
South Africa (~10%).  It supports pastoral, agricultural, and domestic water supply
for ~150,000 people with no surface-water alternatives in this semi-arid region.

GRACE-TELLUS observations show steady depletion since 2002 (Baba Sy 2009;
Kirchner & Van der Merwe 2016).  No binding transboundary management framework
exists — the 2009 SADC Groundwater Management Initiative provides only voluntary
guidelines.  Each country extracts independently under national licence regimes.

The defining feature of B8 is ENDOGENOUS GAME-THEORETIC T UNCERTAINTY:
The transition matrix T depends on the hidden extraction strategies of Botswana
and South Africa, which the decision-maker (Namibia) cannot observe.  Three
regimes are possible at any decision step:

  T_COOP   : Cooperative — both neighbors voluntarily reduce extraction
              (e.g., under a new SADC binding agreement)
  T_NEUTRAL: Mixed — neighbors apply business-as-usual extraction
              (current observed regime; this is T_stat)
  T_DEFECT : Defective — both neighbors escalate extraction
              (e.g., drought-driven food insecurity, diplomatic breakdown)

Unlike B1–B7 where T uncertainty is climatic/parametric/structural, B8 T
uncertainty is ENDOGENOUS — it depends on what rational strategic agents do,
and those strategies evolve in response to the same observations that Namibia
uses.  Classical POMDP (SARSOP/SDP_S) must assume a fixed T; ELS_Phil's
model-averaging over {T_COOP, T_NEUTRAL, T_DEFECT} is the natural representation
of this strategic uncertainty without game-theoretic computation.

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, a regional drought (consistent with CMIP6 RCP8.5
Southern Africa projections) triggers food-security stress in Botswana and
South Africa, causing defection from informal cooperation — T_NEUTRAL → T_DEFECT.
This is a "governance tipping point" triggered by an external climate shock.

State space (TWSA relative to long-term sustainable STAS storage baseline)
---------------------------------------------------------------------------
θ₁ : Surplus       (TWSA > +50 mm WE)    — full extraction available
θ₂ : Near-balanced (−50 to +50 mm WE)   — sustainable under current regime
θ₃ : Stressed      (−150 to −50 mm WE)  — active management needed
θ₄ : Critical      (−300 to −150 mm WE) — near-irreversible depletion
θ₅ : Depleted      (TWSA < −300 mm WE)  — 50+ year recovery; transboundary conflict

Action space (Namibia's unilateral management options)
------------------------------------------------------
a₁ : Unrestricted  (full licence extraction — maximize national benefit)
a₂ : Cooperative   (voluntary 25% reduction + diplomatic engagement)
a₃ : Emergency     (unilateral 60% moratorium + formal SADC complaint)

Reward function
---------------
Units: $M-equiv/year (net pastoral/agricultural/domestic benefit)
  a₁ θ₁: max economic return in well-hydrated system
  a₁ θ₅: catastrophic — livestock failure + crop loss + diplomatic friction = −600
  a₃ θ₅: moratorium avoids −600 at ~$80M cost → net +120
  a₃ θ₁: unnecessary moratorium in surplus → large economic loss = −80

Multi-agent reward calibration (IGRAC TWAP 2018 economic valuation):
  Full extraction (θ₁): Namibia water benefit ~$80M/year
  Critical depletion (θ₅, a₁): ~$600M/year (livestock failure + desalination)
  Diplomatic framing: a₂ has positive externality benefit (+10–15 over a₁ in θ₃)
    because cooperative engagement may shift neighbors toward T_COOP

T-ensemble semantic meanings (B8 novelty):
  T_COOP    (T_COOP neighbor strategy): slower depletion; recovery more likely
  T_NEUTRAL (T_stat = Nash equilibrium): moderate depletion; current baseline
  T_DEFECT  (T_shift = governance breakdown): fast depletion; recovery harder

T_misspec: single-agent practitioner ignores transboundary dynamics entirely,
  assumes T = T_COOP (over-optimistic: "neighbors always cooperate")
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year annual transboundary management horizon
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # governance breakdown (drought → defection) at step 15

N = 5   # aquifer storage stages
M = 3   # Namibia management actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Surplus (TWSA > +50 mm WE) — full extraction sustainable",
    "θ₂ Near-balanced (−50 to +50 mm WE) — current regime stable",
    "θ₃ Stressed (−150 to −50 mm WE) — active management needed",
    "θ₄ Critical (−300 to −150 mm WE) — near-irreversible depletion",
    "θ₅ Depleted (TWSA < −300 mm WE) — transboundary conflict; 50+ yr recovery",
]
FAILURE_STATE = 4   # θ₅ — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Unrestricted (full national licence extraction)",
    "a₂ Cooperative (voluntary 25% reduction + diplomatic engagement)",
    "a₃ Emergency (60% unilateral moratorium + SADC formal complaint)",
]
ACTION_COST = np.array([0.0, 20.0, 80.0])   # $M/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $M-equiv/year net benefit (pastoral + agricultural + domestic)
#
# Multi-agent design principle (IGRAC TWAP 2018 calibration):
#   a₁ Unrestricted: max national benefit in θ₁-θ₂; depletion externality in θ₄-θ₅
#   a₂ Cooperative: moderate national cost; positive diplomatic externality in θ₃
#   a₃ Emergency: large national cost but avoids catastrophic depletion penalty
#
# Note: R[a₂, θ₃] = +65 > R[a₁, θ₃] = -20 — cooperation has positive net benefit
#       in stressed state (avoids tipping to θ₄ where costs accelerate sharply)
#       R[a₁, θ₅] = -600 — highest magnitude in B8 (transboundary conflict)
#       R[a₃, θ₅] = +120 — moratorium avoids -600 at $80M cost
# ---------------------------------------------------------------------------
R = np.array([
    [ 80.0,  50.0, -20.0, -150.0, -600.0],   # a₁ Unrestricted
    [ 30.0,  45.0,  65.0,   30.0, -150.0],   # a₂ Cooperative
    [-80.0, -30.0,  30.0,   80.0,  120.0],   # a₃ Emergency moratorium
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices — T_B8_NEUTRAL (Nash equilibrium; T_stat)
# T[action, s, s'] : rows = from-state, cols = to-state; rows sum to 1
#
# T_NEUTRAL represents the current observed STAS depletion regime where
# all three countries apply their national extraction licences without
# binding coordination.
#
# Calibration to Kirchner & Van der Merwe (2016) STAS monitoring data:
#   - θ₂ self-loop under a₁ = 0.55 (moderate stability at near-balanced)
#   - θ₄ near-absorbing under a₁ (P(θ₄→θ₅|a₁)=0.36 per year)
#   - Recovery from θ₄ under a₃ = 0.32 (consistent with Kalahari sandstone
#     recharge timescale ~5–10 years per IGRAC TWAP 2018)
# ---------------------------------------------------------------------------
_T_B8_NEUTRAL_0 = np.array([        # a₁ Unrestricted (Nash equilibrium)
    [0.60, 0.28, 0.10, 0.02, 0.00],   # θ₁: moderate drift toward θ₂
    [0.05, 0.55, 0.30, 0.08, 0.02],   # θ₂: steady depletion under BAU
    [0.00, 0.08, 0.48, 0.35, 0.09],   # θ₃: significant depletion
    [0.00, 0.01, 0.08, 0.55, 0.36],   # θ₄: near-irreversible under BAU
    [0.00, 0.00, 0.02, 0.10, 0.88],   # θ₅: near-absorbing depleted state
], dtype=float)

_T_B8_NEUTRAL_1 = np.array([        # a₂ Cooperative (voluntary reduction)
    [0.75, 0.20, 0.04, 0.01, 0.00],   # θ₁: well-maintained
    [0.15, 0.60, 0.20, 0.04, 0.01],   # θ₂: stable + some recovery
    [0.03, 0.18, 0.55, 0.21, 0.03],   # θ₃: partial mitigation
    [0.01, 0.05, 0.20, 0.62, 0.12],   # θ₄: slow recovery; limited by neighbors
    [0.00, 0.01, 0.06, 0.22, 0.71],   # θ₅: limited recovery under unilateral action
], dtype=float)

_T_B8_NEUTRAL_2 = np.array([        # a₃ Emergency moratorium (unilateral)
    [0.82, 0.15, 0.02, 0.01, 0.00],   # θ₁: very well maintained
    [0.30, 0.55, 0.13, 0.02, 0.00],   # θ₂: strong recovery tendency
    [0.08, 0.28, 0.48, 0.14, 0.02],   # θ₃: significant recovery with moratorium
    [0.02, 0.10, 0.32, 0.48, 0.08],   # θ₄: recovery achievable unilaterally
    [0.00, 0.02, 0.12, 0.32, 0.54],   # θ₅: partial recovery; limited by neighbors
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("NEUTRAL_0", _T_B8_NEUTRAL_0), ("NEUTRAL_1", _T_B8_NEUTRAL_1),
                   ("NEUTRAL_2", _T_B8_NEUTRAL_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B8_{_tag} rows not sum to 1: {_rs}"

T_B8_NEUTRAL = np.stack([_T_B8_NEUTRAL_0, _T_B8_NEUTRAL_1, _T_B8_NEUTRAL_2], axis=0)


# ---------------------------------------------------------------------------
# Multi-agent T ensemble: cooperative and defective neighbor scenarios
# ---------------------------------------------------------------------------

def _apply_defection_shift(T_base: np.ndarray, delta: float = 0.14) -> np.ndarray:
    """
    Apply neighbor-defection dynamics to a single 5×5 T matrix.

    Physical interpretation: when Botswana and South Africa increase extraction
    (defection from informal cooperation), the net STAS water budget deteriorates
    faster regardless of Namibia's action.  For each non-final state s (0..3):
    subtract delta from diagonal (self-loop), add delta to next-worse state (s+1).

    Calibrated to IGRAC TWAP 2018: coordinated defection by two countries
    extracts an additional ~15–20% above sustainable yield, driving ~0.12–0.18
    additional annual probability of state deterioration per step.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


def _apply_coop_benefit(T_base: np.ndarray, delta: float = 0.08) -> np.ndarray:
    """
    Apply neighbor-cooperation benefit to a single 5×5 T matrix.

    Physical interpretation: when Botswana and South Africa voluntarily reduce
    extraction (cooperation), the net STAS depletion rate decreases.  For each
    non-final state s (0..3): subtract delta from the forward-depletion entry
    (s→s+1), add delta back to the self-loop (s→s).  θ₅ row unchanged.

    This is the inverse of _apply_defection_shift: cooperation reduces the
    probability of advancing to a worse state, increasing self-stability.

    Calibrated to SADC voluntary reduction scenario: 10–15% extraction decrease
    by neighbors → ~0.06–0.10 reduction in annual forward-depletion probability.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s + 1] -= delta   # reduce forward depletion probability
        T_new[s, s]     += delta   # increase self-stability
    T_new[N - 1, :] = T_base[N - 1, :]  # θ₅ row unchanged
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_B8_DEFECT: governance breakdown — both neighbors escalate extraction
# a₁ delta=0.16: Namibia also unrestricted → fastest depletion
# a₂ delta=0.12: diplomatic engagement partially offsets defection
# a₃ delta=0.08: unilateral moratorium substantially mitigates defection impact
T_B8_DEFECT = np.stack([
    _apply_defection_shift(_T_B8_NEUTRAL_0, delta=0.16),
    _apply_defection_shift(_T_B8_NEUTRAL_1, delta=0.12),
    _apply_defection_shift(_T_B8_NEUTRAL_2, delta=0.08),
], axis=0)

# T_B8_COOP: voluntary cooperation — both neighbors reduce extraction
# a₁ delta=0.08: Namibia still extracts fully but neighbors cooperate
# a₂ delta=0.09: cooperative Namibia + cooperative neighbors → best recovery
# a₃ delta=0.06: moratorium less marginal benefit when neighbors already cooperate
T_B8_COOP = np.stack([
    _apply_coop_benefit(_T_B8_NEUTRAL_0, delta=0.08),
    _apply_coop_benefit(_T_B8_NEUTRAL_1, delta=0.09),
    _apply_coop_benefit(_T_B8_NEUTRAL_2, delta=0.06),
], axis=0)

# Validate DEFECT and COOP
for _tag, _mat in [("DEFECT", T_B8_DEFECT), ("COOP", T_B8_COOP)]:
    _rs = _mat.sum(axis=2)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B8_{_tag} rows not sum to 1"

# Aliases for shared-code compatibility
T_stat  = T_B8_NEUTRAL  # Nash equilibrium = stationary baseline
T_shift = T_B8_DEFECT   # governance breakdown = nonstationary shift

# T_misspec: single-agent practitioner assumes neighbors always cooperate
# but uses a SLIGHTLY MORE OPTIMISTIC model than actual T_COOP
# (delta=0.10 instead of COOP's 0.08 — "our neighbors will definitely cooperate fully")
# Represents naive single-agent POMDP modelling ignoring game-theoretic dynamics.
T_misspec = np.stack([
    _apply_coop_benefit(_T_B8_NEUTRAL_0, delta=0.10),
    _apply_coop_benefit(_T_B8_NEUTRAL_1, delta=0.10),
    _apply_coop_benefit(_T_B8_NEUTRAL_2, delta=0.06),
], axis=0)

# ---------------------------------------------------------------------------
# Observation model
# GRACE-TELLUS TWSA regional storage anomaly (STAS extent)
# H_MEAN: mean TWSA per state (mm WE, relative to long-term STAS baseline)
# SIGMA_OBS: GRACE aggregation + STAS lateral heterogeneity (σ=42 mm WE)
#   Calibration: GRACE RL06 mascon uncertainty ~30–50 mm WE for Kalahari region
#   (larger than B5 NCP because STAS has higher lateral heterogeneity from
#   dual-porosity Kalahari sediments + patchy recharge zones)
# ---------------------------------------------------------------------------
H_MEAN    = np.array([60.0, 0.0, -80.0, -200.0, -360.0])  # mm WE TWSA
SIGMA_OBS = 42.0    # GRACE + heterogeneity uncertainty
OBS_BINS  = np.linspace(-460.0, 160.0, 21)                 # 21 edges → 20 bins
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
# L_PRES: single GRACE RL06 mascon model (σ=42 — primary satellite data)
# L_PHIL: model-averaged
#   Component 1: GRACE mascon σ=35 (higher-resolution CRI-filtered product)
#   Component 2: sparse bore network σ=55 (STAS monitoring bore interpolation)
#   L_PHIL = 0.5 * L_GRACE + 0.5 * L_BORE
#   Reflects ELS's epistemic uncertainty about WHICH data source to trust:
#   GRACE aggregates over 300 km footprint (includes confounding surface water);
#   bore network is local but extremely sparse in Kalahari (~1 bore per 1000 km²)
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_GRACE = np.zeros((N, N_OBS), dtype=float)
_L_BORE  = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    for _mat, _sig in [(_L_GRACE, 35.0), (_L_BORE, 55.0)]:
        _hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=_sig)
        _lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=_sig)
        _mat[_s] = _hi - _lo

for _mat, _sig in [(_L_GRACE, 35.0), (_L_BORE, 55.0)]:
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=_sig)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=_sig)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_GRACE + 0.5 * _L_BORE   # (5, 20)

H_MAX_NATS = float(np.log(N))

# ---------------------------------------------------------------------------
# Priors
# ---------------------------------------------------------------------------
# PRIOR_PHIL: uniform — no prior assumption about STAS state
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward θ₃ (stressed) — GRACE shows STAS is in active decline;
# planning typically begins when the trend is already visible in monitoring data.
# Calibrated to IGRAC TWAP 2018 baseline assessment: STAS 60% of wells show
# declining trends consistent with θ₃ (−50 to −150 mm WE range).
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
    Advance one step.
    t < CLIMATE_SWITCH_STEP : T_B8_NEUTRAL (Nash equilibrium)
    t >= CLIMATE_SWITCH_STEP: T_B8_DEFECT (governance breakdown)
    """
    T_use      = T_B8_DEFECT if t >= CLIMATE_SWITCH_STEP else T_B8_NEUTRAL
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
    T_use  = T_B8_DEFECT if t >= CLIMATE_SWITCH_STEP else T_B8_NEUTRAL
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
    print("=" * 60)
    print("pomdp_env_b8  — validation report (Benchmark 8 Stampriet STAS)")
    print("=" * 60)

    assert R.shape == (M, N), f"R shape {R.shape}"
    print(f"R shape: {R.shape}  OK")

    for regime_name, T_mat in [
        ("T_B8_NEUTRAL", T_B8_NEUTRAL), ("T_B8_DEFECT", T_B8_DEFECT),
        ("T_B8_COOP", T_B8_COOP), ("T_misspec", T_misspec),
    ]:
        assert T_mat.shape == (M, N, N)
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), f"{regime_name} rows: {rs}"
        assert (T_mat >= 0).all()
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # B8-specific: T_DEFECT should deplete faster than T_NEUTRAL under a₁
    depl_neutral = sum(T_B8_NEUTRAL[0, s, s+1] for s in range(N-1))
    depl_defect  = sum(T_B8_DEFECT[0, s, s+1] for s in range(N-1))
    assert depl_defect > depl_neutral, \
        f"T_DEFECT should have higher depletion than T_NEUTRAL under a₁"
    print(f"DEFECT > NEUTRAL depletion (a₁):  {depl_defect:.3f} > {depl_neutral:.3f}  OK")

    # T_COOP should deplete slower than T_NEUTRAL under a₁
    depl_coop = sum(T_B8_COOP[0, s, s+1] for s in range(N-1))
    assert depl_coop < depl_neutral, \
        f"T_COOP should have lower depletion than T_NEUTRAL under a₁"
    print(f"COOP < NEUTRAL depletion (a₁):  {depl_coop:.3f} < {depl_neutral:.3f}  OK")

    # T_misspec (over-optimistic cooperative) should be even more optimistic than COOP
    depl_misspec = sum(T_misspec[0, s, s+1] for s in range(N-1))
    assert depl_misspec < depl_coop, \
        f"T_misspec (over-optimistic) should be < T_COOP depletion: {depl_misspec:.3f} < {depl_coop:.3f}"
    print(f"misspec < COOP depletion (a₁):  {depl_misspec:.3f} < {depl_coop:.3f}  OK")

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

    print("=" * 60)
    print("All checks passed.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Module-level exports
# ---------------------------------------------------------------------------
__all__ = [
    "SEED", "N_MC", "T", "GAMMA", "CLIMATE_SWITCH_STEP",
    "N", "M", "N_OBS",
    "STATE_LABELS", "ACTION_LABELS", "ACTION_COST",
    "FAILURE_STATE",
    "R", "T_stat", "T_shift", "T_misspec",
    "T_B8_NEUTRAL", "T_B8_DEFECT", "T_B8_COOP",
    "H_MEAN", "SIGMA_OBS", "OBS_BINS", "OBS_BIN_CENTRES", "LIKELIHOOD",
    "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

if __name__ == "__main__":
    validate()

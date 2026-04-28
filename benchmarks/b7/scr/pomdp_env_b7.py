# =============================================================================
# pomdp_env_b7.py  —  Coastal Aquifer Saltwater Intrusion POMDP (Tipping Point)
# Project  : ELS_NEW / P_Base7  (Benchmark 7 — Coastal Saltwater Intrusion)
# Plan ref : P_Base/docs/experiment_plan2.md §12.2
# Date     : 2026-04-25
# Usage    : import pomdp_env_b7 as env
# Data src : CMWU UNESCO-IHE Gaza coastal monitoring reports
#            PWNT/Deltares MIPWA model outputs (open access)
#            Werner et al. (2013) Seawater intrusion review, Adv Water Resour
#            Post et al. (2018) Coastal GW management, Nat Rev Earth Environ
#            Revelle & Schwartz (1955) On the possible uses of seawater, J Mar Res
# =============================================================================
"""
POMDP environment for the Coastal Aquifer Saltwater Intrusion benchmark.
Benchmark 7 in the ELS NW benchmark suite.

Physical context
----------------
Coastal aquifers worldwide face saltwater intrusion driven by over-abstraction
and sea-level rise.  The Gaza coastal aquifer (Palestine/CMWU) is the world's
most critically over-abstracted coastal aquifer (2.5 × sustainable yield);
Dutch coastal dunes (PWNT/Deltares) are the best-monitored system globally.

The defining physical feature is the TIPPING-POINT structure of saltwater
intrusion dynamics:

  Safe zone (θ₁–θ₂): T is near-deterministic, slow, reversible under reduced
    abstraction.  SARSOP's alpha-vectors perform well in this zone.

  Tipping zone (θ₃ — intrusion front near well-field): T becomes highly
    nonlinear and stochastic.  Small perturbations can trigger rapid advance to
    θ₄–θ₅.  The T matrix has large off-diagonal variance — SARSOP's offline
    alpha-vectors (solved on stationary T_stat) mis-estimate the action-value
    function at this critical state.

  Post-tipping (θ₄–θ₅): T is HYSTERETIC — recovery requires far more effort
    than intrusion took.  P(recovery | a₃, θ₄) << P(intrusion | a₁, θ₂).
    This asymmetry is the core B7 novelty not present in B1–B6.

ELS advantage at B7:
  ELS_Int detects the tipping zone via entropy increase: as the system enters
  θ₃, the belief becomes highly uncertain (several states nearly equiprobable),
  driving entropy up and α_t up, which switches ELS_Int from Philosophical
  (satisficing, slow) to Prescriptive (risk-averse, maximally cautious).
  SARSOP cannot adapt post-solve; its alpha-vectors were computed assuming
  the tipping hazard is fully known and linear in T.

Observation model (log-normal — B7 novelty):
  Chloride concentration is inherently positive and log-normally distributed
  in groundwater monitoring.  This is the first benchmark in the suite to use
  a log-normal likelihood, testing ELS's robustness to non-Gaussian obs.

  H_MEAN_LOG = log([100, 250, 700, 2000, 5000]) in mg/L — 5 Cl states
  SIGMA_LOG   = 0.5 (log-space standard deviation)
  OBS_BINS    = 20 equally-spaced bins in log-Cl space: ln(30) to ln(10000)

Non-stationarity source
-----------------------
At CLIMATE_SWITCH_STEP=15, sea-level rise (CMIP6 RCP8.5 ~0.3 m by 2050 in
Mediterranean) reduces freshwater head gradient, amplifying intrusion pressure.
The climate shift PREFERENTIALLY AMPLIFIES THE TIPPING ZONE (θ₃):
  - Linear states (θ₁, θ₂): uniform forward shift delta=0.12 (a₁), 0.08 (a₂)
  - Tipping state (θ₃): amplified shift delta=0.18 (a₁), 0.12 (a₂)
  - Post-tipping (θ₄, θ₅): unchanged (already near-absorbing)

State space (chloride concentration categories)
------------------------------------------------
θ₁ : Fresh         (Cl < 150 mg/L)  — WHO potable threshold safely met
θ₂ : Marginal      (Cl 150–400 mg/L) — brackish alert zone; potable with treatment
θ₃ : Approaching   (Cl 400–1000 mg/L) — intrusion front near well-field; TIPPING ZONE
θ₄ : Compromised   (Cl 1000–3000 mg/L) — well-field operationally impaired
θ₅ : Saline        (Cl > 3000 mg/L) — WHO 3× threshold; 30-year-scale recovery

Action space
------------
a₁ : Continue     (full abstraction at licensed allocation)
a₂ : Reduce 30%   (partial demand management + monitoring enhancement)
a₃ : Reduce 60% + injection  (managed aquifer recharge via coastal barrier wells)

Reward function
---------------
Units: $k-equiv/year (net economic benefit from water supply − desalination cost)
  a₁ in θ₁: max water supply benefit without restriction ≈ +100
  a₁ in θ₅: catastrophic — desalination + aquifer rehab ≈ −700 per year
  a₃ in θ₅: avoids −700 at ~$150k injection cost → net +150 per year
  a₃ in θ₁: unnecessary injection/restriction in fresh zone → −80 opportunity cost

Data source calibration:
  Reward magnitudes: CMWU Coastal Aquifer Management Program (2020);
    Post et al. (2018) — desalination cost estimates for coastal GW failure
  State boundaries: WHO (2011) Guidelines for Drinking Water Quality;
    Werner et al. (2013) — global saltwater intrusion review; Cl thresholds

Aliases for shared-code compatibility
--------------------------------------
T_stat  = T_B7_STAT  (pre-climate base dynamics)
T_shift = T_B7_SHIFT (sea level rise + abstraction pressure; tipping amplified)
T_misspec = T_B7_STAT perturbed +15% linear shift (misses tipping nonlinearity)
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
SEED                = 2024
N_MC                = 200
T                   = 30       # 30-year annual coastal management horizon
GAMMA               = 0.97
CLIMATE_SWITCH_STEP = 15       # sea-level rise amplifies tipping at step 15

N = 5   # number of chloride-concentration states
M = 3   # number of management actions

# ---------------------------------------------------------------------------
# State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Fresh (Cl < 150 mg/L) — potable without treatment",
    "θ₂ Marginal (Cl 150–400 mg/L) — brackish alert zone",
    "θ₃ Approaching (Cl 400–1000 mg/L) — intrusion front near well-field [TIPPING ZONE]",
    "θ₄ Compromised (Cl 1000–3000 mg/L) — well-field operationally impaired",
    "θ₅ Saline (Cl > 3000 mg/L) — irreversible 30-yr scale",
]
FAILURE_STATE = 4   # θ₅ index — used for P_fail metric

# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Continue (full allocation — no restriction)",
    "a₂ Reduce 30% (demand management + enhanced monitoring)",
    "a₃ Reduce 60% + injection (barrier well managed recharge)",
]
ACTION_COST = np.array([0.0, 25.0, 150.0])   # $k/year management cost

# ---------------------------------------------------------------------------
# Reward matrix  R[action, state]  — shape (M, N)
# Units: $k-equiv/year net water supply benefit
#
# Design (calibrated to CMWU/PWNT coastal aquifer economics):
#   a₁ Continue: max benefit in θ₁-θ₂; catastrophic in θ₄-θ₅
#   a₂ Reduce:   balanced; tipping prevention value in θ₃
#   a₃ Injection: expensive in θ₁-θ₂; critical in θ₄-θ₅ (avoids -700)
#
# Tipping-point reward asymmetry:
#   R[a₁, θ₃] = +10 — BAU still profitable at tipping zone, but hazardous
#   R[a₁, θ₄] = -200 — well-field compromise very costly
#   R[a₁, θ₅] = -700 — saltwater failure: desalination + rehab cost
#   R[a₃, θ₅] = +150 — injection in failure avoids -700 at $150k cost
# ---------------------------------------------------------------------------
R = np.array([
    [100.0,  65.0,  10.0, -200.0, -700.0],   # a₁ Continue (full allocation)
    [ 45.0,  55.0,  60.0,  -50.0, -300.0],   # a₂ Reduce 30%
    [-80.0, -20.0,  50.0,  100.0,  150.0],   # a₃ Reduce 60% + injection
], dtype=float)

# ---------------------------------------------------------------------------
# Transition matrices (pre-climate base dynamics)  T_B7_STAT[action, s, s']
# rows = from-state, cols = to-state; rows sum to 1
#
# KEY B7 PROPERTY — TIPPING-POINT ASYMMETRY:
#
# θ₃ row (tipping zone) under a₁:
#   - Self-loop P(θ₃→θ₃) = 0.50 — only 50% stable (cf. 0.70 in θ₂)
#   - P(θ₃→θ₄) = 0.38 — high jump probability once in tipping zone
#   - P(θ₃→θ₅) = 0.07 — rare but catastrophic direct skip possible
#   → This nonlinearity is QUALITATIVELY different from θ₂ (linear: P(θ₂→θ₃)=0.22)
#
# HYSTERESIS in θ₄:
#   - P(θ₄→θ₃ | a₃) = 0.25 — recovery from intrusion very slow
#   - P(θ₂→θ₃ | a₁) = 0.22 — intrusion much faster than recovery
#   → Illustrates hysteretic structure: intrusion is easier than recovery
#
# Calibration to Werner et al. (2013) coastal aquifer dynamics:
#   - θ₃ transition probability reflects Ghyben-Herzberg lens instability
#     (small head changes → large saltwater interface movement)
#   - Recovery timescale under managed recharge: 10-25 years in practice
#     (calibrates θ₄ recovery probabilities to ~0.20-0.30 per year under a₃)
# ---------------------------------------------------------------------------
_T_B7_STAT_0 = np.array([        # a₁ Continue (full allocation, pre-climate)
    [0.80, 0.18, 0.02, 0.00, 0.00],   # θ₁: mostly stable, slow salinisation
    [0.05, 0.70, 0.22, 0.03, 0.00],   # θ₂: steady intrusion advance (linear zone)
    [0.00, 0.05, 0.50, 0.38, 0.07],   # θ₃: TIPPING — highly nonlinear, fast advance
    [0.00, 0.00, 0.03, 0.62, 0.35],   # θ₄: hysteretic, near-absorbing post-tipping
    [0.00, 0.00, 0.02, 0.08, 0.90],   # θ₅: near-absorbing saline failure
], dtype=float)

_T_B7_STAT_1 = np.array([        # a₂ Reduce 30% (demand management)
    [0.88, 0.11, 0.01, 0.00, 0.00],   # θ₁: well-protected
    [0.15, 0.72, 0.11, 0.02, 0.00],   # θ₂: slow advance; some recovery
    [0.02, 0.15, 0.62, 0.19, 0.02],   # θ₃: reduced tipping hazard (but still exists)
    [0.00, 0.02, 0.15, 0.68, 0.15],   # θ₄: slow recovery from intrusion
    [0.00, 0.00, 0.04, 0.18, 0.78],   # θ₅: limited recovery
], dtype=float)

_T_B7_STAT_2 = np.array([        # a₃ Reduce 60% + injection (barrier wells)
    [0.93, 0.07, 0.00, 0.00, 0.00],   # θ₁: very well maintained
    [0.35, 0.58, 0.07, 0.00, 0.00],   # θ₂: strong recovery; tipping essentially zero
    [0.08, 0.30, 0.52, 0.09, 0.01],   # θ₃: injection substantially reduces tipping
    [0.01, 0.04, 0.15, 0.68, 0.12],   # θ₄: slow recovery — hysteresis (harder than intrusion)
    [0.00, 0.01, 0.06, 0.27, 0.66],   # θ₅: limited recovery even with deep restriction
], dtype=float)

# Validate rows sum to 1
for _tag, _mat in [("STAT_0", _T_B7_STAT_0), ("STAT_1", _T_B7_STAT_1),
                   ("STAT_2", _T_B7_STAT_2)]:
    _rs = _mat.sum(axis=1)
    assert np.allclose(_rs, 1.0, atol=1e-9), f"T_B7_{_tag} rows not sum to 1: {_rs}"

T_B7_STAT = np.stack([_T_B7_STAT_0, _T_B7_STAT_1, _T_B7_STAT_2], axis=0)  # (3,5,5)


def _apply_tipping_shift(
    T_base: np.ndarray,
    delta_linear: float = 0.10,
    delta_tipping: float = 0.15,
) -> np.ndarray:
    """
    Apply sea-level rise / increased abstraction pressure to a 5×5 T matrix.

    B7-specific: shift is NON-UNIFORM:
      - Linear states θ₁ (s=0) and θ₂ (s=1): forward shift by delta_linear
      - Tipping state θ₃ (s=2): AMPLIFIED shift by delta_tipping
        (sea-level rise disproportionately destabilises the tipping zone —
         Ghyben-Herzberg theory: small head changes → large interface advance)
      - Post-tipping states θ₄ (s=3) and θ₅ (s=4): unchanged
        (already near-absorbing; further shift has minimal effect)

    Physical interpretation: CMIP6 RCP8.5 projects ~0.3 m sea-level rise by
    2050 in Mediterranean/Gaza; this reduces the freshwater head gradient and
    lowers the effective recirculation barrier at the saltwater interface,
    preferentially accelerating transitions at the tipping threshold.
    """
    T_new = T_base.copy()
    # Linear states: uniform forward shift
    for s in [0, 1]:
        T_new[s, s]     -= delta_linear
        T_new[s, s + 1] += delta_linear
    # Tipping state: amplified forward shift
    T_new[2, 2] -= delta_tipping
    T_new[2, 3] += delta_tipping
    # Post-tipping rows (s=3, s=4): unchanged
    T_new[3, :] = T_base[3, :]
    T_new[4, :] = T_base[4, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new


# T_shift: sea-level rise + abstraction pressure after CLIMATE_SWITCH_STEP=15
# a₁ delta_linear=0.12, delta_tipping=0.18 — strongest shift in all states
# a₂ delta_linear=0.08, delta_tipping=0.12 — moderated by 30% reduction
# a₃ delta_linear=0.04, delta_tipping=0.07 — injection largely compensates
T_B7_SHIFT = np.stack([
    _apply_tipping_shift(_T_B7_STAT_0, delta_linear=0.12, delta_tipping=0.18),
    _apply_tipping_shift(_T_B7_STAT_1, delta_linear=0.08, delta_tipping=0.12),
    _apply_tipping_shift(_T_B7_STAT_2, delta_linear=0.04, delta_tipping=0.07),
], axis=0)

# T-misspecification ablation: practitioner uses a model that:
#  (a) applies only linear shift (misses tipping-zone amplification entirely)
#  (b) uses uniform delta=0.15 — overestimates linear states, misses tipping
# This represents a practitioner using a porous-medium Darcy model (misses
# sharp-interface Ghyben-Herzberg nonlinearity at the tipping threshold)
def _apply_linear_only_shift(T_base: np.ndarray, delta: float = 0.15) -> np.ndarray:
    """Uniform linear shift — misspecified model that misses tipping nonlinearity."""
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]
    T_new = np.clip(T_new, 0.0, 1.0)
    T_new /= T_new.sum(axis=1, keepdims=True)
    return T_new

T_misspec = np.stack([
    _apply_linear_only_shift(_T_B7_STAT_0, delta=0.15),
    _apply_linear_only_shift(_T_B7_STAT_1, delta=0.15),
    _apply_linear_only_shift(_T_B7_STAT_2, delta=0.075),
], axis=0)

# Aliases for shared-code compatibility
T_stat  = T_B7_STAT
T_shift = T_B7_SHIFT

# ---------------------------------------------------------------------------
# Observation model — LOG-NORMAL (B7 novelty vs B1–B6 Gaussian)
# ---------------------------------------------------------------------------
# Chloride concentration (mg/L) is inherently positive and log-normally
# distributed in groundwater.  We work in log-space (natural log of mg/L).
#
# H_MEAN_LOG: mean log(Cl) per state
#   θ₁: log(100) ≈ 4.61  (fresh, Cl~100 mg/L)
#   θ₂: log(250) ≈ 5.52  (marginal, Cl~250 mg/L)
#   θ₃: log(700) ≈ 6.55  (approaching, Cl~700 mg/L)
#   θ₄: log(2000) ≈ 7.60 (compromised, Cl~2000 mg/L)
#   θ₅: log(5000) ≈ 8.52 (saline, Cl~5000 mg/L)
#
# SIGMA_LOG: observation noise in log-space (σ=0.50)
#   Combines: analytical lab precision (±3%), sampling variability (±15%),
#   spatial heterogeneity in monitoring well network (±25%)
#   → σ_log ≈ 0.25–0.55 typical (Werner et al. 2013; Post et al. 2018)
#
# OBS_BINS: 20 equally-spaced bins in log-Cl space from ln(30) to ln(10000)
#   → covers full observed Gaza/PWNT range (30 mg/L background to 10,000 saline)
# ---------------------------------------------------------------------------
H_MEAN_LOG = np.log(np.array([100.0, 250.0, 700.0, 2000.0, 5000.0]))  # log(mg/L)
SIGMA_LOG   = 0.50    # log-space noise σ (log-normal model)
# Expose as SIGMA_OBS for shared-code compatibility
SIGMA_OBS   = SIGMA_LOG

OBS_BINS    = np.linspace(np.log(30.0), np.log(10000.0), 21)  # 21 edges, 20 bins
N_OBS       = len(OBS_BINS) - 1   # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])  # (20,) in log-space

# Likelihood matrix L[θ, o] = P(obs bin o | state θ)  — shape (N, N_OBS)
# Computed via normal CDF differences in log-space (= log-normal CDF in Cl-space)
_L = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN_LOG[_s], scale=SIGMA_LOG)
    _cdf_lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN_LOG[_s], scale=SIGMA_LOG)
    _L[_s]  = _cdf_hi - _cdf_lo

# Mass beyond bin edges → absorbed into first/last bin
_L[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN_LOG, scale=SIGMA_LOG)
_L[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN_LOG, scale=SIGMA_LOG)
_L /= _L.sum(axis=1, keepdims=True)
LIKELIHOOD = _L   # (5, 20)

# ---------------------------------------------------------------------------
# ELS likelihood variants (log-normal model family)
# L_PRES: single log-normal model (σ_log=0.50 — primary monitoring data)
# L_PHIL: model-averaged log-normal
#   Component 1: precision monitoring bore (σ_log=0.40 — less uncertainty)
#   Component 2: field grab sample / regional proxy (σ_log=0.70 — more uncertainty)
#   L_PHIL = 0.5 * L_precise + 0.5 * L_field
#   Reflects ELS's philosophical stance: uncertainty about measurement precision
#   itself (not just the measurement) — consistent with B6 dual-porosity design
# ---------------------------------------------------------------------------
L_PRES = LIKELIHOOD.copy()

_L_PRECISE = np.zeros((N, N_OBS), dtype=float)
_L_FIELD   = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    for _mat, _sig in [(_L_PRECISE, 0.40), (_L_FIELD, 0.70)]:
        _hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN_LOG[_s], scale=_sig)
        _lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN_LOG[_s], scale=_sig)
        _mat[_s] = _hi - _lo

for _mat, _sig in [(_L_PRECISE, 0.40), (_L_FIELD, 0.70)]:
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN_LOG, scale=_sig)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN_LOG, scale=_sig)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_PRECISE + 0.5 * _L_FIELD   # (5, 20)

H_MAX_NATS = float(np.log(N))

# ---------------------------------------------------------------------------
# Priors
# ---------------------------------------------------------------------------
# PRIOR_PHIL: uniform — no prior commitment to Cl state
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES: biased toward θ₂–θ₃ — coastal aquifer planning is typically
# initiated when intrusion is already a known concern (pre-monitoring era)
# Calibrated to Gaza CMWU 2010 baseline: ~60% of monitoring wells above 400 mg/L
PRIOR_PRES = np.array([0.10, 0.30, 0.35, 0.18, 0.07], dtype=float)
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
    Pre-climate (t < CLIMATE_SWITCH_STEP): T_B7_STAT (slow linear + tipping)
    Post-climate (t >= CLIMATE_SWITCH_STEP): T_B7_SHIFT (amplified tipping)
    """
    T_use      = T_B7_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B7_STAT
    next_state = int(rng.choice(N, p=T_use[action, state]))
    obs_idx    = int(rng.choice(N_OBS, p=LIKELIHOOD[next_state]))
    reward     = float(R[action, next_state])
    return next_state, obs_idx, reward


def update_belief(b: np.ndarray, obs_idx: int) -> np.ndarray:
    """Static Bayesian belief update (ELS default — log-normal likelihood)."""
    b_new = LIKELIHOOD[:, obs_idx] * b
    total = b_new.sum()
    return b_new / total if total > 1e-300 else b.copy()


def markov_update_belief(
    b: np.ndarray, obs_idx: int, action: int, t: int
) -> np.ndarray:
    """Full Markovian belief update (predict + correct)."""
    T_use  = T_B7_SHIFT if t >= CLIMATE_SWITCH_STEP else T_B7_STAT
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
    print("pomdp_env_b7  — validation report (Benchmark 7 Coastal Saltwater)")
    print("=" * 60)

    assert R.shape == (M, N), f"R shape {R.shape}"
    print(f"R shape: {R.shape}  OK")

    for regime_name, T_mat in [("T_B7_STAT", T_B7_STAT), ("T_B7_SHIFT", T_B7_SHIFT),
                                ("T_misspec", T_misspec)]:
        assert T_mat.shape == (M, N, N)
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), f"{regime_name} rows: {rs}"
        assert (T_mat >= 0).all()
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # B7-specific: tipping zone (θ₃, a₁) should have higher advance probability
    # than linear zone (θ₂, a₁) in both stat and shift regimes
    for T_mat, lbl in [(T_B7_STAT, "STAT"), (T_B7_SHIFT, "SHIFT")]:
        p_theta3_advance = T_mat[0, 2, 3] + T_mat[0, 2, 4]   # P(θ₃→θ₄ or θ₅ | a₁)
        p_theta2_advance = T_mat[0, 1, 2] + T_mat[0, 1, 3]   # P(θ₂→θ₃ or θ₄ | a₁)
        assert p_theta3_advance > p_theta2_advance, \
            f"T_{lbl}: tipping zone should have higher advance probability than linear zone"
        print(f"T_{lbl} tipping nonlinearity:  "
              f"P(θ₃→θ₄⁺|a₁)={p_theta3_advance:.3f} > P(θ₂→θ₃⁺|a₁)={p_theta2_advance:.3f}  OK")

    # Hysteresis check: recovery slower than intrusion
    p_intrude  = T_B7_STAT[0, 1, 2]   # P(θ₂→θ₃ | a₁) — intrusion rate
    p_recover  = T_B7_STAT[2, 3, 2]   # P(θ₄→θ₃ | a₃) — recovery rate
    assert p_recover < p_intrude, \
        f"Hysteresis: P(recovery|a₃)={p_recover:.3f} should < P(intrusion|a₁)={p_intrude:.3f}"
    print(f"Hysteresis check:  P(intrude|a₁)={p_intrude:.3f} > P(recover|a₃)={p_recover:.3f}  OK")

    # Log-normal obs model check
    assert LIKELIHOOD.shape == (N, N_OBS)
    assert np.allclose(LIKELIHOOD.sum(axis=1), 1.0, atol=1e-9)
    print(f"LIKELIHOOD (log-normal) shape {LIKELIHOOD.shape}  row sums OK")

    # State separation check: modal bin should increase monotonically
    modal_bins = np.argmax(LIKELIHOOD, axis=1)
    assert np.all(np.diff(modal_bins) >= 0), \
        f"Log-normal modal bins not monotone: {modal_bins}"
    print(f"Log-normal modal bins (monotone): {modal_bins}  OK")

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
    "T_B7_STAT", "T_B7_SHIFT",
    "H_MEAN_LOG", "SIGMA_LOG", "SIGMA_OBS", "OBS_BINS", "OBS_BIN_CENTRES",
    "LIKELIHOOD", "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

if __name__ == "__main__":
    validate()

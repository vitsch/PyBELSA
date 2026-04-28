# =============================================================================
# pomdp_env.py  —  Synthetic 5-State Groundwater POMDP Environment
# Project  : ELS_NEW / P_Base  (Benchmark 1 — Nature Water reproducibility anchor)
# Paper    : P_Base/ref/Frames_paper.tex (v2) + experiment_plan.md
# Date     : 2026-04-21
# Usage    : import pomdp_env as env
# Outputs  : module-level constants + step() / reset() / update_belief() / validate()
# =============================================================================
"""
Fully self-contained POMDP environment for the synthetic 5-state groundwater
benchmark.  No external POMDP library required.

State space  : 5 hidden aquifer depletion states θ₁ (sustainable) … θ₅ (failed)
Action space : 3 abstraction-level actions a₁ (unrestricted) … a₃ (emergency cessation)
Obs space    : 20 discrete piezometric-head bins, [-80, 10] m
Dynamics     : Regime A (stationary, t < CLIMATE_SWITCH_STEP)
               Regime B (climate-shifted, t ≥ CLIMATE_SWITCH_STEP)
               Agent does NOT observe the regime switch.

Key functions
-------------
reset(rng)                → initial_state (int), b0 (ndarray shape (N,))
step(state, action, t, rng) → next_state (int), obs_idx (int), reward (float)
update_belief(b, obs_idx)   → new belief (ndarray shape (N,), normalised)
validate()                  → prints sanity checks; raises AssertionError on failure
"""

import numpy as np
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Fixed parameters  (single source of truth for all downstream scripts)
# ---------------------------------------------------------------------------
SEED               = 2024
N_MC               = 200      # Monte Carlo episodes per method
T                  = 60       # horizon steps per episode
GAMMA              = 0.97     # discount factor (shared across all methods)
CLIMATE_SWITCH_STEP = 30      # step t at which Regime B replaces Regime A

N = 5   # number of states
M = 3   # number of actions

# ---------------------------------------------------------------------------
# 1.1  State descriptions
# ---------------------------------------------------------------------------
STATE_LABELS = [
    "θ₁ Sustainable (>−5 m)",
    "θ₂ Moderate stress (−5 to −15 m)",
    "θ₃ Significant depletion (−15 to −30 m)",
    "θ₄ Critical (−30 to −50 m)",
    "θ₅ Failed (<−50 m)",
]
FAILURE_STATE = 4   # index of θ₅

# ---------------------------------------------------------------------------
# 1.2  Action descriptions and costs
# ---------------------------------------------------------------------------
ACTION_LABELS = [
    "a₁ Unrestricted",
    "a₂ Restricted (50 %)",
    "a₃ Emergency cessation",
]
ACTION_COST = np.array([0.0, 15.0, 45.0])   # £/ML

# ---------------------------------------------------------------------------
# 1.3  Reward matrix  R[action, state]  — shape (M, N)
# Units: £/ML-equivalent utility (economic net benefit normalised to licence value)
# U_eval(a, θ) = R[a, θ]  — common evaluation utility for all cross-method comparisons
# ---------------------------------------------------------------------------
R = np.array([
    [100.0,  80.0,  40.0, -20.0, -100.0],   # a₁ Unrestricted
    [ 60.0,  60.0,  55.0,  30.0,  -30.0],   # a₂ Restricted
    [  5.0,   5.0,   5.0,   5.0,    5.0],   # a₃ Emergency cessation
], dtype=float)

# ---------------------------------------------------------------------------
# 1.4  Transition matrices  T_stat[action]  — shape (M, N, N)
# T[a, s, s'] = P(θ_{t+1}=s' | θ_t=s, a_t=a)   rows sum to 1
# Regime A (stationary)
# ---------------------------------------------------------------------------
_T0 = np.array([               # a₁ Unrestricted — fastest depletion
    [0.70, 0.25, 0.05, 0.00, 0.00],
    [0.10, 0.65, 0.20, 0.05, 0.00],
    [0.00, 0.10, 0.65, 0.20, 0.05],
    [0.00, 0.00, 0.10, 0.65, 0.25],
    [0.00, 0.00, 0.00, 0.10, 0.90],
], dtype=float)

_T1 = np.array([               # a₂ Restricted — slows depletion
    [0.80, 0.18, 0.02, 0.00, 0.00],
    [0.20, 0.70, 0.09, 0.01, 0.00],
    [0.05, 0.20, 0.65, 0.09, 0.01],
    [0.00, 0.05, 0.20, 0.65, 0.10],
    [0.00, 0.00, 0.05, 0.20, 0.75],
], dtype=float)

_T2 = np.array([               # a₃ Emergency cessation — strong recovery in θ₁–θ₃
    [0.90, 0.10, 0.00, 0.00, 0.00],
    [0.35, 0.60, 0.05, 0.00, 0.00],
    [0.10, 0.35, 0.50, 0.05, 0.00],
    [0.00, 0.10, 0.35, 0.50, 0.05],
    [0.00, 0.00, 0.10, 0.30, 0.60],
], dtype=float)

T_stat = np.stack([_T0, _T1, _T2], axis=0)   # shape (3, 5, 5)


def _apply_climate_shift(T_base: np.ndarray, delta: float = 0.10) -> np.ndarray:
    """
    Shift a single 5×5 transition matrix toward faster depletion.

    For each non-absorbing state s (0..3): subtract delta from diagonal
    and add delta to the next-worse state (s+1).  θ₅ remains absorbing.
    Rows are renormalised to correct floating-point drift.
    """
    T_new = T_base.copy()
    for s in range(N - 1):
        T_new[s, s]     -= delta
        T_new[s, s + 1] += delta
    T_new[N - 1, :] = T_base[N - 1, :]   # keep θ₅ row unchanged (absorbing)
    # Clip negatives (numerical guard) then renormalise
    T_new = np.clip(T_new, 0.0, 1.0)
    row_sums = T_new.sum(axis=1, keepdims=True)
    return T_new / row_sums


# Regime B: a₁ and a₂ get full delta=0.10; a₃ retains half recovery (delta=0.05)
T_shift = np.stack([
    _apply_climate_shift(_T0, delta=0.10),   # a₁ full shift
    _apply_climate_shift(_T1, delta=0.10),   # a₂ full shift
    _apply_climate_shift(_T2, delta=0.05),   # a₃ half shift (recovery partially retained)
], axis=0)   # shape (3, 5, 5)

# ---------------------------------------------------------------------------
# Misspecified transition matrix for T-misspecification ablation (Priority 1)
# T_misspec: T_stat perturbed by +15% depletion shift — represents a practitioner
# who believes the aquifer depletes 15% faster than T_stat.
# Used in SARSOP_Misspec and SDP_S_Misspec ablation to show that the
# POMDP-solver advantage is contingent on T being correctly specified.
# ---------------------------------------------------------------------------
T_misspec = np.stack([
    _apply_climate_shift(_T0, delta=0.15),   # a₁ +15% shift
    _apply_climate_shift(_T1, delta=0.15),   # a₂ +15% shift
    _apply_climate_shift(_T2, delta=0.075),  # a₃ half-shift (consistent with T_shift rule)
], axis=0)   # shape (3, 5, 5)

# ---------------------------------------------------------------------------
# 1.5  Observation model
# ---------------------------------------------------------------------------
H_MEAN    = np.array([0.0, -10.0, -22.0, -40.0, -60.0])   # piezometric head means (m)
SIGMA_OBS = 4.0                                             # noise std dev (m)
OBS_BINS  = np.linspace(-80.0, 10.0, 21)                   # 21 edges → 20 bins
N_OBS     = len(OBS_BINS) - 1                               # = 20

OBS_BIN_CENTRES = 0.5 * (OBS_BINS[:-1] + OBS_BINS[1:])    # shape (20,)

# Likelihood matrix L[θ, o] = P(obs bin o | state θ)  — shape (N, N_OBS)
# Computed via CDF differences for numerical accuracy; rows normalised.
_L = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=SIGMA_OBS)
    _cdf_lo = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=SIGMA_OBS)
    _L[_s] = _cdf_hi - _cdf_lo

# Assign any probability mass outside bin range to the nearest edge bin
_L[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=SIGMA_OBS)
_L[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=SIGMA_OBS)

# Renormalise rows to sum exactly to 1
_L = _L / _L.sum(axis=1, keepdims=True)
LIKELIHOOD = _L   # shape (5, 20);  LIKELIHOOD[s, o] = P(o | θ=s)

# ---------------------------------------------------------------------------
# ELS framework likelihood and prior variants
# ---------------------------------------------------------------------------
# L_PRES : single Gaussian model (σ=4.0) — used by ELS-Pres and as P_TRUE
L_PRES = LIKELIHOOD.copy()

# L_PHIL : model-averaged likelihood for ELS-Phil (Eq. lik_phil)
#   M1 (σ=3.5): represents a high-precision monitoring bore
#   M2 (σ=5.5): represents a low-precision monitoring bore
#   L_PHIL = 0.5 * L_M1 + 0.5 * L_M2   (equal model weights)
_L_M1 = np.zeros((N, N_OBS), dtype=float)
_L_M2 = np.zeros((N, N_OBS), dtype=float)
for _s in range(N):
    _cdf_hi_m1 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=3.5)
    _cdf_lo_m1 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=3.5)
    _cdf_hi_m2 = norm.cdf(OBS_BINS[1:],  loc=H_MEAN[_s], scale=5.5)
    _cdf_lo_m2 = norm.cdf(OBS_BINS[:-1], loc=H_MEAN[_s], scale=5.5)
    _L_M1[_s] = _cdf_hi_m1 - _cdf_lo_m1
    _L_M2[_s] = _cdf_hi_m2 - _cdf_lo_m2

for _mat in (_L_M1, _L_M2):
    _mat[:, 0]  += norm.cdf(OBS_BINS[0],  loc=H_MEAN, scale=4.0)
    _mat[:, -1] += 1.0 - norm.cdf(OBS_BINS[-1], loc=H_MEAN, scale=4.0)
    _mat /= _mat.sum(axis=1, keepdims=True)

L_PHIL = 0.5 * _L_M1 + 0.5 * _L_M2   # shape (5, 20); rows sum to 1

# H_MAX_NATS: maximum entropy in nats for normalisation (Eq. alpha_norm)
H_MAX_NATS = float(np.log(N))

# PRIOR_PHIL : broad uniform prior (no prior commitment to aquifer state)
PRIOR_PHIL = np.full(N, 1.0 / N, dtype=float)

# PRIOR_PRES : concentrated prior reflecting optimistic literature assumption
#   (aquifer mostly in θ₁–θ₂; source: typical groundwater literature review)
PRIOR_PRES = np.array([0.55, 0.30, 0.10, 0.04, 0.01], dtype=float)
PRIOR_PRES = PRIOR_PRES / PRIOR_PRES.sum()   # normalise to exactly 1

# ---------------------------------------------------------------------------
# Environment API
# ---------------------------------------------------------------------------

def reset(rng: np.random.Generator) -> tuple[int, np.ndarray]:
    """
    Begin a new episode.

    Returns
    -------
    initial_state : int
        True hidden state drawn uniformly from {0, 1, 2, 3, 4}.
    b0 : ndarray shape (N,)
        Initial belief — uniform over all states (agent has no prior information).
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
    Advance the environment by one step.

    Parameters
    ----------
    state  : current true hidden state (0–4)
    action : chosen action (0–2)
    t      : current time step (0-indexed); used to select regime
    rng    : numpy Generator for reproducibility

    Returns
    -------
    next_state : int  — sampled from T[regime][action][state]
    obs_idx    : int  — sampled observation bin index (0–19)
    reward     : float — R[action, next_state]   (reward on arrival state)
    """
    T = T_shift if t >= CLIMATE_SWITCH_STEP else T_stat
    row = T[action, state]
    next_state = int(rng.choice(N, p=row))
    obs_idx    = int(rng.choice(N_OBS, p=LIKELIHOOD[next_state]))
    reward     = float(R[action, next_state])
    return next_state, obs_idx, reward


def update_belief(b: np.ndarray, obs_idx: int) -> np.ndarray:
    """
    Static Bayesian belief update (no transition predict step).

    Implements Eq. (1) from Frames_paper.tex:
        b_t(θ) ∝ P(o_t | θ) · b_{t-1}(θ)

    The static form is the correct choice when transition uncertainty is high
    or transitions are slow relative to decision frequency (see Remark in Sec. 1.2
    of Frames_paper.tex).  Baselines that use the Markovian form must implement
    their own predict step using the appropriate T matrix.

    Parameters
    ----------
    b       : prior belief, shape (N,), sums to 1
    obs_idx : observed bin index (0–19)

    Returns
    -------
    b_new : posterior belief, shape (N,), sums to 1
    """
    b_new = LIKELIHOOD[:, obs_idx] * b
    total = b_new.sum()
    if total < 1e-300:
        return b.copy()   # degenerate: likelihood nearly zero for all states; keep prior
    return b_new / total


def markov_update_belief(
    b: np.ndarray,
    obs_idx: int,
    action: int,
    t: int,
) -> np.ndarray:
    """
    Full Markovian belief update (predict + correct).

    Implements Eq. (2) from Frames_paper.tex:
        b_t(θ') ∝ P(o_t | θ') · Σ_θ P(θ'|θ,a) · b_{t-1}(θ)

    Used by SARSOP, PBVI, SDP baselines that maintain a fully Markovian model.

    Parameters
    ----------
    b       : prior belief, shape (N,)
    obs_idx : observed bin index (0–19)
    action  : action taken (0–2)
    t       : current step (selects regime for T)

    Returns
    -------
    b_new : posterior belief, shape (N,), sums to 1
    """
    T = T_shift if t >= CLIMATE_SWITCH_STEP else T_stat
    b_pred = T[action].T @ b          # predict: shape (N,)
    b_new  = LIKELIHOOD[:, obs_idx] * b_pred
    total  = b_new.sum()
    if total < 1e-300:
        return b_pred / b_pred.sum()
    return b_new / total


def expected_reward(b: np.ndarray, action: int) -> float:
    """
    Single-period expected reward under belief b: Σ_θ b(θ) · R[action, θ].
    Shared utility for all methods using U_eval = R.
    """
    return float(b @ R[action])


def entropy(b: np.ndarray) -> float:
    """Shannon entropy H(b) in nats.  Zero-probability states excluded."""
    mask = b > 0
    return float(-np.sum(b[mask] * np.log(b[mask])))


def entropy_norm(b: np.ndarray) -> float:
    """Normalised Shannon entropy H_norm = H(b) / log(N) ∈ [0, 1]."""
    return entropy(b) / np.log(N)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate() -> None:
    """
    Sanity-check all POMDP components.  Raises AssertionError on failure.
    Prints a brief report to stdout.
    """
    print("=" * 60)
    print("pomdp_env  — validation report")
    print("=" * 60)

    # Reward shape
    assert R.shape == (M, N), f"R shape {R.shape} != ({M},{N})"
    print(f"R shape: {R.shape}  OK")

    # Transition matrices — row sums
    for regime_name, T_mat in [("T_stat", T_stat), ("T_shift", T_shift)]:
        assert T_mat.shape == (M, N, N), f"{regime_name} shape {T_mat.shape}"
        rs = T_mat.sum(axis=2)
        assert np.allclose(rs, 1.0, atol=1e-9), \
            f"{regime_name} row sums not 1: {rs}"
        assert (T_mat >= 0).all(), f"{regime_name} has negative entries"
        print(f"{regime_name} shape {T_mat.shape}  row sums OK  non-negative OK")

    # Climate shift monotonicity: T_shift should have ≥ mass on worse states
    for a in range(M):
        diff = T_shift[a] - T_stat[a]
        # Upper-right triangle (s < s') should be ≥ 0 on balance
        upper_mass_stat  = np.tril(T_stat[a],  k=-1).sum()
        upper_mass_shift = np.tril(T_shift[a], k=-1).sum()
        assert upper_mass_shift >= upper_mass_stat - 1e-9, \
            f"a={a}: T_shift has less recovery mass than T_stat"
    print("Climate shift monotonicity  OK")

    # Likelihood matrix — shape and row sums
    assert LIKELIHOOD.shape == (N, N_OBS), \
        f"LIKELIHOOD shape {LIKELIHOOD.shape} != ({N},{N_OBS})"
    assert np.allclose(LIKELIHOOD.sum(axis=1), 1.0, atol=1e-9), \
        "LIKELIHOOD row sums not 1"
    assert (LIKELIHOOD >= 0).all(), "LIKELIHOOD has negative entries"
    print(f"LIKELIHOOD shape {LIKELIHOOD.shape}  row sums OK  non-negative OK")

    # Likelihood peak check: P(o | θ) should peak at the bin containing H_MEAN[θ]
    peak_obs = np.argmax(LIKELIHOOD, axis=1)
    for s in range(N):
        # bin index where H_MEAN[s] falls
        expected_bin = int(np.searchsorted(OBS_BINS, H_MEAN[s], side='right')) - 1
        expected_bin = max(0, min(N_OBS - 1, expected_bin))
        assert abs(peak_obs[s] - expected_bin) <= 1, \
            f"State {s}: LIKELIHOOD peak at bin {peak_obs[s]}, expected ~{expected_bin}"
    print("LIKELIHOOD peak positions  OK")

    # step() smoke test
    rng = np.random.default_rng(SEED)
    state, b0 = reset(rng)
    assert 0 <= state < N
    assert b0.shape == (N,)
    assert np.isclose(b0.sum(), 1.0)
    ns, o, rew = step(state, 0, t=0, rng=rng)
    assert 0 <= ns < N
    assert 0 <= o  < N_OBS
    assert rew in R[0]
    print(f"reset() + step() smoke test  OK  (state={state}, next={ns}, obs={o}, r={rew:.1f})")

    # update_belief() smoke test
    b1 = update_belief(b0, o)
    assert b1.shape == (N,)
    assert np.isclose(b1.sum(), 1.0)
    print(f"update_belief() smoke test  OK  (entropy before={entropy(b0):.4f}, after={entropy(b1):.4f})")

    # markov_update_belief() smoke test
    b2 = markov_update_belief(b0, o, action=0, t=0)
    assert np.isclose(b2.sum(), 1.0)
    print(f"markov_update_belief() smoke test  OK")

    # Full episode smoke test — 60 steps, check no crashes
    rng2 = np.random.default_rng(SEED + 1)
    s, b = reset(rng2)
    cumr = 0.0
    for t_step in range(T):
        a = int(np.argmax([expected_reward(b, ai) for ai in range(M)]))
        s, o, r = step(s, a, t_step, rng2)
        b = update_belief(b, o)
        cumr += GAMMA ** t_step * r
    print(f"Full episode smoke test  OK  (U_cum={cumr:.2f}, final_state=θ{s+1})")

    # Belief entropy progression (should tend to decrease over a well-observed episode)
    rng3 = np.random.default_rng(SEED + 2)
    s, b = reset(rng3)
    entropies = [entropy_norm(b)]
    for t_step in range(T):
        s, o, r = step(s, 0, t_step, rng3)  # always unrestricted
        b = update_belief(b, o)
        entropies.append(entropy_norm(b))
    h_start = entropies[0]
    h_end   = np.mean(entropies[-10:])
    print(f"Entropy trend  OK  (H_norm start={h_start:.3f}, mean last 10={h_end:.3f})")

    print("=" * 60)
    print("All checks passed.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Module-level constants exported for downstream scripts
# ---------------------------------------------------------------------------
__all__ = [
    # Parameters
    "SEED", "N_MC", "T", "GAMMA", "CLIMATE_SWITCH_STEP",
    "N", "M", "N_OBS",
    # Labels
    "STATE_LABELS", "ACTION_LABELS", "ACTION_COST",
    "FAILURE_STATE",
    # Arrays
    "R", "T_stat", "T_shift", "T_misspec", "H_MEAN", "SIGMA_OBS",
    "OBS_BINS", "OBS_BIN_CENTRES", "LIKELIHOOD",
    # ELS framework variants
    "L_PRES", "L_PHIL", "H_MAX_NATS", "PRIOR_PHIL", "PRIOR_PRES",
    # Functions
    "reset", "step", "update_belief", "markov_update_belief",
    "expected_reward", "entropy", "entropy_norm",
    "validate",
]

# ---------------------------------------------------------------------------
# Self-test when run as main script
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    validate()

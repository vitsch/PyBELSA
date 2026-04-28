# =============================================================================
# els_methods.py  —  ELS Framework Policies for Groundwater POMDP Benchmark
# Project  : ELS_NEW / P_Base  (Benchmark 8 — Karst Aquifer)
# Source   : Ported from P_Bernoulli/scr_update/frames_domain.py (v6)
# Paper    : P_Bernoulli/ref/Frames_Bernoulli_update.tex (v3)
# Plan ref : experiment_plan.md §5 Step 3
# Date     : 2026-04-25
# Usage    : from els_methods import ALL_ELS; policy = ALL_ELS["ELS_Int"]()
# =============================================================================
"""
Three ELS framework policies, each exposing:
    policy.reset()           — call at episode start (resets belief and state)
    policy.act(belief, t)    — return action int (0–2)

Policy inventory
----------------
ELSPhil   Philosophical (SR4): satisficing + info-gain, broad prior, option value O(a)
ELSPres   Prescriptive (SR5):  EU-max with cost penalty, concentrated prior, ν=0
ELSInt    Integrated Bernoulli (SR3.2): entropy-driven Bernoulli selector,
           k_t ~ Bern(1-α_t), P_hyb belief update, TEF amplification

Key adaptation from production code
-------------------------------------
frames_domain.py uses action-indexed likelihoods P_lik[a, o, θ] (diagonal
categorical matrices) and real groundwater data.  The synthetic POMDP benchmark
uses continuous Gaussian-bin likelihoods that are action-independent:

  L_PRES[θ, o]  — single Gaussian model (σ=4.0)  →  ELS-Pres and P_TRUE
  L_PHIL[θ, o]  — model-averaged (σ=3.5 + σ=5.5) →  ELS-Phil info-gain and belief update

For sr2_bayesian_update the indexing simplifies from P_lik[a, o, :] to
L[o, :] (observation row of the action-independent matrix).
All other formulae are faithful ports of the production SR1–SR5.

Hyperparameter defaults (from frames_domain.py docstring UK defaults):
    LAMBDA=1.0, NU=1.0, BETA=0.90, MU=0.8
    KAPPA_PRIME=0.2, ALPHA_MIN=0.05, ALPHA_MAX=0.95
    U_MIN=0.0, C_TEF=1.0

Notes
-----
- U_MIN is calibrated on the raw R scale (Frames_paper.tex Remark rem:binding).
  U_MIN=0.0 is safe since R[a₃,θ]=5 > 0 for all θ: action a₃ is always viable.
- ELSInt uses P_hyb computed from alpha_{t-1}, not alpha_t, matching production.
- All policies use GAMMA from pomdp_env for U_cum (computed externally in runner).
"""

import sys
import os
import numpy as np

# ---------------------------------------------------------------------------
# Import POMDP environment
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pomdp_env_b8 as env
from pomdp_env_b8 import (
    N, M, N_OBS, T, SEED,
    R, T_stat, LIKELIHOOD,
    L_PRES, L_PHIL,
    H_MAX_NATS, PRIOR_PHIL, PRIOR_PRES,
    ACTION_COST,
)

# ---------------------------------------------------------------------------
# ELS hyperparameters (UK-domain defaults from frames_domain.py)
# ---------------------------------------------------------------------------
LAMBDA      = 1.0    # option-value weight λ
NU          = 1.0    # information-gain weight ν
BETA        = 0.90   # satisficing probability threshold β
MU          = 0.8    # cost-aversion weight μ
KAPPA_PRIME = 0.2    # entropy temperature κ' = 1/κ
ALPHA_MIN   = 0.05   # minimum blending weight (philosophical regime)
ALPHA_MAX   = 0.95   # maximum blending weight (prescriptive regime)
U_MIN       = -800.0    # viability threshold on raw R scale (Req. 3)
C_TEF       = 1.0    # TEF coefficient: H_eff = H_norm*(1 + C_TEF*t/T)

# Priority 2 — Intervention A1: Hybrid Transition-Informed Belief Update
# w=0 → static ELS update (full T-distrust, original behaviour)
# w=1 → Markovian Bayes update (full T-trust, POMDP)
# w=0.5 → principled intermediate (recommended default)
W_TRANS     = 0.5    # model-trust weight for hybrid belief update


# ===========================================================================
# SR1  PreComputeOptionValues  (Eq. option_value)
# ===========================================================================

def _sr1_option_values(prior: np.ndarray, T_mat: np.ndarray) -> np.ndarray:
    """
    Compute option value O(a) for each action.

    O(a) = Σ_θ prior(θ) · Σ_θ' T_mat[a,θ,θ'] · (V*_R(θ') − R(ã*, θ'))

    where ã* = argmax_a' Σ_θ prior(θ)·R[a',θ]  and  V*_R(θ') = max_a R[a,θ'].

    Uses T_stat (stationary) as the known transition model; option values are
    computed once at episode start from PRIOR_PHIL (static mode).

    Returns
    -------
    O : ndarray shape (M,)
    """
    expected_R = R @ prior           # shape (M,)
    a_tilde    = int(np.argmax(expected_R))
    R_tilde    = R[a_tilde, :]       # shape (N,)
    V_R_star   = R.max(axis=0)       # shape (N,)

    O = np.zeros(M, dtype=float)
    for a in range(M):
        for theta in range(N):
            inner = float(T_mat[a, theta, :] @ (V_R_star - R_tilde))
            O[a] += prior[theta] * inner
    return O


# ===========================================================================
# SR2  BayesianUpdate  (static form, Eq. static_update)
# ===========================================================================

def _sr2_update(b: np.ndarray, obs: int, L: np.ndarray) -> np.ndarray:
    """
    b_new(θ) ∝ L[θ, obs] · b(θ)

    L : (N, N_OBS) action-independent likelihood matrix.
    Returns normalised posterior; falls back to prior if denominator < 1e-12.
    """
    num = L[:, obs] * b
    Z   = num.sum()
    if Z < 1e-12:
        return b.copy()
    return num / Z


# ===========================================================================
# SR2b  HybridUpdate  (Intervention A1, Eq. hybrid_update)
# ===========================================================================

def _sr2_hybrid(
    b: np.ndarray,
    obs: int,
    action: int,
    L: np.ndarray,
    T_mat: np.ndarray,
    w: float,
) -> np.ndarray:
    """
    Hybrid (predict-blend) belief update — Intervention A1.

    b_blend = (1−w)·b + w·(T_mat[action]ᵀ·b)     # convex blend of static and Markovian prior
    b_new  ∝ L[:, obs] · b_blend                   # ELS-style likelihood correction

    Parameters
    ----------
    b      : prior belief (N,)
    obs    : observation index
    action : action taken at this step (needed for T_mat[action])
    L      : (N, N_OBS) likelihood matrix
    T_mat  : (M, N, N) transition matrices (use T_stat for standard variant)
    w      : model-trust weight ∈ [0,1];  w=0 → static ELS;  w=1 → Markovian Bayes

    Returns
    -------
    Normalised posterior (N,).
    """
    if w < 1e-9:
        return _sr2_update(b, obs, L)             # fast path: exact static ELS

    b_pred  = T_mat[action].T @ b                 # Markovian prediction
    b_blend = (1.0 - w) * b + w * b_pred          # convex blend of priors
    num = L[:, obs] * b_blend
    Z   = num.sum()
    if Z < 1e-12:
        s = b_blend.sum()
        return b_blend / s if s > 1e-300 else b_blend.copy()
    return num / Z


# ===========================================================================
# SR3  ExpectedInfoGain  I(a;b) = H(b) − E_o[H(b_{a,o})]
# ===========================================================================

def _entropy_nats(b: np.ndarray) -> float:
    """Shannon entropy of b in nats; 0·log 0 := 0."""
    b_safe = np.where(b > 0, b, 1.0)
    return float(-np.sum(b * np.log(b_safe) * (b > 0)))


def _sr3_info_gain(b: np.ndarray, a: int, L: np.ndarray) -> float:
    """
    I(a; b) = H(b) − E_o[H(b_{t+1})]   (nats, clipped ≥ 0)

    L : (N, N_OBS) likelihood matrix used by the calling framework.
    The action index a is unused (action-independent likelihoods) but kept
    for API consistency with the production SR3 signature.
    """
    H_curr = _entropy_nats(b)
    H_exp  = 0.0
    for o in range(N_OBS):
        p_o = float(L[:, o] @ b)
        if p_o < 1e-10:
            continue
        b_next = L[:, o] * b
        b_next /= b_next.sum()
        H_exp  += p_o * _entropy_nats(b_next)
    return max(0.0, H_curr - H_exp)


# ===========================================================================
# SR4  PhilosophicalSelector  (Eqs. decision_phil–I_phil)
# ===========================================================================

def _sr4_phil(
    b: np.ndarray,
    U_phil: np.ndarray,
    L: np.ndarray,
    nu: float,
    u_min: float,
    beta: float,
) -> int:
    """
    Satisficing + info-gain decision rule.

    Pi_sat = {a : P(U_phil(a,θ) > u_min | b) > β}
    a* = argmax_{a ∈ Pi_sat} [EU_phil(a,b) + ν · I(a;b)]
    Fallback to full A if Pi_sat is empty.
    """
    pi_sat = [
        a for a in range(M)
        if float(np.sum(b[U_phil[a, :] > u_min])) > beta
    ]
    if not pi_sat:
        pi_sat = list(range(M))

    best, a_star = -np.inf, pi_sat[0]
    for a in pi_sat:
        score = float(b @ U_phil[a, :]) + nu * _sr3_info_gain(b, a, L)
        if score > best:
            best   = score
            a_star = a
    return a_star


# ===========================================================================
# SR5  PrescriptiveSelector  (Eq. decision_pres)
# ===========================================================================

def _sr5_pres(b: np.ndarray, U_pres: np.ndarray) -> int:
    """argmax_a EU_pres(a, b) — unconstrained EU-max."""
    return int(np.argmax(U_pres @ b))


# ===========================================================================
# alpha_t  computation  (Eq. alpha with H_eff TEF)
# ===========================================================================

def _alpha_t(b: np.ndarray, t: int) -> float:
    """
    Blending weight α_t driven by normalised entropy with TEF amplification.

      H_norm = H(b) / log(N)
      H_eff  = H_norm · (1 + C_TEF · t / T)      [Eq. H_eff]
      α_t    = α_min + (α_max − α_min) · 2 / (1 + exp(H_eff / κ'))

    High uncertainty → α_t → α_min (philosophical dominant).
    Low uncertainty  → α_t → α_max (prescriptive dominant).
    """
    H_norm = _entropy_nats(b) / H_MAX_NATS if H_MAX_NATS > 1e-12 else 0.0
    tef    = 1.0 + C_TEF * t / T if T > 0 else 1.0
    H_eff  = H_norm * tef
    return ALPHA_MIN + (ALPHA_MAX - ALPHA_MIN) * 2.0 / (1.0 + np.exp(H_eff / KAPPA_PRIME))


# ===========================================================================
# 1.  ELSPhil  —  Philosophical framework (Algorithm 1)
# ===========================================================================

class ELSPhil:
    """
    Philosophical framework (SR4).

    Prior  : PRIOR_PHIL (uniform — epistemic humility)
    Utility: U_phil = R + λ · O[:, newaxis]  (option value from SR1)
    Belief : static Bayesian update with L_PHIL (model-averaged)
    Action : satisficing + info-gain (SR4), ν > 0
    """
    NAME = "ELS_Phil"

    def __init__(self):
        O        = _sr1_option_values(PRIOR_PHIL, T_stat)
        self._U_phil = R + LAMBDA * O[:, np.newaxis]   # (M, N)

    def initial_belief(self) -> np.ndarray:
        """Starting belief: uniform PRIOR_PHIL."""
        return PRIOR_PHIL.copy()

    def reset(self) -> None:
        pass   # stateless — belief passed in at each step

    def act(self, belief: np.ndarray, t: int) -> int:
        return _sr4_phil(belief, self._U_phil, L_PHIL, NU, U_MIN, BETA)


# ===========================================================================
# 2.  ELSPres  —  Prescriptive framework (Algorithm 2)
# ===========================================================================

class ELSPres:
    """
    Prescriptive framework (SR5).

    Prior  : PRIOR_PRES (peaked around θ₁ — optimistic literature prior)
    Utility: U_pres = R − μ · C  (no option value, cost-penalised)
    Belief : static Bayesian update with L_PRES (single best model)
    Action : unconstrained EU-max (SR5), ν=0
    """
    NAME = "ELS_Pres"

    def __init__(self):
        self._U_pres = R - MU * ACTION_COST[:, np.newaxis]   # (M, N)

    def initial_belief(self) -> np.ndarray:
        """Starting belief: peaked PRIOR_PRES (optimistic literature prior)."""
        return PRIOR_PRES.copy()

    def reset(self) -> None:
        pass

    def act(self, belief: np.ndarray, t: int) -> int:
        return _sr5_pres(belief, self._U_pres)


# ===========================================================================
# 3.  ELSInt  —  Integrated Bernoulli framework (Algorithm 3 / SR3.2)
# ===========================================================================

class ELSInt:
    """
    Integrated framework with Bernoulli hard switching (SR3.2).

    Algorithm 3 (Frames_Bernoulli_update.tex v3):
      Step 1  P_hyb = (1-α_{t-1}) L_PHIL + α_{t-1} L_PRES
      Step 2  H_eff = H_norm · (1 + C_TEF · t/T);   α_t = f(H_eff)
      Step 3  a_phil ← SR4(b, U_phil, P_hyb)
              a_pres ← SR5(b, U_pres)
      Step 4  k_t ~ Bernoulli(1 − α_t):
                k_t="phil" → a* = a_phil
                k_t="pres" → a* = a_pres
      Step 8  belief update with P_hyb (regardless of k_t)
      Step 9  α_{t-1} ← α_t  (carried forward)

    Stochastic draws use an episode-local RNG seeded from SEED so results
    are reproducible across act() calls within an episode.  The runner must
    call reset() before each new episode to re-seed.

    Attributes
    ----------
    last_k_t : str   — "phil" or "pres" — selector used at the last step
    alpha_trajectory : list[float] — α_t values for the episode (for reporting)
    """
    NAME = "ELS_Int"

    def __init__(self, seed: int = SEED, c_tef: float = C_TEF):
        O = _sr1_option_values(PRIOR_PHIL, T_stat)
        self._U_phil  = R + LAMBDA * O[:, np.newaxis]
        self._U_pres  = R - MU * ACTION_COST[:, np.newaxis]
        self._seed    = seed
        self._c_tef   = c_tef
        self.last_k_t: str = "phil"
        self.alpha_trajectory: list[float] = []
        self._alpha_prev  = ALPHA_MIN   # α_{t-1} for P_hyb
        self._ep_rng: np.random.Generator = np.random.default_rng(seed)

    def initial_belief(self) -> np.ndarray:
        """Starting belief: PRIOR_PHIL (uniform — matches production Alg3 line `b = PRIOR_PHIL`)."""
        return PRIOR_PHIL.copy()

    def reset(self, seed: int | None = None) -> None:
        """Re-seed episode RNG and clear trajectory."""
        self._alpha_prev     = ALPHA_MIN
        self.last_k_t        = "phil"
        self.alpha_trajectory = []
        self._ep_rng = np.random.default_rng(
            seed if seed is not None else self._seed
        )

    def act(self, belief: np.ndarray, t: int) -> int:
        """
        Return action selected by Bernoulli hard switching.

        Does NOT advance the belief — the runner calls update_belief()
        after observing the outcome and passes the updated belief to the
        next act() call.
        """
        # Step 1: P_hyb uses α from previous step
        P_hyb = (1.0 - self._alpha_prev) * L_PHIL + self._alpha_prev * L_PRES

        # Step 2: α_t from current belief entropy + TEF
        H_norm = _entropy_nats(belief) / H_MAX_NATS if H_MAX_NATS > 1e-12 else 0.0
        tef    = 1.0 + self._c_tef * t / T if T > 0 else 1.0
        H_eff  = H_norm * tef
        alpha_t = ALPHA_MIN + (ALPHA_MAX - ALPHA_MIN) * 2.0 / (
            1.0 + np.exp(H_eff / KAPPA_PRIME)
        )
        self.alpha_trajectory.append(alpha_t)

        # Step 3: candidate actions from both selectors
        a_phil = _sr4_phil(belief, self._U_phil, P_hyb, NU, U_MIN, BETA)
        a_pres = _sr5_pres(belief, self._U_pres)

        # Step 4: Bernoulli draw — k_t ~ Bernoulli(1 - α_t)
        k_t    = "phil" if self._ep_rng.random() < (1.0 - alpha_t) else "pres"
        a_star = a_phil if k_t == "phil" else a_pres
        self.last_k_t = k_t

        # Step 9: carry α_t forward as α_{t-1} for next call
        self._alpha_prev = alpha_t

        return a_star

    def phys_belief_update(
        self, b: np.ndarray, obs: int, action: int | None = None
    ) -> np.ndarray:
        """
        Hybrid belief update (Step 8): always uses P_hyb = (1-α_prev) L_PHIL + α_prev L_PRES.
        Call this instead of env.update_belief() when running ELSInt episodes.

        The optional `action` parameter is unused in the base ELSInt (w=0 static update)
        but accepted for API compatibility with ELSIntT.
        """
        P_hyb = (1.0 - self._alpha_prev) * L_PHIL + self._alpha_prev * L_PRES
        return _sr2_update(b, obs, P_hyb)

    @property
    def pct_phil(self) -> float:
        """Fraction of steps where philosophical selector was chosen (0–1)."""
        if not self.alpha_trajectory:
            return float("nan")
        return sum(1 for k in [self.last_k_t]) / max(1, len(self.alpha_trajectory))


# ===========================================================================
# 4.  ELSPhilT  —  Philosophical + Hybrid Belief Update (Intervention A1)
# ===========================================================================

class ELSPhilT(ELSPhil):
    """
    Philosophical framework with hybrid (predict-blend) belief update.

    Intervention A1 from how_improve_performance.md §2.2:
        b_blend = (1−w)·b + w·(T_stat[action]ᵀ·b)
        b_new  ∝ L_PHIL[:, obs] · b_blend

    Inherits SR4 action selection from ELSPhil; only the belief update changes.

    Parameters
    ----------
    w : float, default W_TRANS=0.5
        Model-trust weight.  w=0 → ELSPhil (static);  w=1 → Markovian Bayes.

    Belief update needs the executed action → call phys_belief_update(b, obs, action).
    """
    NAME = "ELS_Phil_T"

    def __init__(self, w: float = W_TRANS):
        super().__init__()
        self._w = float(w)

    def phys_belief_update(
        self, b: np.ndarray, obs: int, action: int | None = None
    ) -> np.ndarray:
        """Hybrid update with L_PHIL and T_stat; action is required for w > 0."""
        if action is None or self._w < 1e-9:
            return _sr2_update(b, obs, L_PHIL)
        return _sr2_hybrid(b, obs, action, L_PHIL, T_stat, self._w)


# ===========================================================================
# 5.  ELSIntT  —  Integrated Bernoulli + Hybrid Belief Update (Intervention A1)
# ===========================================================================

class ELSIntT(ELSInt):
    """
    Integrated Bernoulli framework with hybrid (predict-blend) belief update.

    Combines ELSInt's Bernoulli hard-switching action selection with the
    Intervention A1 belief update:
        b_blend = (1−w)·b + w·(T_stat[action]ᵀ·b)
        b_new  ∝ P_hyb[:, obs] · b_blend

    The P_hyb likelihood blend is preserved (α-weighted L_PHIL/L_PRES);
    the new w parameter adds partial Markovian prediction to the prior.

    Parameters
    ----------
    w : float, default W_TRANS=0.5
        Model-trust weight.  w=0 → ELSInt (static);  w=1 → Markovian Bayes.
    """
    NAME = "ELS_Int_T"

    def __init__(
        self,
        seed: int = SEED,
        c_tef: float = C_TEF,
        w: float = W_TRANS,
    ):
        super().__init__(seed=seed, c_tef=c_tef)
        self._w = float(w)

    def phys_belief_update(
        self, b: np.ndarray, obs: int, action: int | None = None
    ) -> np.ndarray:
        """
        Hybrid update (Step 8): P_hyb likelihood on blended prior.

        Uses α_prev (carried forward from act()) for P_hyb; action is required
        for the Markovian predict step when w > 0.
        """
        P_hyb = (1.0 - self._alpha_prev) * L_PHIL + self._alpha_prev * L_PRES
        if action is None or self._w < 1e-9:
            return _sr2_update(b, obs, P_hyb)
        return _sr2_hybrid(b, obs, action, P_hyb, T_stat, self._w)


# ===========================================================================
# Shared belief-update helpers for runners
# ===========================================================================

def els_phil_update(b: np.ndarray, obs: int) -> np.ndarray:
    """Belief update for ELSPhil: static update with L_PHIL."""
    return _sr2_update(b, obs, L_PHIL)


def els_pres_update(b: np.ndarray, obs: int) -> np.ndarray:
    """Belief update for ELSPres: static update with L_PRES."""
    return _sr2_update(b, obs, L_PRES)


# ---------------------------------------------------------------------------
# update_belief dispatch table — used by run_benchmark.py
# ELS_Phil / ELS_Pres use module-level static functions (action-independent).
# ELS_Int / ELS_Phil_T / ELS_Int_T use policy.phys_belief_update(b, obs, action).
# ---------------------------------------------------------------------------
ELS_BELIEF_UPDATE = {
    "ELS_Phil": els_phil_update,
    "ELS_Pres": els_pres_update,
    # ELS_Int, ELS_Phil_T, ELS_Int_T use their own phys_belief_update() methods
}

# Methods that require phys_belief_update(b, obs, action)
ELS_PHYS_UPDATE_METHODS = {"ELS_Int", "ELS_Phil_T", "ELS_Int_T"}


# ===========================================================================
# Registry
# ===========================================================================

ALL_ELS: dict[str, type] = {
    "ELS_Phil":   ELSPhil,
    "ELS_Pres":   ELSPres,
    "ELS_Int":    ELSInt,
    "ELS_Phil_T": ELSPhilT,
    "ELS_Int_T":  ELSIntT,
}


# ===========================================================================
# Validation
# ===========================================================================

def validate(verbose: bool = True) -> None:
    """
    Smoke-test each ELS policy through one complete episode.
    Checks: valid actions, belief evolution, alpha trajectory, k_t labels.
    """
    import pomdp_env_b8 as env_mod

    rng_val = np.random.default_rng(SEED + 300)
    state, _b0_unused = env_mod.reset(rng_val)

    for name, cls in ALL_ELS.items():
        policy = cls()
        policy.reset()

        is_int = isinstance(policy, ELSInt)

        b = policy.initial_belief()   # each framework uses its own prior
        s = state
        cum_r = 0.0
        rng_ep = np.random.default_rng(SEED + 400)
        kt_counts = {"phil": 0, "pres": 0}

        for t_step in range(env_mod.T):
            a = policy.act(b, t_step)
            assert 0 <= a < M, f"{name}: invalid action {a}"

            s, o, r = env_mod.step(s, a, t_step, rng_ep)

            if is_int:
                b = policy.phys_belief_update(b, o)
                kt_counts[policy.last_k_t] += 1
            elif name == "ELS_Phil":
                b = els_phil_update(b, o)
            else:
                b = els_pres_update(b, o)

            assert np.isclose(b.sum(), 1.0), f"{name}: belief not normalised at t={t_step}"
            cum_r += env_mod.GAMMA ** t_step * r

        if verbose:
            if is_int:
                alphas = policy.alpha_trajectory
                pct = 100 * kt_counts["phil"] / env_mod.T
                print(
                    f"{name:<12}  OK  U_cum={cum_r:8.2f}  "
                    f"α_mean={np.mean(alphas):.3f}  "
                    f"α_range=[{min(alphas):.3f},{max(alphas):.3f}]  "
                    f"f_phil={pct:.1f}%  final_state=θ{s+1}"
                )
            else:
                print(f"{name:<12}  OK  U_cum={cum_r:8.2f}  final_state=θ{s+1}")

    # Additional checks for ELSInt
    policy_int = ELSInt(seed=SEED)
    policy_int.reset(seed=SEED + 1)
    rng2 = np.random.default_rng(SEED + 500)
    s2, _ = env_mod.reset(rng2)
    b2 = policy_int.initial_belief()
    n_phil_1 = 0

    for t_step in range(env_mod.T):
        a = policy_int.act(b2, t_step)
        s2, o, _ = env_mod.step(s2, a, t_step, rng2)
        b2 = policy_int.phys_belief_update(b2, o)
        if policy_int.last_k_t == "phil":
            n_phil_1 += 1

    pct_1 = 100 * n_phil_1 / env_mod.T
    assert 0 <= pct_1 <= 100
    if verbose:
        print(f"ELSInt k_t distribution  OK  (f_phil={pct_1:.1f}% in seed+1 episode)")

    # SR1 option value range check
    O_vals = _sr1_option_values(PRIOR_PHIL, T_stat)
    if verbose:
        print(f"SR1 O(a) = {O_vals}  range={np.ptp(O_vals):.4f}")
    # For synthetic POMDP with action-dependent T, O should have some variation
    assert O_vals.min() >= 0.0, "Option values must be non-negative"

    # alpha_t limits check at known entropy extremes
    b_max_H = PRIOR_PHIL.copy()
    b_min_H = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    a_max_H = _alpha_t(b_max_H, t=0)
    a_min_H = _alpha_t(b_min_H, t=env_mod.T - 1)
    assert a_max_H < 0.5, f"At max entropy α_t should be near α_min; got {a_max_H:.3f}"
    assert a_min_H > 0.5, f"At zero entropy α_t should be near α_max; got {a_min_H:.3f}"
    if verbose:
        print(f"α_t limits  OK  (max-H: {a_max_H:.3f} ≈ α_min={ALPHA_MIN},  "
              f"zero-H: {a_min_H:.3f} ≈ α_max={ALPHA_MAX})")

    if verbose:
        print("All ELS smoke tests passed.")


if __name__ == "__main__":
    validate(verbose=True)

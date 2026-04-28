# =============================================================================
# els_adapt_b5.py  —  ELS Adaptive Model-Trust Variants (Benchmark 5 — NCP)
# Project  : ELS_NEW / P_Base5  (North China Plain GRACE-Based)
# Plan ref : BDT_concept_impr.md §3.1; P_Base/docs/summary_w_update_B4.md
# Ported   : from P_Base4/scr/els_adapt_b4.py — only imports changed for B5
# Date     : 2026-04-25
# Usage    : from els_adapt_b5 import ELSPhilAdapt, ELSIntAdapt
# =============================================================================
"""
ELS_Phil_Adapt and ELS_Int_Adapt for Benchmark 5 (North China Plain GRACE).

Adaptive model-trust weight w: after each observation, w is updated in
logit space based on log-likelihood ratio (T_B5_STAT-propagated vs static):

    ll_T  = log P(obs | T_stat[a]ᵀ · b)    [T_B5_STAT prediction]
    ll_s  = log P(obs | b)                   [static prior]
    δ     = η · (ll_T − ll_s)
    logit(w_new) = logit(w) + δ
    w_new  = clip(sigmoid(logit(w_new)), w_min, w_max)

Key B5 differences vs B4:
  - Domain: NCP provincial quota + crop management (GRACE observations)
  - T = 30 steps (CLIMATE_SWITCH_STEP = 15)
  - N_OBS = 20 bins (H_MEAN: TWSA mm WE proxy; σ_obs = 45 mm WE — widest in suite)
  - T_stat = T_B5_STAT (long-term average NCP dynamics; bidirectional)
  - T_shift = T_B5_SHIFT (delta=0.18/0.14/0.08 — SSP5-8.5 irrigation demand)
  - U_MIN = -600.0 in els_methods.py (R[a₁,θ₅] = -500 dominates)
  - U_T ≈ 0.7–0.9 (highest in suite — GRACE noise + sparse wells)
  - SIGMA_OBS = 45 (wider than B4=35, GRACE footprint aggregation)

Inheritance chain (B5):
  ELSPhilAdapt  ←  ELSPhilT  ←  ELSPhil   (all from P_Base5/scr/els_methods.py)
  ELSIntAdapt   ←  ELSIntT   ←  ELSInt

All parent classes already import from pomdp_env_b5 — no additional changes needed.
"""

import os
import sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from els_methods import (
    ELSPhilT, ELSIntT, ELSInt,
    W_TRANS, SEED, C_TEF,
)
from pomdp_env_b5 import T_stat, L_PHIL, L_PRES


# ===========================================================================
# 1.  ELSPhilAdapt  —  Philosophical + Online-Adaptive w  (B5)
# ===========================================================================

class ELSPhilAdapt(ELSPhilT):
    """
    Philosophical framework (B5 NCP GRACE) with adaptive model-trust weight.

    Uses T_B5_STAT as the reference model. L_PHIL is model-averaged likelihood
    (σ=35 GRACE gridded + σ=60 basin-scale — widest in suite).

    Parameters
    ----------
    w_init : float, default W_TRANS=0.5
    eta    : float, default 0.5
    w_min  : float, default 0.0
    w_max  : float, default 1.0

    Attributes
    ----------
    w_trajectory : list[float]
    """

    NAME = "ELS_Phil_Adapt"

    def __init__(self, w_init=W_TRANS, eta=0.5, w_min=0.0, w_max=1.0):
        super().__init__(w=w_init)
        self._w_init = float(w_init)
        self._eta    = float(eta)
        self._w_min  = float(w_min)
        self._w_max  = float(w_max)
        self.w_trajectory: list[float] = []

    def reset(self) -> None:
        super().reset()
        self._w = self._w_init
        self.w_trajectory = []

    def phys_belief_update(self, b, obs, action=None):
        b_new = super().phys_belief_update(b, obs, action)
        if action is not None and self._eta > 1e-12:
            b_pred  = T_stat[action].T @ b
            ll_T    = float(np.log(max(float(L_PHIL[:, obs] @ b_pred), 1e-300)))
            ll_s    = float(np.log(max(float(L_PHIL[:, obs] @ b),      1e-300)))
            delta   = self._eta * (ll_T - ll_s)
            w_safe  = float(np.clip(self._w, 1e-6, 1.0 - 1e-6))
            logit_w = np.log(w_safe / (1.0 - w_safe)) + delta
            self._w = float(np.clip(
                1.0 / (1.0 + np.exp(-logit_w)),
                self._w_min, self._w_max,
            ))
        self.w_trajectory.append(self._w)
        return b_new


# ===========================================================================
# 2.  ELSIntAdapt  —  Integrated Bernoulli + Online-Adaptive w  (B5)
# ===========================================================================

class ELSIntAdapt(ELSIntT):
    """
    Integrated Bernoulli framework (B5 NCP GRACE) with adaptive model-trust weight.

    P_hyb = (1−α_prev)·L_PHIL + α_prev·L_PRES used for both belief update
    and T-accuracy measurement (self-consistent with Bernoulli mixing).

    Parameters
    ----------
    seed, c_tef, w_init, eta, w_min, w_max — see ELSPhilAdapt

    Attributes
    ----------
    w_trajectory : list[float]
    """

    NAME = "ELS_Int_Adapt"

    def __init__(self, seed=SEED, c_tef=C_TEF, w_init=W_TRANS,
                 eta=0.5, w_min=0.0, w_max=1.0):
        super().__init__(seed=seed, c_tef=c_tef, w=w_init)
        self._w_init = float(w_init)
        self._eta    = float(eta)
        self._w_min  = float(w_min)
        self._w_max  = float(w_max)
        self.w_trajectory: list[float] = []

    def reset(self, seed=None):
        super().reset(seed=seed)
        self._w = self._w_init
        self.w_trajectory = []

    def phys_belief_update(self, b, obs, action=None):
        b_new = super().phys_belief_update(b, obs, action)
        if action is not None and self._eta > 1e-12:
            P_hyb   = (1.0 - self._alpha_prev) * L_PHIL + self._alpha_prev * L_PRES
            b_pred  = T_stat[action].T @ b
            ll_T    = float(np.log(max(float(P_hyb[:, obs] @ b_pred), 1e-300)))
            ll_s    = float(np.log(max(float(P_hyb[:, obs] @ b),      1e-300)))
            delta   = self._eta * (ll_T - ll_s)
            w_safe  = float(np.clip(self._w, 1e-6, 1.0 - 1e-6))
            logit_w = np.log(w_safe / (1.0 - w_safe)) + delta
            self._w = float(np.clip(
                1.0 / (1.0 + np.exp(-logit_w)),
                self._w_min, self._w_max,
            ))
        self.w_trajectory.append(self._w)
        return b_new


# ===========================================================================
# Registry supplement
# ===========================================================================

ELS_ADAPT_METHODS   = {"ELS_Phil_Adapt": ELSPhilAdapt, "ELS_Int_Adapt": ELSIntAdapt}
ELS_ADAPT_PHYS_UPDATE = {"ELS_Phil_Adapt", "ELS_Int_Adapt"}


# ===========================================================================
# Validation
# ===========================================================================

def validate(verbose: bool = True) -> None:
    import pomdp_env_b5 as env_mod
    from pomdp_env_b5 import N, M, T as T_B5, SEED as _SEED

    rng_val = np.random.default_rng(_SEED + 700)
    state   = int(rng_val.integers(0, N))

    tests = [
        ("ELS_Phil_Adapt", ELSPhilAdapt(w_init=0.5, eta=0.5), None),
        ("ELS_Int_Adapt",  ELSIntAdapt(seed=_SEED + 1, w_init=0.5, eta=0.5), _SEED + 1),
    ]

    for name, policy, ep_seed in tests:
        if isinstance(policy, ELSInt):
            policy.reset(seed=ep_seed)
        else:
            policy.reset()

        b      = policy.initial_belief()
        s      = state
        cum_r  = 0.0
        rng_ep = np.random.default_rng(_SEED + 800)

        for t_step in range(T_B5):
            a = policy.act(b, t_step)
            assert 0 <= a < M, f"{name}: invalid action {a}"
            s_next, obs, r = env_mod.step(s, a, t_step, rng_ep)
            b = policy.phys_belief_update(b, obs, action=a)
            assert np.isclose(b.sum(), 1.0, atol=1e-6), \
                f"{name}: belief not normalised at t={t_step}"
            cum_r += env_mod.GAMMA ** t_step * r
            s = s_next

        assert len(policy.w_trajectory) == T_B5
        w_arr = np.array(policy.w_trajectory)
        if verbose:
            print(
                f"{name:<18}  OK  U_cum={cum_r:8.2f}  "
                f"w_mean={w_arr.mean():.3f}  "
                f"w_range=[{w_arr.min():.3f}, {w_arr.max():.3f}]  "
                f"final_state=θ{s+1}"
            )

    if verbose:
        print("ELS-Adapt B5 smoke tests passed.")


if __name__ == "__main__":
    validate(verbose=True)

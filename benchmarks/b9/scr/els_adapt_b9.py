# =============================================================================
# els_adapt_b9.py  —  ELS Adaptive Model-Trust Variants (Benchmark 9 — HKH)
# Project  : ELS_NEW / P_Base9  (Glacial Meltwater Recharge: Indus Basin / HKH)
# Plan ref : BDT_concept_impr.md §3.1; P_Base/docs/experiment_plan2.md §12.4
# Ported   : from P_Base8/scr/els_adapt_b8.py — only imports changed for B9
# Date     : 2026-04-25
# Usage    : from els_adapt_b9 import ELSPhilAdapt, ELSIntAdapt
# =============================================================================
"""
ELS_Phil_Adapt and ELS_Int_Adapt for Benchmark 9 (Indus Basin / HKH).

Adaptive model-trust weight w: after each observation, w is updated in
logit space based on log-likelihood ratio (T_B9_STAT-propagated vs static):

    ll_T  = log P(obs | T_stat[a]ᵀ · b)    [T_B9_STAT prediction]
    ll_s  = log P(obs | b)                   [static prior]
    δ     = η · (ll_T − ll_s)
    logit(w_new) = logit(w) + δ
    w_new  = clip(sigmoid(logit(w_new)), w_min, w_max)

Key B9 novelty — within-episode w trajectory:
  Unlike B1–B8 where T uncertainty is fixed or step-switching, B9's T_true(t)
  continuously diverges from T_stat as t increases.  The adaptive w update
  uses T_stat as reference throughout (consistent across all benchmarks).
  This produces a natural within-episode w arc:
    - Early steps (t≈0–8): T_stat ≈ T(0) = T_true → ll_T > ll_s → w rises
    - Mid steps (t≈9–18): T_stat starts diverging → mixed signal → w plateaus
    - Late steps (t≈19–29): T_stat ≠ T_true → ll_T < ll_s → w declines
  Net result: bell-shaped w trajectory, w_mean < w_peak ≈ 0.65–0.75 (η=0.5)
  This self-correcting behaviour is the B9 showcase for adaptive w.

Key B9 differences vs B8:
  - Domain: Indus Basin alluvial aquifer, HKH glacial meltwater recharge
  - T = 30 steps (no CLIMATE_SWITCH_STEP — continuous drift)
  - N_OBS = 20 bins (Gaussian TWSA likelihood; OBS_BINS in mm WE space)
  - T_stat = T_B9_STAT (current HKH recharge era, ~2020–2030)
  - T_shift = T_B9_SHIFT (diminished recharge, ~2085–2100)
  - T_true(t) = (1-α)·T_stat + α·T_shift; α=t/(T-1)
  - U_MIN = -700.0 (Indus crop failure + food crisis)
  - SIGMA_OBS = 48 mm WE (GRACE-FO + HKH terrain correction)
  - L_PHIL = avg(σ_GRACE=38, σ_WAPDA=62)

Expected adaptive behaviour at B9:
  - η=0.1: w_mean ≈ 0.52–0.58 (slow to respond; bell flattened)
  - η=0.5: w_mean ≈ 0.58–0.65 (moderate bell; self-corrects late-episode)
  - η=1.0: w_mean ≈ 0.60–0.70 (sharper bell; earlier peak and decline)
  - B9 w_mean lower than B8 (0.86) — T_stat less reliable under continuous drift

Inheritance chain (B9):
  ELSPhilAdapt  ←  ELSPhilT  ←  ELSPhil   (all from P_Base9/scr/els_methods.py)
  ELSIntAdapt   ←  ELSIntT   ←  ELSInt

All parent classes import from pomdp_env_b9 — no additional changes needed.
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
from pomdp_env_b9 import T_stat, L_PHIL, L_PRES


# ===========================================================================
# 1.  ELSPhilAdapt  —  Philosophical + Online-Adaptive w  (B9)
# ===========================================================================

class ELSPhilAdapt(ELSPhilT):
    """
    Philosophical framework (B9 Indus/HKH) with adaptive model-trust weight.

    Uses T_B9_STAT as the reference model (consistent across all benchmarks).
    The within-episode w trajectory is bell-shaped under continuous drift:
    rises early (T_stat accurate), peaks ~t=8-12, declines late (T_stat diverges).

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
# 2.  ELSIntAdapt  —  Integrated Bernoulli + Online-Adaptive w  (B9)
# ===========================================================================

class ELSIntAdapt(ELSIntT):
    """
    Integrated Bernoulli framework (B9 Indus/HKH) with adaptive model-trust weight.

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

ELS_ADAPT_METHODS    = {"ELS_Phil_Adapt": ELSPhilAdapt, "ELS_Int_Adapt": ELSIntAdapt}
ELS_ADAPT_PHYS_UPDATE = {"ELS_Phil_Adapt", "ELS_Int_Adapt"}


# ===========================================================================
# Validation
# ===========================================================================

def validate(verbose: bool = True) -> None:
    import pomdp_env_b9 as env_mod
    from pomdp_env_b9 import N, M, T as T_B9, SEED as _SEED

    rng_val = np.random.default_rng(_SEED + 900)
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
        rng_ep = np.random.default_rng(_SEED + 1000)

        for t_step in range(T_B9):
            a = policy.act(b, t_step)
            assert 0 <= a < M, f"{name}: invalid action {a}"
            s_next, obs, r = env_mod.step(s, a, t_step, rng_ep)
            b = policy.phys_belief_update(b, obs, action=a)
            assert np.isclose(b.sum(), 1.0, atol=1e-6), \
                f"{name}: belief not normalised at t={t_step}"
            cum_r += env_mod.GAMMA ** t_step * r
            s = s_next

        assert len(policy.w_trajectory) == T_B9
        w_arr = np.array(policy.w_trajectory)
        if verbose:
            print(
                f"{name:<18}  OK  U_cum={cum_r:8.2f}  "
                f"w_mean={w_arr.mean():.3f}  "
                f"w_range=[{w_arr.min():.3f}, {w_arr.max():.3f}]  "
                f"final_state=θ{s+1}"
            )

    if verbose:
        print("ELS-Adapt B9 smoke tests passed.")


if __name__ == "__main__":
    validate(verbose=True)
